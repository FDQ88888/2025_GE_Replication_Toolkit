"""Run tax-emissions and quota-price correspondence sweeps."""

from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from duanmu_ge_lab import (
    CandidateFeatureBlocks,
    EmissionTaxEquilibriumDiagnostics,
    PaperExample3TaxSolver,
    QuotaEquilibriumDiagnostics,
    build_paper_example_3_tax_economy,
    build_quota_candidate,
    cluster_verified_candidates,
    map_emission_tax_to_global_quota,
    paper_example_3_good_1_excess,
    paper_example_3_reduction_percent,
    solve_multistart,
)
from duanmu_ge_lab.experiment_io import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def validate_cluster_counts(
    actual_tax_counts, expected_tax_counts, actual_quota_counts, expected_quota_counts
):
    """Return exact sweep-target validation without inferring root completeness."""

    return bool(
        list(actual_tax_counts) == list(expected_tax_counts)
        and list(actual_quota_counts) == list(expected_quota_counts)
    )


def run(config_path: Path | None = None):
    path = config_path or ROOT / "configs" / "experiments" / "tax_quota_sweeps.yaml"
    config = load_yaml_mapping(path)
    tolerance = float(config["solver"]["tolerance"])
    residual_acceptance_tolerance = float(
        config["solver"]["residual_acceptance_tolerance"]
    )
    max_nfev = int(config["solver"]["max_nfev"])
    threshold = float(config["clustering"]["distance_threshold"])
    seed = int(config["experiment"]["random_seed"])
    example_solver = PaperExample3TaxSolver()

    tax_rows = []
    previous_tax_etas: list[list[float]] = []
    for tax_index, tau_value in enumerate(config["tax_sweep"]["table_goods_sum_tax_rates"]):
        tau = float(tau_value)
        economy = build_paper_example_3_tax_economy(tau)
        diagnostics = EmissionTaxEquilibriumDiagnostics(economy)

        def solve_eta(initial, current_tau=tau):
            result = least_squares(
                lambda point: np.array(
                    [paper_example_3_good_1_excess(current_tau, float(point[0]))]
                ),
                initial,
                bounds=(np.array([0.2]), np.array([3.0])),
                xtol=tolerance,
                ftol=tolerance,
                gtol=tolerance,
                max_nfev=max_nfev,
            )
            eta = float(result.x[0])
            root = example_solver.build_root(current_tau, eta)
            residual = abs(root.scalar_residual)
            root.candidate.solver_success = bool(
                result.success and residual <= residual_acceptance_tolerance
            )
            root.candidate.solver_message = str(result.message)
            root.candidate.solver_method = "least_squares:tax_sweep_eta"
            root.candidate.function_calls = int(result.nfev)
            root.candidate.metadata.update(
                {"terminal_eta": eta, "terminal_scalar_residual": residual}
            )
            return root.candidate

        tax_config = config["tax_sweep"]
        runs = solve_multistart(
            solve_eta,
            diagnostics.evaluate,
            deterministic_starts=[
                [float(value)] for value in tax_config["deterministic_eta_starts"]
            ],
            random_bounds=(
                [float(tax_config["random_eta_bounds"][0])],
                [float(tax_config["random_eta_bounds"][1])],
            ),
            random_count=int(tax_config["random_count"]),
            continuation_starts=previous_tax_etas,
            random_seed=seed + tax_index,
        )
        clusters = cluster_verified_candidates(
            runs,
            lambda candidate: CandidateFeatureBlocks.from_candidate(
                candidate,
                [candidate.total_net_emissions[0], candidate.tax_revenue],
            ),
            distance_threshold=threshold,
        )
        equilibria = []
        previous_tax_etas = []
        for equilibrium_id, cluster in enumerate(clusters):
            run_record = runs[cluster.representative_run_id]
            candidate = run_record.candidate
            eta = float(candidate.metadata["terminal_eta"])
            previous_tax_etas.append([eta])
            utilities = {
                consumer.id: consumer.utility(candidate.allocations[index])
                for index, consumer in enumerate(economy.consumers)
            }
            equilibria.append(
                {
                    "equilibrium_id": equilibrium_id,
                    "eta_p1_over_p2": eta,
                    "prices": candidate.prices.tolist(),
                    "emissions": float(candidate.total_net_emissions[0]),
                    "reduction_percent": paper_example_3_reduction_percent(tau, eta),
                    "production": candidate.firm_plans.tolist(),
                    "allocations": candidate.allocations.tolist(),
                    "utilities": utilities,
                    "profits": dict(candidate.firm_profits),
                    "tax_revenue": candidate.tax_revenue,
                    "residuals": run_record.diagnostics.errors,
                    "classification": run_record.classification,
                    "cluster": cluster.to_dict(),
                }
            )
        tax_rows.append(
            {
                "table_goods_sum_tax_rate": tau,
                "core_signed_l1_tax_rate": tau / (1.0 + tau),
                "paper_theoretical_status": (
                    "NO_EQUILIBRIUM" if tau >= 0.03800995 else "EQUILIBRIUM_EXISTS"
                ),
                "numerical_search_status": (
                    f"DISCOVERED_{len(clusters)}_VERIFIED_CANDIDATE_CLUSTERS"
                ),
                "run_summary": {
                    "total": len(runs),
                    "verified": sum(
                        run.classification == "VERIFIED_CANDIDATE" for run in runs
                    ),
                },
                "equilibria": equilibria,
            }
        )

    quota_rows = []
    previous_quota_starts: list[list[float]] = []
    quota_config = config["quota_sweep"]
    for target_index, target_value in enumerate(quota_config["reduction_targets"]):
        target = float(target_value)

        def solve_target(initial):
            def equations(point):
                eta, tau = (float(value) for value in point)
                return np.array(
                    [
                        paper_example_3_good_1_excess(tau, eta),
                        paper_example_3_reduction_percent(tau, eta) / 100.0
                        - target,
                    ]
                )

            result = least_squares(
                equations,
                initial,
                bounds=(np.array([0.1, 0.0]), np.array([4.0, 0.04])),
                xtol=tolerance,
                ftol=tolerance,
                gtol=tolerance,
                max_nfev=max_nfev,
            )
            eta, tau = (float(value) for value in result.x)
            root = example_solver.build_root(tau, eta)
            residual = float(np.max(np.abs(equations(result.x))))
            root.candidate.solver_success = bool(
                result.success and residual <= residual_acceptance_tolerance
            )
            root.candidate.solver_message = str(result.message)
            root.candidate.solver_method = "least_squares:quota_target_eta_tau"
            root.candidate.function_calls = int(result.nfev)
            root.candidate.metadata.update(
                {
                    "terminal_eta": eta,
                    "terminal_table_tax_rate": tau,
                    "terminal_system_residual": residual,
                }
            )
            return root.candidate

        def diagnose_dynamic(candidate):
            tau = float(candidate.metadata["terminal_table_tax_rate"])
            return EmissionTaxEquilibriumDiagnostics(
                build_paper_example_3_tax_economy(tau)
            ).evaluate(candidate)

        runs = solve_multistart(
            solve_target,
            diagnose_dynamic,
            deterministic_starts=quota_config["deterministic_eta_tau_starts"],
            random_bounds=(
                quota_config["random_bounds_lower"],
                quota_config["random_bounds_upper"],
            ),
            random_count=int(quota_config["random_count"]),
            continuation_starts=previous_quota_starts,
            random_seed=seed + 100 + target_index,
        )
        clusters = cluster_verified_candidates(
            runs,
            lambda candidate: CandidateFeatureBlocks.from_candidate(
                candidate,
                [candidate.total_net_emissions[0], candidate.tax_revenue],
            ),
            distance_threshold=threshold,
        )
        equilibria = []
        previous_quota_starts = []
        for equilibrium_id, cluster in enumerate(clusters):
            source_run = runs[cluster.representative_run_id]
            tax_candidate = source_run.candidate
            tau = float(tax_candidate.metadata["terminal_table_tax_rate"])
            eta = float(tax_candidate.metadata["terminal_eta"])
            previous_quota_starts.append([eta, tau])
            tax_economy = build_paper_example_3_tax_economy(tau)
            quota_economy = map_emission_tax_to_global_quota(
                tax_economy, tax_candidate.allocations, tax_candidate.firm_plans
            )
            quota_candidate = build_quota_candidate(
                quota_economy,
                np.asarray(tax_candidate.prices),
                np.asarray(tax_candidate.allocations),
                np.zeros((1, 3)),
                solver_success=True,
                solver_message="Quota sweep Theorem 4 mapping",
                solver_method="quota_sweep_mapping",
                iterations=0,
                function_calls=0,
                metadata={"target_reduction": target},
            )
            report = QuotaEquilibriumDiagnostics(quota_economy).evaluate(
                quota_candidate
            )
            q_core = float(quota_economy.policy.quota_prices(quota_candidate.prices)[0])
            utilities = {
                consumer.id: consumer.utility(quota_candidate.allocations[index])
                for index, consumer in enumerate(quota_economy.consumers)
            }
            equilibria.append(
                {
                    "equilibrium_id": equilibrium_id,
                    "quota_price_goods_sum_convention": q_core / (1.0 - q_core),
                    "quota_price_core_signed_l1": q_core,
                    "emissions": float(-report.candidate_resource_residual[0]),
                    "allocations": quota_candidate.allocations.tolist(),
                    "utilities": utilities,
                    "ownership_income": quota_candidate.income_breakdowns,
                    "classification": report.classification.value,
                    "residuals": report.errors,
                    "cluster": cluster.to_dict(),
                }
            )
        quota_rows.append(
            {
                "target_reduction_fraction": target,
                "quota_emissions": 0.4 * (1.0 - target),
                "numerical_search_status": (
                    f"DISCOVERED_{len(clusters)}_VERIFIED_CANDIDATE_CLUSTERS"
                ),
                "run_summary": {
                    "total": len(runs),
                    "verified": sum(
                        run.classification == "VERIFIED_CANDIDATE" for run in runs
                    ),
                },
                "equilibria": equilibria,
            }
        )

    actual_tax_counts = [len(row["equilibria"]) for row in tax_rows]
    actual_quota_counts = [len(row["equilibria"]) for row in quota_rows]
    expected_tax_counts = [
        int(value) for value in config["validation"]["expected_tax_cluster_counts"]
    ]
    expected_quota_counts = [
        int(value) for value in config["validation"]["expected_quota_cluster_counts"]
    ]
    validation_passed = validate_cluster_counts(
        actual_tax_counts,
        expected_tax_counts,
        actual_quota_counts,
        expected_quota_counts,
    )
    result = {
        "status": "SWEEP_SUCCESS" if validation_passed else "SWEEP_FAILURE",
        "claim_language": (
            "Each row reports discovered verified candidate clusters; sets are "
            "never averaged and numerical search does not prove exact counts."
        ),
        "config_snapshot": config,
        "tax_emissions_correspondence": tax_rows,
        "quota_price_correspondence": quota_rows,
        "validation": {
            "passed": validation_passed,
            "expected_tax_cluster_counts": expected_tax_counts,
            "actual_tax_cluster_counts": actual_tax_counts,
            "expected_quota_cluster_counts": expected_quota_counts,
            "actual_quota_cluster_counts": actual_quota_counts,
        },
    }
    write_json(ROOT / "results" / "milestone9_tax_quota_sweeps.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(
        [(row["table_goods_sum_tax_rate"], len(row["equilibria"])) for row in output["tax_emissions_correspondence"]]
    )
    print(
        [(row["target_reduction_fraction"], len(row["equilibria"])) for row in output["quota_price_correspondence"]]
    )
