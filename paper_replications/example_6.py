"""Reproduce the Example 6 tax/quota target comparison."""

from pathlib import Path
from typing import Any

import numpy as np

from duanmu_ge_lab import (
    EmissionTaxEquilibriumDiagnostics,
    QuotaEquilibriumDiagnostics,
    build_emission_tax_candidate,
    build_paper_example_4_tax_economy,
    build_quota_candidate,
    map_emission_tax_to_global_quota,
    paper_example_4_coordinates,
)

from paper_replications.common import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or ROOT / "configs" / "paper" / "example_6.yaml"
    config = load_yaml_mapping(path)
    v = float(config["model"]["desired_emissions_v_hat"])
    tax = float(config["model"]["supporting_tax_rate"])
    tax_economy = build_paper_example_4_tax_economy(tax)
    prices, allocations, plans = paper_example_4_coordinates(tax, v)
    tax_candidate = build_emission_tax_candidate(
        tax_economy,
        prices,
        allocations,
        plans,
        solver_success=True,
        solver_message="Example 4 boundary branch supporting Example 6 target",
        solver_method="paper_example_4_claim_5_3",
        iterations=0,
        function_calls=0,
        metadata={"model_role": "PAPER_REPLICATION_EXAMPLE_6_TAX_SOURCE"},
    )
    tax_report = EmissionTaxEquilibriumDiagnostics(tax_economy).evaluate(tax_candidate)
    quota_economy = map_emission_tax_to_global_quota(
        tax_economy, allocations, plans
    )
    quota_plans = np.vstack([np.zeros(3), plans])
    quota_candidate = build_quota_candidate(
        quota_economy,
        prices,
        allocations,
        quota_plans,
        solver_success=True,
        solver_message="Theorem 4 global quota construction for Example 6",
        solver_method="paper_example_6_theorem_4_mapping",
        iterations=0,
        function_calls=0,
        metadata={"model_role": "PAPER_REPLICATION_EXAMPLE_6"},
    )
    quota_report = QuotaEquilibriumDiagnostics(quota_economy).evaluate(quota_candidate)
    success = bool(
        tax_report.passed
        and quota_report.passed
        and abs(float(tax_candidate.total_net_emissions[0]) - v) <= 1e-10
        and abs(float(-quota_report.candidate_resource_residual[0]) - v) <= 1e-10
    )
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "desired_emissions_v_hat": v,
        "tax_side": {
            "supporting_tax_rate": tax,
            "candidate": tax_candidate.to_dict(),
            "complete_diagnostics": tax_report.to_dict(),
            "paper_guarantee_status": (
                "DOES_NOT_GUARANTEE_TARGET: same t=1/4 supports every v in [0,1]"
            ),
        },
        "quota_side": {
            "quota": float(-quota_economy.policy.total_m[0]),
            "candidate": quota_candidate.to_dict(),
            "complete_diagnostics": quota_report.to_dict(),
            "candidate_emissions": float(-quota_report.candidate_resource_residual[0]),
            "paper_guarantee_status": "QUOTA_DEFINITION_FIXES_TOTAL_EMISSIONS",
        },
        "claim_scope": (
            "The candidate is a numerical check. The universal guarantee is the "
            "paper's theoretical result, not inferred from one computation."
        ),
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone7_paper_example_6.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["tax_side"]["complete_diagnostics"]["classification"])
    print(output["quota_side"]["complete_diagnostics"]["classification"])
