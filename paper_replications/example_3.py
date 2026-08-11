"""Reproduce the three-equilibrium row of paper Example 3, Table I."""

from pathlib import Path
from typing import Any

from duanmu_ge_lab import (
    EmissionTaxEquilibriumDiagnostics,
    PaperExample3TaxSolver,
    PriceSign,
    PriceSignRestrictions,
    build_paper_example_3_tax_economy,
)

from paper_replications.common import compare_numeric, load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]
SIGNS = PriceSignRestrictions(
    (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
)


def run(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or ROOT / "configs" / "paper" / "example_3.yaml"
    config = load_yaml_mapping(path)
    tau = float(config["model"]["table_goods_sum_tax_rate"])
    solver_data = config["solver"]
    solver = PaperExample3TaxSolver(
        eta_min=float(solver_data["eta_min"]),
        eta_max=float(solver_data["eta_max"]),
        scan_points=int(solver_data["scan_points"]),
        root_tolerance=float(solver_data["root_tolerance"]),
        root_deduplication_tolerance=float(
            solver_data["root_deduplication_tolerance"]
        ),
    )
    roots = solver.solve_tax_rate(tau)
    economy = build_paper_example_3_tax_economy(tau)
    entries = []
    for branch, root in enumerate(roots, start=1):
        report = EmissionTaxEquilibriumDiagnostics(
            economy, price_sign_restrictions=SIGNS
        ).evaluate(root.candidate)
        entries.append(
            {
                "branch": branch,
                "eta_p1_over_p2_unrounded": root.eta,
                "reduction_percent_unrounded": root.reduction_percent,
                "table_goods_sum_tax_rate": tau,
                "core_signed_l1_tax_rate": float(economy.policy.tax_rates[0]),
                "candidate": root.candidate.to_dict(),
                "complete_diagnostics": report.to_dict(),
            }
        )
    targets = config["paper_rounded_targets"]
    eta_comparison = compare_numeric(
        targets["eta"],
        [round(root.eta, 3) for root in roots],
        absolute_tolerance=float(targets["decimal_tolerance_eta"]),
        relative_tolerance=0.0,
    )
    reduction_comparison = compare_numeric(
        targets["reduction_percent"],
        [round(root.reduction_percent, 2) for root in roots],
        absolute_tolerance=float(targets["decimal_tolerance_reduction"]),
        relative_tolerance=0.0,
    )
    success = bool(
        len(roots) == 3
        and all(entry["complete_diagnostics"]["passed"] for entry in entries)
        and eta_comparison["passed"]
        and reduction_comparison["passed"]
    )
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "paper_theoretical_equilibrium_count_at_tau": 3,
        "numerical_search_status": (
            f"DISCOVERED_{len(roots)}_VERIFIED_CANDIDATE_BRANCHES"
        ),
        "normalization_note": (
            "Table tau uses p1+p2=1. Core diagnostics rescale p and t together "
            "to signed L1."
        ),
        "branches": entries,
        "paper_rounded_comparisons": {
            "eta": eta_comparison,
            "reduction_percent": reduction_comparison,
        },
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone7_paper_example_3.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    for branch in output["branches"]:
        print(
            branch["branch"],
            branch["eta_p1_over_p2_unrounded"],
            branch["reduction_percent_unrounded"],
            branch["complete_diagnostics"]["classification"],
        )
