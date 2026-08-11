"""Reproduce the existence boundary and emissions continuum in Example 4."""

from pathlib import Path
from typing import Any

import numpy as np

from duanmu_ge_lab import (
    EmissionTaxEquilibriumDiagnostics,
    PriceSign,
    PriceSignRestrictions,
    build_emission_tax_candidate,
    build_paper_example_4_tax_economy,
    paper_example_4_coordinates,
)

from paper_replications.common import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]
SIGNS = PriceSignRestrictions(
    (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
)


def _candidate(tax: float, emissions: float | None):
    economy = build_paper_example_4_tax_economy(tax)
    prices, allocations, plans = paper_example_4_coordinates(tax, emissions)
    candidate = build_emission_tax_candidate(
        economy,
        prices,
        allocations,
        plans,
        solver_success=True,
        solver_message="Supplement Section 3.4 analytical construction",
        solver_method="paper_claim_5_1_to_5_3_construction",
        iterations=0,
        function_calls=0,
        metadata={"model_role": "PAPER_REPLICATION_EXAMPLE_4"},
    )
    report = EmissionTaxEquilibriumDiagnostics(
        economy, price_sign_restrictions=SIGNS
    ).evaluate(candidate)
    return candidate, report


def run(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or ROOT / "configs" / "paper" / "example_4.yaml"
    config = load_yaml_mapping(path)
    below_tax = float(config["model"]["below_boundary_tax_rate"])
    below_candidate, below_report = _candidate(below_tax, 1.0)
    boundary_tax = float(config["model"]["boundary_tax_rate"])
    boundary = []
    for emissions in config["model"]["boundary_emissions_grid"]:
        candidate, report = _candidate(boundary_tax, float(emissions))
        boundary.append(
            {
                "emissions": float(emissions),
                "candidate": candidate.to_dict(),
                "complete_diagnostics": report.to_dict(),
            }
        )
    above_tax = float(config["model"]["above_boundary_tax_rate"])
    implied_electricity_price = 0.5
    sequestration_unit_margin = 2.0 * above_tax - implied_electricity_price
    numerical_status = (
        "NO_VERIFIED_CANDIDATE_ANALYTIC_PRECHECK_UNBOUNDED_FIRM_2_PROFIT"
        if sequestration_unit_margin > 0.0
        else "PRECHECK_INCONCLUSIVE"
    )
    success = bool(
        below_report.passed
        and all(item["complete_diagnostics"]["passed"] for item in boundary)
        and config["paper_theoretical_status_above_boundary"] == "NO_EQUILIBRIUM"
        and sequestration_unit_margin > 0.0
    )
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "below_boundary": {
            "tax_rate": below_tax,
            "paper_theoretical_emissions": 1.0,
            "candidate": below_candidate.to_dict(),
            "complete_diagnostics": below_report.to_dict(),
        },
        "boundary_continuum_sample": {
            "tax_rate": boundary_tax,
            "paper_theoretical_emissions_set": "[0,1]",
            "sampled_verified_candidates": boundary,
        },
        "above_boundary": {
            "tax_rate": above_tax,
            "paper_theoretical_status": config[
                "paper_theoretical_status_above_boundary"
            ],
            "numerical_search_status": numerical_status,
            "analytic_precheck_firm_2_unit_margin": sequestration_unit_margin,
            "language_guard": (
                "The paper proves nonexistence. This computational precheck is not "
                "presented as a numerical proof of nonexistence."
            ),
        },
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone7_paper_example_4.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["below_boundary"]["complete_diagnostics"]["classification"])
    print(len(output["boundary_continuum_sample"]["sampled_verified_candidates"]))
    print(output["above_boundary"]["paper_theoretical_status"])
