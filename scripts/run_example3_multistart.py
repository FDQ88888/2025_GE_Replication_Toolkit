"""Run seeded multistart, continuation, diagnostics, and clustering on Example 3."""

from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from duanmu_ge_lab import (
    CandidateFeatureBlocks,
    EmissionTaxEquilibriumDiagnostics,
    PaperExample3TaxSolver,
    build_paper_example_3_tax_economy,
    cluster_verified_candidates,
    paper_example_3_good_1_excess,
    solve_multistart,
)
from duanmu_ge_lab.experiment_io import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None):
    path = config_path or ROOT / "configs" / "experiments" / "example3_multistart.yaml"
    config = load_yaml_mapping(path)
    tau = float(config["experiment"]["current_table_tax_rate"])
    prior_tau = float(config["experiment"]["continuation_source_tax_rate"])
    solver_config = config["solver"]
    eta_lower, eta_upper = (float(value) for value in solver_config["eta_bounds"])
    tolerance = float(solver_config["tolerance"])
    residual_acceptance_tolerance = float(
        solver_config["residual_acceptance_tolerance"]
    )
    example_solver = PaperExample3TaxSolver()
    prior_roots = example_solver.solve_tax_rate(prior_tau)
    continuation_starts = [[root.eta] for root in prior_roots]
    economy = build_paper_example_3_tax_economy(tau)
    diagnostics = EmissionTaxEquilibriumDiagnostics(economy)

    def solve_one(initial: np.ndarray):
        result = least_squares(
            lambda point: np.array(
                [paper_example_3_good_1_excess(tau, float(point[0]))]
            ),
            initial,
            bounds=(np.array([eta_lower]), np.array([eta_upper])),
            xtol=tolerance,
            ftol=tolerance,
            gtol=tolerance,
            max_nfev=int(solver_config["max_nfev"]),
        )
        eta = float(result.x[0])
        root = example_solver.build_root(tau, eta)
        residual = abs(root.scalar_residual)
        root.candidate.solver_success = bool(
            result.success and residual <= residual_acceptance_tolerance
        )
        root.candidate.solver_message = str(result.message)
        root.candidate.solver_method = "least_squares:example3_eta_multistart"
        root.candidate.function_calls = int(result.nfev)
        root.candidate.metadata.update(
            {
                "initial_eta": float(initial[0]),
                "terminal_eta": eta,
                "terminal_scalar_residual": residual,
            }
        )
        return root.candidate

    start_config = config["starts"]
    runs = solve_multistart(
        solve_one,
        diagnostics.evaluate,
        deterministic_starts=[
            [float(value)] for value in start_config["deterministic_eta"]
        ],
        random_bounds=(
            [float(start_config["random_eta_bounds"][0])],
            [float(start_config["random_eta_bounds"][1])],
        ),
        random_count=int(start_config["random_count"]),
        continuation_starts=continuation_starts,
        random_seed=int(start_config["random_seed"]),
    )

    def features(candidate):
        return CandidateFeatureBlocks.from_candidate(
            candidate,
            policy_quantities=[
                float(candidate.total_net_emissions[0]),
                float(candidate.tax_revenue),
            ],
        )

    clusters = cluster_verified_candidates(
        runs,
        features,
        distance_threshold=float(config["clustering"]["distance_threshold"]),
    )
    cluster_data = []
    for cluster in clusters:
        representative = runs[cluster.representative_run_id]
        cluster_data.append(
            {
                **cluster.to_dict(),
                "representative_eta": representative.candidate.metadata[
                    "terminal_eta"
                ],
                "representative_emissions": float(
                    representative.candidate.total_net_emissions[0]
                ),
                "representative_reduction_percent": float(
                    100.0
                    * (0.4 - representative.candidate.total_net_emissions[0])
                    / 0.4
                ),
            }
        )
    verified_runs = [
        run for run in runs if run.classification == "VERIFIED_CANDIDATE"
    ]
    result = {
        "status": (
            "MULTISTART_CLUSTERING_SUCCESS"
            if len(clusters) == 3
            else "MULTISTART_CLUSTERING_FAILURE"
        ),
        "claim_language": (
            f"discovered {len(clusters)} verified candidate clusters; this numerical "
            "statement is not an exact equilibrium-count proof"
        ),
        "config_snapshot": config,
        "continuation_source_verified_etas": [root.eta for root in prior_roots],
        "run_counts": {
            "total": len(runs),
            "verified": len(verified_runs),
            "failed_or_unverified": len(runs) - len(verified_runs),
        },
        "runs": [run.to_dict() for run in runs],
        "verified_candidate_clusters": cluster_data,
    }
    write_json(ROOT / "results" / "milestone8_example3_multistart.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["claim_language"])
    print(output["run_counts"])
