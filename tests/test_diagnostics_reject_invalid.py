import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    EquilibriumCandidate,
    EquilibriumDiagnostics,
    build_two_by_two_cobb_douglas_benchmark,
)


def test_diagnostics_rejects_fabricated_solver_success_and_cached_residuals() -> None:
    economy, normalization, analytical = (
        build_two_by_two_cobb_douglas_benchmark()
    )
    bad_candidate = EquilibriumCandidate(
        prices=np.array([2.0, 1.0]),
        allocations=analytical.allocations,
        aggregate_demand=np.array([1.0, 1.0]),
        aggregate_endowment=np.array([1.0, 1.0]),
        excess_demand=np.array([0.0, 0.0]),
        solver_success=True,
        solver_message="fabricated success",
        solver_method="manual",
        iterations=1,
        function_calls=1,
        metadata={"purpose": "prove diagnostics independence"},
    )

    report = EquilibriumDiagnostics(economy, normalization).evaluate(bad_candidate)

    assert report.classification is CandidateClassification.SOLVER_POINT
    assert not report.passed
    assert not report.checks["consumer_optimality"]
    assert report.checks["market_clearing"]
    assert not report.checks["budget_feasibility"]
    np.testing.assert_allclose(
        report.candidate_resource_residual, [0.0, 0.0], atol=1e-14
    )
    np.testing.assert_allclose(
        report.reoptimized_resource_residual, [-0.25, 0.5], atol=1e-14
    )
    assert report.candidate_walras_residual == 0.0
    assert report.reoptimized_walras_residual == 0.0


def test_candidate_allocation_controls_market_clearing_not_reoptimized_demand() -> None:
    economy, normalization, _ = build_two_by_two_cobb_douglas_benchmark()
    candidate = EquilibriumCandidate(
        prices=np.array([1.0, 1.0]),
        allocations=np.array([[0.8, 0.2], [0.8, 0.2]]),
        aggregate_demand=np.array([1.0, 1.0]),
        aggregate_endowment=np.array([1.0, 1.0]),
        excess_demand=np.array([0.0, 0.0]),
        solver_success=True,
        solver_message="candidate differs from reoptimized demand",
        solver_method="manual",
    )

    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    np.testing.assert_allclose(
        report.candidate_resource_residual, [0.6, -0.6], atol=1e-14
    )
    np.testing.assert_allclose(
        report.reoptimized_allocations,
        [[0.5, 0.5], [0.5, 0.5]],
        atol=1e-14,
    )
    np.testing.assert_allclose(
        report.reoptimized_resource_residual, [0.0, 0.0], atol=1e-14
    )
    assert not report.checks["market_clearing"]
    assert not report.checks["consumer_optimality"]
    assert report.candidate_walras_residual == pytest.approx(0.0, abs=1e-14)
    assert report.reoptimized_walras_residual == pytest.approx(0.0, abs=1e-14)
    assert report.utility_gaps["Consumer 1"] == pytest.approx(0.1)
    assert report.utility_gaps["Consumer 2"] == pytest.approx(0.1)


def test_diagnostics_rejects_negative_candidate_consumption() -> None:
    economy, normalization, _ = build_two_by_two_cobb_douglas_benchmark()
    candidate = EquilibriumCandidate(
        prices=np.array([1.0, 1.0]),
        allocations=np.array([[-0.1, 1.1], [1.1, -0.1]]),
        aggregate_demand=np.array([1.0, 1.0]),
        aggregate_endowment=np.array([1.0, 1.0]),
        excess_demand=np.array([0.0, 0.0]),
        solver_success=True,
        solver_message="resource-feasible but outside the consumption set",
        solver_method="manual",
    )

    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    assert report.checks["market_clearing"]
    assert report.checks["budget_feasibility"]
    assert not report.checks["consumer_feasibility"]
    assert not report.checks["consumer_optimality"]
    assert not report.passed
    assert report.consumer_feasibility_violations == {
        "Consumer 1": 0.1,
        "Consumer 2": 0.1,
    }
    assert all(
        result.candidate_utility is None
        for result in report.consumer_optimality_results.values()
    )


def test_diagnostics_does_not_promote_solver_failure() -> None:
    economy, normalization, analytical = (
        build_two_by_two_cobb_douglas_benchmark()
    )
    candidate = EquilibriumCandidate(
        prices=analytical.prices,
        allocations=analytical.allocations,
        aggregate_demand=np.array([1.0, 1.0]),
        aggregate_endowment=np.array([1.0, 1.0]),
        excess_demand=np.array([0.0, 0.0]),
        solver_success=False,
        solver_message="forced failure",
        solver_method="manual",
    )

    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    assert report.classification is CandidateClassification.FAILED_RUN
    assert not report.passed


def test_diagnostics_rejects_malformed_cached_vector_shapes() -> None:
    economy, normalization, analytical = (
        build_two_by_two_cobb_douglas_benchmark()
    )
    candidate = EquilibriumCandidate(
        prices=analytical.prices,
        allocations=analytical.allocations,
        aggregate_demand=np.array([1.0]),
        aggregate_endowment=np.array([1.0, 1.0]),
        excess_demand=np.array([0.0, 0.0]),
        solver_success=True,
        solver_message="malformed cache",
        solver_method="manual",
    )

    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    assert report.classification is CandidateClassification.SOLVER_POINT
    assert not report.checks["finite_values"]
