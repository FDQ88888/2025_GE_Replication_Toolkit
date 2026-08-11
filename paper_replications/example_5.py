"""Reproduce Example 5 Tables II-III and quota-tax inequivalence."""

from pathlib import Path
from typing import Any

import numpy as np

from duanmu_ge_lab import (
    EmissionTaxEquilibriumDiagnostics,
    PaperExample3TaxSolver,
    PaperExample5TargetSolver,
    QuotaEquilibriumDiagnostics,
    build_paper_example_3_tax_economy,
    build_quota_candidate,
    map_emission_tax_to_global_quota,
)

from paper_replications.common import compare_numeric, load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or ROOT / "configs" / "paper" / "example_5.yaml"
    config = load_yaml_mapping(path)
    target = float(config["model"]["target_reduction_fraction"])
    solver = PaperExample5TargetSolver(
        starts_eta_tau=config["solver"]["starts_eta_tau"],
        tolerance=float(config["solver"]["tolerance"]),
        residual_acceptance_tolerance=float(
            config["solver"]["residual_acceptance_tolerance"]
        ),
        root_deduplication_tolerance=float(
            config["solver"]["root_deduplication_tolerance"]
        ),
    )
    target_roots = solver.solve_target_reduction(target)
    table_rows = []
    quota_branches = []
    for target_root in target_roots:
        tau = target_root.table_goods_sum_tax_rate
        tax_economy = build_paper_example_3_tax_economy(tau)
        target_tax_report = EmissionTaxEquilibriumDiagnostics(tax_economy).evaluate(
            target_root.candidate
        )
        all_tax_roots = PaperExample3TaxSolver().solve_tax_rate(tau)
        all_tax_entries = []
        for branch_root in all_tax_roots:
            report = EmissionTaxEquilibriumDiagnostics(tax_economy).evaluate(
                branch_root.candidate
            )
            all_tax_entries.append(
                {
                    "eta": branch_root.eta,
                    "reduction_percent": branch_root.reduction_percent,
                    "diagnostics": report.to_dict(),
                }
            )
        table_rows.append(
            {
                "table_goods_sum_tax_rate": tau,
                "reductions_percent": [
                    entry["reduction_percent"] for entry in all_tax_entries
                ],
                "branches": all_tax_entries,
            }
        )

        quota_economy = map_emission_tax_to_global_quota(
            tax_economy,
            target_root.candidate.allocations,
            target_root.candidate.firm_plans,
        )
        quota_candidate = build_quota_candidate(
            quota_economy,
            np.asarray(target_root.candidate.prices),
            np.asarray(target_root.candidate.allocations),
            np.zeros((1, 3), dtype=float),
            solver_success=True,
            solver_message="Theorem 4 mapping at Example 5 target reduction",
            solver_method="paper_example_5_theorem_4_mapping",
            iterations=0,
            function_calls=0,
            metadata={"model_role": "PAPER_REPLICATION_EXAMPLE_5"},
        )
        quota_report = QuotaEquilibriumDiagnostics(quota_economy).evaluate(
            quota_candidate
        )
        core_quota_price = float(quota_economy.policy.quota_prices(quota_candidate.prices)[0])
        recovered_goods_sum_price = core_quota_price / (1.0 - core_quota_price)
        quota_branches.append(
            {
                "table_goods_sum_quota_price": recovered_goods_sum_price,
                "core_signed_l1_quota_price": core_quota_price,
                "emissions": float(-quota_report.candidate_resource_residual[0]),
                "target_tax_candidate_diagnostics": target_tax_report.to_dict(),
                "quota_candidate": quota_candidate.to_dict(),
                "quota_diagnostics": quota_report.to_dict(),
            }
        )

    tolerances = config["paper_rounding_tolerances"]
    tax_comparison = compare_numeric(
        config["paper_rounded_quota_prices_goods_sum"],
        [item["table_goods_sum_quota_price"] for item in quota_branches],
        absolute_tolerance=float(tolerances["tax_rate"]),
        relative_tolerance=0.0,
    )
    reduction_comparison = compare_numeric(
        config["paper_rounded_table_ii_reduction_percent"],
        [[round(value, 2) for value in row["reductions_percent"]] for row in table_rows],
        absolute_tolerance=float(tolerances["reduction_percent"]),
        relative_tolerance=0.0,
    )
    success = bool(
        len(target_roots) == 3
        and all(len(row["branches"]) == 3 for row in table_rows)
        and all(
            branch["target_tax_candidate_diagnostics"]["passed"]
            and branch["quota_diagnostics"]["passed"]
            and abs(branch["emissions"] - 0.28) <= 1e-10
            for branch in quota_branches
        )
        and tax_comparison["passed"]
        and reduction_comparison["passed"]
    )
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "target_reduction_fraction": target,
        "target_emissions": 0.4 * (1.0 - target),
        "table_ii_tax_multiplicity": table_rows,
        "table_iii_quota_branches": quota_branches,
        "paper_rounded_comparisons": {
            "quota_prices_goods_sum_convention": tax_comparison,
            "table_ii_reductions": reduction_comparison,
        },
        "conclusion": (
            "Each listed tax rate has three verified candidates with different "
            "emissions reductions; each quota candidate fixes emissions at 0.28 "
            "but the quota price differs."
        ),
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone7_paper_example_5.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    for branch in output["table_iii_quota_branches"]:
        print(branch["table_goods_sum_quota_price"], branch["emissions"])
