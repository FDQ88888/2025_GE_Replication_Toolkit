import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    EquilibriumDiagnostics,
    ExchangeEquilibriumSolver,
    SolverConfiguration,
    build_two_by_two_cobb_douglas_benchmark,
)


def test_solver_recovers_analytical_equilibrium() -> None:
    economy, normalization, analytical = (
        build_two_by_two_cobb_douglas_benchmark()
    )
    solver = ExchangeEquilibriumSolver(
        SolverConfiguration(bracket=(0.05, 20.0))
    )

    candidate = solver.solve(economy, normalization)
    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    assert candidate.solver_success
    np.testing.assert_allclose(candidate.prices, analytical.prices, atol=1e-11)
    np.testing.assert_allclose(
        candidate.allocations, analytical.allocations, atol=1e-11
    )
    assert report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert report.passed
    assert report.checks["market_clearing"]
    assert report.checks["walras_law"]


def test_solver_returns_failed_run_without_bracket_sign_change() -> None:
    economy, normalization, _ = build_two_by_two_cobb_douglas_benchmark()
    solver = ExchangeEquilibriumSolver(SolverConfiguration(bracket=(2.0, 3.0)))

    candidate = solver.solve(economy, normalization)
    report = EquilibriumDiagnostics(economy, normalization).evaluate(candidate)

    assert not candidate.solver_success
    assert "No sign change" in candidate.solver_message
    assert report.classification is CandidateClassification.FAILED_RUN


def test_solver_rejects_negative_cobb_douglas_price_bracket() -> None:
    economy, normalization, _ = build_two_by_two_cobb_douglas_benchmark()
    solver = ExchangeEquilibriumSolver(SolverConfiguration(bracket=(-2.0, 3.0)))

    try:
        solver.solve(economy, normalization)
    except ValueError as exc:
        assert "strictly positive" in str(exc)
    else:
        raise AssertionError("Negative Cobb-Douglas prices must not be altered or accepted.")

