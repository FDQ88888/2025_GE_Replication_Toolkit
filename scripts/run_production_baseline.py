"""Run and persist the Milestone 2 analytical production benchmark."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    NumericalTolerances,
    ProductionEquilibriumDiagnostics,
    ProductionEquilibriumSolver,
    SolverConfiguration,
    build_analytical_production_benchmark,
)
from duanmu_ge_lab.experiment_io import write_json


def main() -> int:
    """Solve, diagnose, print, and save the production validation experiment."""

    economy, normalization, analytical = build_analytical_production_benchmark()
    tolerances = NumericalTolerances()
    solver_config = SolverConfiguration(bracket=(0.1, 0.8))
    candidate = ProductionEquilibriumSolver(solver_config).solve(
        economy, normalization
    )
    report = ProductionEquilibriumDiagnostics(
        economy, normalization, tolerances
    ).evaluate(candidate)

    distances = {
        "price_l2": float(np.linalg.norm(candidate.prices - analytical.prices)),
        "allocation_l2": float(
            np.linalg.norm(candidate.allocations - analytical.allocations)
        ),
        "firm_plan_l2": float(
            np.linalg.norm(candidate.firm_plans - analytical.firm_plans)
        ),
        "firm_profit_l2": float(
            np.linalg.norm(candidate.firm_profits - analytical.firm_profits)
        ),
    }

    print("Duanmu GE Lab - Milestone 2 Analytical Production Benchmark")
    print()
    print(f"Prices: {candidate.prices.tolist()}")
    print(f"Allocations: {candidate.allocations.tolist()}")
    print(f"Firm plans: {candidate.firm_plans.tolist()}")
    print(f"Firm profits: {candidate.firm_profits.tolist()}")
    print()
    print("Income breakdowns:")
    for consumer_id, breakdown in report.candidate_income_breakdowns.items():
        print(
            f"  {consumer_id}: endowment={breakdown.endowment_income:.16e}, "
            f"dividend={breakdown.firm_dividend_income:.16e}, "
            f"policy={breakdown.policy_income:.16e}, "
            f"total={breakdown.total_income:.16e}"
        )
    print()
    print("Candidate resource residuals (x - e - y):")
    for commodity, residual in zip(
        economy.commodities, report.candidate_resource_residual, strict=True
    ):
        print(f"  {commodity.name}: {residual:.16e}")
    print(f"Candidate Walras residual: {report.candidate_walras_residual:.16e}")
    print()
    print("Firm diagnostics:")
    for firm_id, result in report.firm_optimality_results.items():
        print(
            f"  {firm_id}: feasibility={result.feasibility_violation:.16e}, "
            f"profit_gap={result.profit_gap:.16e}"
        )
    print()
    print(f"Classification: {report.classification.value}")

    result = {
        "model": {
            "name": "milestone2_capacity_constrained_production",
            "role": "ANALYTICAL_PRODUCTION_BENCHMARK",
            "paper_replication": False,
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
            "consumers": [
                {
                    "id": consumer.id,
                    "endowment": np.asarray(consumer.endowment).tolist(),
                    "population_weight": consumer.population_weight,
                    "alphas": np.asarray(consumer.preference.alphas).tolist(),
                }
                for consumer in economy.consumers
            ],
            "firms": [
                {
                    "id": firm.id,
                    "technology": {
                        "type": type(firm.technology).__name__,
                        "net_output_per_unit": np.asarray(
                            firm.technology.net_output_per_unit
                        ).tolist(),
                        "capacity": firm.technology.capacity,
                    },
                    "ownership": firm.ownership.to_dict(),
                }
                for firm in economy.firms
            ],
            "numeraire": {
                "index": normalization.index,
                "value": normalization.value,
            },
        },
        "analytical_solution": analytical.to_dict(),
        "numerical_solution": candidate.to_dict(),
        "analytical_distances": distances,
        "diagnostics": report.to_dict(),
        "solver": {
            "method": solver_config.method,
            "bracket": list(solver_config.bracket),
            "xtol": solver_config.xtol,
            "rtol": solver_config.rtol,
            "maxiter": solver_config.maxiter,
        },
        "tolerances": tolerances.to_dict(),
    }
    project_root = Path(__file__).resolve().parents[1]
    output = project_root / "results" / "milestone2_production_baseline.json"
    result["status"] = report.classification.value
    result["config_snapshot"] = {
        "runner": "scripts/run_production_baseline.py",
        "parameters": result["parameters"],
        "solver": result["solver"],
        "tolerances": result["tolerances"],
    }
    write_json(output, result)
    print(f"Saved JSON: {output}")
    return (
        0
        if report.classification is CandidateClassification.VERIFIED_CANDIDATE
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
