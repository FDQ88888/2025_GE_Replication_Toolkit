"""Compare Example 2 property-right allocations at fixed total emissions."""

from pathlib import Path

from duanmu_ge_lab import (
    PaperExample2QuotaSolver,
    QuotaEquilibriumDiagnostics,
    build_paper_example_2,
)
from duanmu_ge_lab.experiment_io import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path | None = None):
    path = config_path or ROOT / "configs" / "experiments" / "quota_ownership_welfare.yaml"
    config = load_yaml_mapping(path)
    v = float(config["experiment"]["emissions_quota_v"])
    regimes = {}
    candidates = {}
    for regime in config["experiment"]["regimes"]:
        economy, _ = build_paper_example_2(v, regime)
        candidate = PaperExample2QuotaSolver().solve(economy)
        candidates[regime] = candidate
        report = QuotaEquilibriumDiagnostics(economy).evaluate(candidate)
        profits = economy.firm_profit_breakdowns(
            candidate.prices, candidate.firm_plans
        )
        individual = {}
        for consumer_index, consumer in enumerate(economy.consumers):
            operating_by_firm = {
                firm.id: firm.ownership.share_of(consumer.id)
                * profits[firm.id].operating_profit
                for firm in economy.firms
            }
            quota_by_firm = {
                firm.id: firm.ownership.share_of(consumer.id)
                * profits[firm.id].quota_profit
                for firm in economy.firms
            }
            income = report.consumer_income_breakdowns[consumer.id]
            individual[consumer.id] = {
                "consumption": candidate.allocations[consumer_index].tolist(),
                "own_electricity_component_not_paper_cardinal_utility": float(
                    candidate.allocations[consumer_index, 2]
                ),
                "income_decomposition": income.to_dict(),
                "firm_operating_ownership_income_by_firm": operating_by_firm,
                "quota_income_by_firm": quota_by_firm,
                "tax_rebate": {
                    "applicable": False,
                    "amount": 0.0,
                    "reason": "This is a quota economy, not an emission-tax economy.",
                },
            }
        regimes[regime] = {
            "classification": report.classification.value,
            "passed": report.passed,
            "prices": candidate.prices.tolist(),
            "total_emissions": float(-report.candidate_resource_residual[0]),
            "firm_profit_breakdowns": {
                firm_id: value.to_dict() for firm_id, value in profits.items()
            },
            "individual": individual,
            "diagnostic_errors": report.errors,
        }
    global_candidate = candidates["global_quota"]
    cap_candidate = candidates["cap_and_trade"]
    electricity_difference = (
        global_candidate.allocations[:, 2] - cap_candidate.allocations[:, 2]
    )
    success = bool(
        all(regime["passed"] for regime in regimes.values())
        and abs(regimes["global_quota"]["total_emissions"] - v) <= 1e-10
        and abs(regimes["cap_and_trade"]["total_emissions"] - v) <= 1e-10
    )
    result = {
        "status": (
            "WELFARE_DISTRIBUTION_SUCCESS"
            if success
            else "WELFARE_DISTRIBUTION_FAILURE"
        ),
        "config_snapshot": config,
        "fixed_underlying_objects": [
            "commodities",
            "consumer preferences",
            "endowments",
            "production technologies",
            "total quota",
            "total emissions",
        ],
        "changed_object": "quota property-right allocation between government and firm_1",
        "regimes": regimes,
        "global_minus_cap_electricity": electricity_difference.tolist(),
        "paper_supported_individual_ordering": {
            "omega_1": "global_quota_better",
            "omega_2": "indifferent",
            "omega_3": "cap_and_trade_better",
        },
        "welfare_scope": {
            "comparison": "within-agent comparison at fixed emissions",
            "constrained_pareto_context": True,
            "full_pareto_comparison_across_emissions": False,
            "weighted_welfare_reported": False,
            "reason": (
                "The paper gives no cardinal Example 2 utility or social welfare "
                "objective; no aggregate welfare number is fabricated."
            ),
            "automatic_optimal_carbon_policy": False,
        },
    }
    write_json(ROOT / "results" / "milestone10_welfare_distribution.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["global_minus_cap_electricity"])
    print(output["paper_supported_individual_ordering"])
