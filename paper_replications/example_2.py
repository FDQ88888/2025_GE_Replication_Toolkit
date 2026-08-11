"""Run both property-rights regimes in paper Example 2."""

from pathlib import Path
from typing import Any

import numpy as np

from duanmu_ge_lab import (
    PaperExample2QuotaSolver,
    PriceSign,
    PriceSignRestrictions,
    QuotaEquilibriumDiagnostics,
    build_paper_example_2,
)

from paper_replications.common import compare_numeric, load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None) -> dict[str, Any]:
    config_file = config_path or ROOT / "configs" / "paper" / "example_2.yaml"
    config = load_yaml_mapping(config_file)
    v = float(config["model"]["emissions_quota_v"])
    solver_config = config["solver"]
    solver = PaperExample2QuotaSolver(
        initial_guess=tuple(float(value) for value in solver_config["initial_guess"]),
        tolerance=float(solver_config["tolerance"]),
        max_nfev=int(solver_config["max_nfev"]),
    )
    compare_config = config["comparison"]
    compare_kwargs = {
        "absolute_tolerance": float(compare_config["absolute_tolerance"]),
        "relative_tolerance": float(compare_config["relative_tolerance"]),
    }
    regimes: dict[str, Any] = {}
    candidates = {}
    for regime in config["model"]["regimes"]:
        economy, analytical = build_paper_example_2(v, regime)
        candidate = solver.solve(economy)
        candidates[regime] = candidate
        diagnostics = QuotaEquilibriumDiagnostics(
            economy,
            price_sign_restrictions=PriceSignRestrictions(
                (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
            ),
        ).evaluate(candidate)
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
        comparison_pass = all(item["passed"] for item in comparisons.values())
        regimes[regime] = {
            "status": (
                "PAPER_REPLICATION_SUCCESS"
                if diagnostics.passed and comparison_pass
                else "PAPER_REPLICATION_FAILURE"
            ),
            "firm_m_vectors": economy.policy.to_dict()["firm_m_vectors"],
            "paper_analytical_solution": target,
            "computed_candidate": computed,
            "comparisons": comparisons,
            "all_comparisons_passed": comparison_pass,
            "complete_diagnostics": diagnostics.to_dict(),
            "own_electricity_component_not_paper_cardinal_utility": {
                consumer.id: float(candidate.allocations[index, 2])
                for index, consumer in enumerate(economy.consumers)
            },
        }

    global_electricity = np.asarray(candidates["global_quota"].allocations)[:, 2]
    cap_electricity = np.asarray(candidates["cap_and_trade"].allocations)[:, 2]
    difference = global_electricity - cap_electricity
    distribution_check = {
        "global_minus_cap_electricity": difference.tolist(),
        "paper_target": [v / 12.0, 0.0, -v / 12.0],
        "comparison": compare_numeric(
            [v / 12.0, 0.0, -v / 12.0], difference, **compare_kwargs
        ),
        "paper_supported_ordinal_welfare": {
            "omega_1": "global_quota_better",
            "omega_2": "indifferent_at_fixed_emissions",
            "omega_3": "cap_and_trade_better",
        },
        "cardinal_utility_warning": (
            "The paper supplies no cardinal utility formula for Example 2; "
            "electricity consumption identifies the within-agent welfare ordering "
            "because total emissions are fixed across regimes."
        ),
    }
    prices_equal = compare_numeric(
        candidates["global_quota"].prices,
        candidates["cap_and_trade"].prices,
        **compare_kwargs,
    )
    total_consumption_equal = compare_numeric(
        np.sum(candidates["global_quota"].allocations, axis=0),
        np.sum(candidates["cap_and_trade"].allocations, axis=0),
        **compare_kwargs,
    )
    success = bool(
        all(value["status"] == "PAPER_REPLICATION_SUCCESS" for value in regimes.values())
        and distribution_check["comparison"]["passed"]
        and prices_equal["passed"]
        and total_consumption_equal["passed"]
    )
    result = {
        "status": (
            "PAPER_REPLICATION_SUCCESS" if success else "PAPER_REPLICATION_FAILURE"
        ),
        "paper": config["paper"],
        "config_path": config_file.resolve().relative_to(ROOT).as_posix(),
        "model": {
            "emissions_quota_v": v,
            "regimes": list(config["model"]["regimes"]),
            "permit_commodity_added": False,
        },
        "regimes": regimes,
        "property_rights_distribution_check": distribution_check,
        "aggregate_invariance_checks": {
            "prices": prices_equal,
            "total_consumption": total_consumption_equal,
        },
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone5_paper_example_2.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    for name, regime in output["regimes"].items():
        print(name, regime["status"], regime["complete_diagnostics"]["classification"])
