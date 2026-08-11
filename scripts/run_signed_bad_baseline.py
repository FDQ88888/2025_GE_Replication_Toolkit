"""Run the Milestone 4 signed-price bad-absorption benchmark."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    EquilibriumCandidate,
    EquilibriumDiagnostics,
    NumericalTolerances,
    build_signed_bad_absorption_benchmark,
    rescale_to_fixed_numeraire,
)
from duanmu_ge_lab.experiment_io import write_json


def main() -> int:
    """Verify and persist the analytical negative-price candidate."""

    economy, normalization, restrictions, analytical = (
        build_signed_bad_absorption_benchmark()
    )
    aggregate = economy.aggregate_allocations(analytical.allocations)
    endowment = economy.aggregate_endowment()
    candidate = EquilibriumCandidate(
        prices=analytical.prices,
        allocations=analytical.allocations,
        aggregate_demand=aggregate,
        aggregate_endowment=endowment,
        excess_demand=aggregate - endowment,
        solver_success=True,
        solver_message="analytical signed-price candidate",
        solver_method="analytical",
        metadata={"model_role": "SIGNED_BAD_ABSORPTION_BENCHMARK"},
    )
    tolerances = NumericalTolerances()
    report = EquilibriumDiagnostics(
        economy,
        normalization,
        tolerances,
        restrictions,
    ).evaluate(candidate)
    l1_prices = np.asarray(report.signed_l1_prices)
    recovered = rescale_to_fixed_numeraire(l1_prices, normalization)

    print("Duanmu GE Lab - Milestone 4 Signed Bad-Absorption Benchmark")
    print()
    print(f"Numeraire prices: {candidate.prices.tolist()}")
    print(f"Signed L1 prices: {l1_prices.tolist()}")
    print(f"Recovered numeraire prices: {recovered.tolist()}")
    print(f"Allocation: {candidate.allocations.tolist()}")
    print(f"Resource residual: {report.candidate_resource_residual}")
    print(f"Walras residual: {report.candidate_walras_residual:.16e}")
    print(f"Checks: {report.checks}")
    print(f"Classification: {report.classification.value}")

    consumer = economy.consumers[0]
    upper_bounds = [
        None if np.isposinf(value) else float(value)
        for value in np.asarray(consumer.consumption_set.upper_bounds)
    ]
    result = {
        "model": {
            "name": "milestone4_signed_bad_absorption",
            "role": "SIGNED_BAD_ABSORPTION_SOFTWARE_VALIDATION_BENCHMARK",
            "paper_replication": False,
            "commodity_kind_implies_price_sign": False,
            "commodity_kind_implies_disposal": False,
        },
        "parameters": {
            "commodities": [
                {
                    "name": commodity.name,
                    "index": commodity.index,
                    "kind": commodity.kind.value,
                    "clearing_rule": commodity.clearing_rule.value,
                }
                for commodity in economy.commodities
            ],
            "consumer": {
                "id": consumer.id,
                "endowment": np.asarray(consumer.endowment).tolist(),
                "population_weight": consumer.population_weight,
                "preference": {
                    "type": type(consumer.preference).__name__,
                    "bad_disutility": consumer.preference.bad_disutility,
                    "max_bad": consumer.preference.max_bad,
                },
                "consumption_set": {
                    "type": type(consumer.consumption_set).__name__,
                    "lower_bounds": np.asarray(
                        consumer.consumption_set.lower_bounds
                    ).tolist(),
                    "upper_bounds": upper_bounds,
                },
            },
            "price_sign_restrictions": restrictions.to_dict(),
            "numeraire": {
                "index": normalization.index,
                "value": normalization.value,
            },
        },
        "analytical_solution": analytical.to_dict(),
        "candidate": candidate.to_dict(),
        "diagnostics": report.to_dict(),
        "normalization_round_trip": {
            "signed_l1_prices": l1_prices.tolist(),
            "recovered_fixed_numeraire_prices": recovered.tolist(),
            "max_abs_error": float(
                np.max(np.abs(recovered - np.asarray(candidate.prices)))
            ),
        },
        "tolerances": tolerances.to_dict(),
    }
    output = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "milestone4_signed_bad_absorption.json"
    )
    passed = bool(
        report.classification is CandidateClassification.VERIFIED_CANDIDATE
        and result["normalization_round_trip"]["max_abs_error"] <= 1e-12
    )
    result["status"] = (
        "SIGNED_BAD_ABSORPTION_SUCCESS" if passed else "SIGNED_BAD_ABSORPTION_FAILURE"
    )
    result["config_snapshot"] = {
        "runner": "scripts/run_signed_bad_baseline.py",
        "parameters": result["parameters"],
        "tolerances": result["tolerances"],
    }
    write_json(output, result)
    print(f"Saved JSON: {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
