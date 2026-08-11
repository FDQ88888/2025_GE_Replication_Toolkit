"""Run the independently solved replication of paper Example 1."""

from pathlib import Path
from typing import Any

from duanmu_ge_lab import (
    PaperExample1QuotaSolver,
    PriceSign,
    PriceSignRestrictions,
    QuotaEquilibriumDiagnostics,
    build_paper_example_1,
)

from paper_replications.common import compare_numeric, load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None) -> dict[str, Any]:
    config_file = config_path or ROOT / "configs" / "paper" / "example_1.yaml"
    config = load_yaml_mapping(config_file)
    v = float(config["model"]["emissions_quota_v"])
    economy, analytical = build_paper_example_1(v)
    solver_config = config["solver"]
    candidate = PaperExample1QuotaSolver(
        initial_guess=tuple(float(value) for value in solver_config["initial_guess"]),
        tolerance=float(solver_config["tolerance"]),
        max_nfev=int(solver_config["max_nfev"]),
    ).solve(economy)
    diagnostics = QuotaEquilibriumDiagnostics(
        economy,
        price_sign_restrictions=PriceSignRestrictions(
            (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
        ),
    ).evaluate(candidate)
    comparison_config = config["comparison"]
    compare_kwargs = {
        "absolute_tolerance": float(comparison_config["absolute_tolerance"]),
        "relative_tolerance": float(comparison_config["relative_tolerance"]),
    }
    computed = candidate.to_dict()
    target = analytical.to_dict()
    fields = (
        "prices",
        "allocations",
        "firm_plans",
        "quota_prices",
        "operating_profits",
        "quota_profit_terms",
        "total_firm_profits",
        "income_breakdowns",
    )
    comparisons = {
        field: compare_numeric(target[field], computed[field], **compare_kwargs)
        for field in fields
    }
    computed_v = -diagnostics.candidate_resource_residual[0]
    computed_utilities = {
        "omega_1": float(candidate.allocations[0, 2] - computed_v**2),
        "omega_2": float(candidate.allocations[1, 1] - computed_v**2),
    }
    utility_comparison = compare_numeric(
        {
            "omega_1": analytical.paper_utility_data["omega_1"],
            "omega_2": analytical.paper_utility_data["omega_2"],
        },
        computed_utilities,
        **compare_kwargs,
    )
    comparisons["paper_cardinal_utilities"] = utility_comparison
    all_comparisons_passed = all(item["passed"] for item in comparisons.values())
    success = diagnostics.passed and all_comparisons_passed
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "config_path": config_file.resolve().relative_to(ROOT).as_posix(),
        "model": {
            "emissions_quota_v": v,
            "firm_m_vectors": economy.policy.to_dict()["firm_m_vectors"],
            "total_m": economy.policy.total_m.tolist(),
            "permit_commodity_added": False,
        },
        "paper_analytical_solution": target,
        "computed_candidate": computed,
        "comparisons": comparisons,
        "all_comparisons_passed": all_comparisons_passed,
        "complete_diagnostics": diagnostics.to_dict(),
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone5_paper_example_1.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["complete_diagnostics"]["classification"])
