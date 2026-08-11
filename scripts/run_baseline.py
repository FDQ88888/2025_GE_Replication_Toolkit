"""Run and persist the Duanmu GE Lab Milestone 1 analytical benchmark."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    EquilibriumDiagnostics,
    ExchangeEquilibriumSolver,
    NumericalTolerances,
    SolverConfiguration,
    build_two_by_two_cobb_douglas_benchmark,
)
from duanmu_ge_lab.experiment_io import write_json


def main() -> int:
    """Solve, independently diagnose, print, and save the baseline experiment."""

    economy, normalization, analytical = build_two_by_two_cobb_douglas_benchmark()
    tolerances = NumericalTolerances()
    solver_config = SolverConfiguration(bracket=(0.05, 20.0))
    solver = ExchangeEquilibriumSolver(configuration=solver_config)
    candidate = solver.solve(economy, normalization)
    report = EquilibriumDiagnostics(
        economy=economy,
        normalization=normalization,
        tolerances=tolerances,
    ).evaluate(candidate)

    price_distance = float(
        np.linalg.norm(np.asarray(candidate.prices) - analytical.prices)
    )
    allocation_distance = float(
        np.linalg.norm(np.asarray(candidate.allocations) - analytical.allocations)
    )

    print("Duanmu GE Lab - Milestone 1 Analytical Benchmark")
    print()
    print("Economy:")
    print(f"  {economy.n_consumers} consumers")
    print(f"  {economy.n_goods} goods")
    print("  Cobb-Douglas alpha = (0.5, 0.5)")
    print()
    print("Normalization:")
    print("  Good 2 numeraire = 1")
    print()
    print("Analytical equilibrium:")
    print(f"  p = {analytical.prices.tolist()}")
    print()
    print("Numerical candidate:")
    print(f"  p = {np.asarray(candidate.prices).tolist()}")
    print(f"  allocations = {np.asarray(candidate.allocations).tolist()}")
    print()
    print("Candidate resource residuals (allocation - endowment):")
    for commodity, residual in zip(
        economy.commodities, report.candidate_resource_residual, strict=True
    ):
        print(f"  {commodity.name}: {residual:.16e}")
    print()
    print("Candidate Walras residual (p dot candidate resource residual):")
    print(f"  {report.candidate_walras_residual:.16e}")
    print()
    print("Reoptimized demand residuals (counterfactual diagnostic):")
    for commodity, residual in zip(
        economy.commodities, report.reoptimized_resource_residual, strict=True
    ):
        print(f"  {commodity.name}: {residual:.16e}")
    print()
    print("Budget residuals (wealth - expenditure):")
    for consumer_id, residual in report.budget_residuals.items():
        print(f"  {consumer_id}: {residual:.16e}")
    print()
    print("Utility optimality gaps:")
    for consumer_id, gap in report.utility_gaps.items():
        formatted_gap = "unsupported" if gap is None else f"{gap:.16e}"
        print(f"  {consumer_id}: {formatted_gap}")
    print()
    print("Analytical distances:")
    print(f"  price L2 distance: {price_distance:.16e}")
    print(f"  allocation L2 distance: {allocation_distance:.16e}")
    print()
    print("Classification:")
    print(f"  {report.classification.value}")

    result = {
        "model": {
            "name": "milestone1_two_consumer_two_good_cobb_douglas",
            "role": "SOFTWARE_VALIDATION_BENCHMARK",
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
            "numeraire": {"index": normalization.index, "value": normalization.value},
        },
        "analytical_solution": analytical.to_dict(),
        "numerical_solution": candidate.to_dict(),
        "analytical_distances": {
            "price_l2": price_distance,
            "allocation_l2": allocation_distance,
        },
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
    result_path = project_root / "results" / "milestone1_baseline.json"
    result["status"] = report.classification.value
    result["config_snapshot"] = {
        "runner": "scripts/run_baseline.py",
        "parameters": result["parameters"],
        "solver": result["solver"],
        "tolerances": result["tolerances"],
    }
    write_json(result_path, result)
    print()
    print(f"Saved JSON: {result_path}")

    return (
        0
        if report.classification is CandidateClassification.VERIFIED_CANDIDATE
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
