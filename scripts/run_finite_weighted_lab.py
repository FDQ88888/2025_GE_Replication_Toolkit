"""Paper-inspired finite weighted bad-absorption approximation experiment."""

from pathlib import Path
from time import perf_counter

import numpy as np

from duanmu_ge_lab import (
    BadAbsorptionLinearUtility,
    BoxConsumptionSet,
    ClearingRule,
    Commodity,
    CommodityKind,
    Consumer,
    EquilibriumCandidate,
    EquilibriumDiagnostics,
    ExchangeEconomy,
    FixedNumeraire,
    PriceSign,
    PriceSignRestrictions,
)
from duanmu_ge_lab.experiment_io import load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]


def _tail_diagnostics(absorption, weights, top_fraction, truncation):
    order = np.argsort(absorption)[::-1]
    sorted_absorption = absorption[order]
    sorted_weights = weights[order]
    count = max(1, int(np.ceil(top_fraction / float(np.max(weights)))))
    count = min(count, absorption.size)
    top_mass = float(np.sum(sorted_weights[:count]))
    total = float(np.dot(weights, absorption))
    top_integral = float(np.dot(sorted_weights[:count], sorted_absorption[:count]))
    return {
        "max_individual_bad_absorption": float(np.max(absorption)),
        "requested_top_population_fraction": top_fraction,
        "actual_top_population_mass_due_to_atoms": top_mass,
        "top_population_absorption_share": top_integral / total,
        "weighted_tail_integral": top_integral,
        "truncation_level": truncation,
        "weighted_truncated_mean": float(
            np.dot(weights, np.minimum(absorption, truncation))
        ),
        "largest_population_atom": float(np.max(weights)),
        "interpretation": (
            "Heuristic concentration diagnostics related to tail control; not a "
            "uniform-integrability proof."
        ),
    }


def run(config_path: Path | None = None):
    path = config_path or ROOT / "configs" / "experiments" / "finite_weighted_bad_absorption.yaml"
    config = load_yaml_mapping(path)
    prices = np.array(config["continuum_type_target"]["target_prices"], dtype=float)
    target_aggregate = np.array(
        config["continuum_type_target"]["target_aggregate_consumption"], dtype=float
    )
    results = []
    for population_size in config["experiment"]["population_sizes"]:
        start_time = perf_counter()
        n = int(population_size)
        types = (np.arange(n, dtype=float) + 0.5) / n
        weight = 1.0 / n
        consumers = tuple(
            Consumer(
                id=f"type_{index:04d}",
                preference=BadAbsorptionLinearUtility(
                    bad_disutility=0.25 + 0.5 * float(z),
                    max_bad=0.5 + float(z),
                ),
                endowment=np.array([1.0, 2.0]),
                population_weight=weight,
                consumption_set=BoxConsumptionSet(
                    [0.0, 0.0], [0.5 + float(z), np.inf]
                ),
            )
            for index, z in enumerate(types)
        )
        economy = ExchangeEconomy(
            commodities=(
                Commodity("absorbed bad", 0, ClearingRule.EXACT, CommodityKind.BAD),
                Commodity("ordinary good", 1, ClearingRule.EXACT, CommodityKind.GOOD),
            ),
            consumers=consumers,
        )
        allocations = economy.individual_demands(prices)
        aggregate = economy.aggregate_allocations(allocations)
        endowment = economy.aggregate_endowment()
        residual = aggregate - endowment
        candidate = EquilibriumCandidate(
            prices=prices,
            allocations=allocations,
            aggregate_demand=aggregate,
            aggregate_endowment=endowment,
            excess_demand=residual,
            solver_success=True,
            solver_message="Analytical midpoint finite-weight construction",
            solver_method="paper_inspired_analytical_construction",
            iterations=0,
            function_calls=0,
            metadata={
                "model_role": "PAPER_INSPIRED_FINITE_APPROXIMATION_EXPERIMENT",
                "population_size": n,
            },
        )
        report = EquilibriumDiagnostics(
            economy,
            FixedNumeraire(index=1, value=1.0),
            price_sign_restrictions=PriceSignRestrictions(
                (PriceSign.NEGATIVE, PriceSign.POSITIVE)
            ),
        ).evaluate(candidate)
        weights = np.array([consumer.population_weight for consumer in consumers])
        utilities = np.array(
            [
                consumer.utility(allocations[index])
                for index, consumer in enumerate(consumers)
            ]
        )
        runtime = perf_counter() - start_time
        results.append(
            {
                "N": n,
                "population_weights": {
                    "count": n,
                    "common_weight": weight,
                    "sum": float(np.sum(weights)),
                },
                "prices": prices.tolist(),
                "aggregate_consumption": aggregate.tolist(),
                "aggregate_endowment": endowment.tolist(),
                "production": [0.0, 0.0],
                "emissions_unabsorbed_bad": float(endowment[0] - aggregate[0]),
                "welfare_summary": {
                    "label": "population-weighted utility representation summary",
                    "weighted_mean": float(np.dot(weights, utilities)),
                    "minimum": float(np.min(utilities)),
                    "maximum": float(np.max(utilities)),
                    "not_a_social_welfare_optimum": True,
                },
                "tail_diagnostics": _tail_diagnostics(
                    allocations[:, 0],
                    weights,
                    float(config["tail_diagnostics"]["top_population_fraction"]),
                    float(config["tail_diagnostics"]["truncation_level"]),
                ),
                "resource_residual": residual.tolist(),
                "target_aggregate_error_linf": float(
                    np.max(np.abs(aggregate - target_aggregate))
                ),
                "runtime_seconds": runtime,
                "classification": report.classification.value,
                "diagnostic_errors": report.errors,
            }
        )
    success = all(item["classification"] == "VERIFIED_CANDIDATE" for item in results)
    output = {
        "status": (
            "FINITE_WEIGHTED_EXPERIMENT_SUCCESS"
            if success
            else "FINITE_WEIGHTED_EXPERIMENT_FAILURE"
        ),
        "claim_scope": (
            "PAPER-INSPIRED FINITE APPROXIMATION EXPERIMENT; not a paper "
            "replication, measure-theoretic convergence proof, Loeb measure, or "
            "hyperfinite implementation"
        ),
        "config_snapshot": config,
        "continuum_type_target": config["continuum_type_target"],
        "finite_results": results,
    }
    write_json(ROOT / "results" / "milestone11_finite_weighted_lab.json", output)
    return output


if __name__ == "__main__":
    output = run()
    print(output["status"])
    for item in output["finite_results"]:
        print(
            item["N"],
            item["prices"],
            item["aggregate_consumption"],
            item["tail_diagnostics"]["max_individual_bad_absorption"],
            item["classification"],
        )
