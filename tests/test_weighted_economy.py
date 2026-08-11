import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    CobbDouglasUtility,
    Consumer,
    ProductionEquilibriumDiagnostics,
    ProductionEquilibriumSolver,
    SolverConfiguration,
    build_split_agent_invariance_benchmarks,
)


def test_population_weight_must_be_positive_and_finite() -> None:
    for bad_weight in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="population weight"):
            Consumer(
                id="bad weight",
                preference=CobbDouglasUtility([0.5, 0.5]),
                endowment=[1.0, 0.0],
                population_weight=bad_weight,
            )


def test_split_agent_preserves_weighted_ownership_and_endowment() -> None:
    original, split, _ = build_split_agent_invariance_benchmarks()

    np.testing.assert_allclose(
        original.aggregate_endowment(), split.aggregate_endowment(), atol=1e-14
    )
    assert original.ownership_total(original.firms[0]) == pytest.approx(1.0)
    assert split.ownership_total(split.firms[0]) == pytest.approx(1.0)
    assert sum(split.population_weights()) == pytest.approx(1.0)
    assert split.firms[0].ownership.total_share == pytest.approx(2.0)


def test_split_agent_invariance_of_equilibrium_and_aggregates() -> None:
    original, split, normalization = build_split_agent_invariance_benchmarks()
    solver = ProductionEquilibriumSolver(
        SolverConfiguration(bracket=(0.1, 0.8))
    )

    original_candidate = solver.solve(original, normalization)
    split_candidate = solver.solve(split, normalization)
    original_report = ProductionEquilibriumDiagnostics(
        original, normalization
    ).evaluate(original_candidate)
    split_report = ProductionEquilibriumDiagnostics(split, normalization).evaluate(
        split_candidate
    )

    assert original_report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert split_report.classification is CandidateClassification.VERIFIED_CANDIDATE
    np.testing.assert_allclose(
        original_candidate.prices, split_candidate.prices, atol=1e-12
    )
    np.testing.assert_allclose(
        original.aggregate_allocations(original_candidate.allocations),
        split.aggregate_allocations(split_candidate.allocations),
        atol=1e-12,
    )
    np.testing.assert_allclose(
        original_candidate.firm_plans, split_candidate.firm_plans, atol=1e-14
    )
    np.testing.assert_allclose(
        original_candidate.firm_profits, split_candidate.firm_profits, atol=1e-12
    )
    np.testing.assert_allclose(
        original_report.candidate_resource_residual,
        split_report.candidate_resource_residual,
        atol=1e-12,
    )
