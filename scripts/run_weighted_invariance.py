"""Run the Milestone 3 split-agent invariance experiment."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    NumericalTolerances,
    ProductionEquilibriumDiagnostics,
    ProductionEquilibriumSolver,
    SolverConfiguration,
    build_split_agent_invariance_benchmarks,
)
from duanmu_ge_lab.experiment_io import write_json


def main() -> int:
    """Solve equivalent original and split weighted economies and compare them."""

    original, split, normalization = build_split_agent_invariance_benchmarks()
    configuration = SolverConfiguration(bracket=(0.1, 0.8))
    tolerances = NumericalTolerances()
    solver = ProductionEquilibriumSolver(configuration)
    original_candidate = solver.solve(original, normalization)
    split_candidate = solver.solve(split, normalization)
    original_report = ProductionEquilibriumDiagnostics(
        original, normalization, tolerances
    ).evaluate(original_candidate)
    split_report = ProductionEquilibriumDiagnostics(
        split, normalization, tolerances
    ).evaluate(split_candidate)

    original_aggregate = original.aggregate_allocations(
        original_candidate.allocations
    )
    split_aggregate = split.aggregate_allocations(split_candidate.allocations)
    differences = {
        "price_l2": float(
            np.linalg.norm(original_candidate.prices - split_candidate.prices)
        ),
        "aggregate_allocation_l2": float(
            np.linalg.norm(original_aggregate - split_aggregate)
        ),
        "aggregate_endowment_l2": float(
            np.linalg.norm(
                original.aggregate_endowment() - split.aggregate_endowment()
            )
        ),
        "firm_plan_l2": float(
            np.linalg.norm(
                original_candidate.firm_plans - split_candidate.firm_plans
            )
        ),
        "firm_profit_l2": float(
            np.linalg.norm(
                original_candidate.firm_profits - split_candidate.firm_profits
            )
        ),
        "resource_residual_l2": float(
            np.linalg.norm(
                np.asarray(original_report.candidate_resource_residual)
                - np.asarray(split_report.candidate_resource_residual)
            )
        ),
    }
    print("Duanmu GE Lab - Milestone 3 Split-Agent Invariance")
    print()
    print(f"Original weights: {original.population_weights().tolist()}")
    print(f"Split weights: {split.population_weights().tolist()}")
    print(
        "Weighted ownership totals: "
        f"original={original.ownership_total(original.firms[0]):.16e}, "
        f"split={split.ownership_total(split.firms[0]):.16e}"
    )
    print(f"Original prices: {original_candidate.prices.tolist()}")
    print(f"Split prices: {split_candidate.prices.tolist()}")
    print(f"Original aggregate allocation: {original_aggregate.tolist()}")
    print(f"Split aggregate allocation: {split_aggregate.tolist()}")
    print(f"Differences: {differences}")
    print(
        "Classifications: "
        f"{original_report.classification.value}, "
        f"{split_report.classification.value}"
    )

    result = {
        "model": {
            "name": "milestone3_split_agent_invariance",
            "role": "FINITE_WEIGHTED_SOFTWARE_VALIDATION_BENCHMARK",
            "paper_replication": False,
            "population_weights_are_welfare_weights": False,
        },
        "original": {
            "population_weights": original.population_weights().tolist(),
            "weighted_ownership_total": original.ownership_total(
                original.firms[0]
            ),
            "candidate": original_candidate.to_dict(),
            "diagnostics": original_report.to_dict(),
            "aggregate_allocation": original_aggregate.tolist(),
            "aggregate_endowment": original.aggregate_endowment().tolist(),
        },
        "split": {
            "population_weights": split.population_weights().tolist(),
            "weighted_ownership_total": split.ownership_total(split.firms[0]),
            "raw_unweighted_ownership_sum": split.firms[0].ownership.total_share,
            "candidate": split_candidate.to_dict(),
            "diagnostics": split_report.to_dict(),
            "aggregate_allocation": split_aggregate.tolist(),
            "aggregate_endowment": split.aggregate_endowment().tolist(),
        },
        "invariance_differences": differences,
        "solver": {
            "method": configuration.method,
            "bracket": list(configuration.bracket),
        },
        "tolerances": tolerances.to_dict(),
    }
    passed = bool(
        original_report.classification
        is CandidateClassification.VERIFIED_CANDIDATE
        and split_report.classification
        is CandidateClassification.VERIFIED_CANDIDATE
        and all(value <= 1e-12 for value in differences.values())
    )
    result["status"] = (
        "SPLIT_AGENT_INVARIANCE_SUCCESS" if passed else "SPLIT_AGENT_INVARIANCE_FAILURE"
    )
    result["config_snapshot"] = {
        "runner": "scripts/run_weighted_invariance.py",
        "construction": "built-in analytical split-agent benchmark",
        "solver": result["solver"],
        "tolerances": result["tolerances"],
    }
    output = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "milestone3_split_agent_invariance.json"
    )
    write_json(output, result)
    print(f"Saved JSON: {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
