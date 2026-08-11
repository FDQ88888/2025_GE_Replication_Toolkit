import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    Firm,
    FirmOwnership,
    ProductionEconomy,
    ProductionEquilibriumCandidate,
    ProductionEquilibriumDiagnostics,
    ProductionEquilibriumSolver,
    SolverConfiguration,
    build_analytical_production_benchmark,
)


def test_solver_recovers_analytical_production_equilibrium() -> None:
    economy, normalization, analytical = build_analytical_production_benchmark()
    solver = ProductionEquilibriumSolver(
        SolverConfiguration(bracket=(0.1, 0.8))
    )

    candidate = solver.solve(economy, normalization)
    report = ProductionEquilibriumDiagnostics(economy, normalization).evaluate(
        candidate
    )

    assert candidate.solver_success
    np.testing.assert_allclose(candidate.prices, analytical.prices, atol=1e-11)
    np.testing.assert_allclose(
        candidate.allocations, analytical.allocations, atol=1e-11
    )
    np.testing.assert_allclose(
        candidate.firm_plans, analytical.firm_plans, atol=1e-14
    )
    np.testing.assert_allclose(
        candidate.firm_profits, analytical.firm_profits, atol=1e-11
    )
    assert report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert report.passed
    assert all(report.checks.values())


def test_zero_production_can_clear_candidate_resources_but_is_not_optimal() -> None:
    economy, normalization, analytical = build_analytical_production_benchmark()
    prices = analytical.prices
    allocations = np.array([[1.0, 0.0], [1.0, 0.0]])
    firm_plans = np.array([[0.0, 0.0]])
    incomes = economy.income_breakdowns(prices, firm_plans)
    candidate = ProductionEquilibriumCandidate(
        prices=prices,
        allocations=allocations,
        firm_plans=firm_plans,
        aggregate_demand=np.sum(allocations, axis=0),
        aggregate_endowment=economy.aggregate_endowment(),
        aggregate_production=np.sum(firm_plans, axis=0),
        resource_residual=economy.candidate_resource_residual(
            allocations, firm_plans
        ),
        firm_profits=economy.firm_profits(prices, firm_plans),
        income_breakdowns={
            consumer_id: breakdown.to_dict()
            for consumer_id, breakdown in incomes.items()
        },
        solver_success=True,
        solver_message="fabricated zero-production point",
        solver_method="manual",
    )

    report = ProductionEquilibriumDiagnostics(economy, normalization).evaluate(
        candidate
    )

    assert report.checks["market_clearing"]
    assert report.checks["firm_feasibility"]
    assert not report.checks["firm_optimality"]
    assert not report.checks["consumer_optimality"]
    assert report.firm_optimality_results["Conversion firm"].profit_gap == pytest.approx(
        1.0 / 3.0
    )
    assert not report.passed


def test_diagnostics_rejects_ownership_and_dividend_accounting_gap() -> None:
    base_economy, normalization, analytical = build_analytical_production_benchmark()
    original_firm = base_economy.firms[0]
    bad_firm = Firm(
        id=original_firm.id,
        technology=original_firm.technology,
        ownership=FirmOwnership({"Consumer 1": 0.4, "Consumer 2": 0.4}),
    )
    economy = ProductionEconomy(
        commodities=base_economy.commodities,
        consumers=base_economy.consumers,
        firms=(bad_firm,),
    )
    incomes = economy.income_breakdowns(
        analytical.prices, analytical.firm_plans
    )
    candidate = ProductionEquilibriumCandidate(
        prices=analytical.prices,
        allocations=analytical.allocations,
        firm_plans=analytical.firm_plans,
        aggregate_demand=np.sum(analytical.allocations, axis=0),
        aggregate_endowment=economy.aggregate_endowment(),
        aggregate_production=np.sum(analytical.firm_plans, axis=0),
        resource_residual=economy.candidate_resource_residual(
            analytical.allocations, analytical.firm_plans
        ),
        firm_profits=economy.firm_profits(
            analytical.prices, analytical.firm_plans
        ),
        income_breakdowns={
            consumer_id: breakdown.to_dict()
            for consumer_id, breakdown in incomes.items()
        },
        solver_success=True,
        solver_message="bad ownership",
        solver_method="manual",
    )

    report = ProductionEquilibriumDiagnostics(economy, normalization).evaluate(
        candidate
    )

    assert report.ownership_adding_up_errors["Conversion firm"] == pytest.approx(0.2)
    assert not report.checks["ownership_share_adding_up"]
    assert not report.checks["dividend_accounting"]
    assert not report.passed


def test_diagnostics_rejects_nonfinite_nested_income_cache() -> None:
    economy, normalization, _ = build_analytical_production_benchmark()
    candidate = ProductionEquilibriumSolver(
        SolverConfiguration(bracket=(0.1, 0.8))
    ).solve(economy, normalization)
    candidate.income_breakdowns["Consumer 1"]["total_income"] = float("nan")

    report = ProductionEquilibriumDiagnostics(economy, normalization).evaluate(
        candidate
    )

    assert not report.checks["finite_values"]
    assert not report.checks["candidate_cache_consistency"]
    assert not report.passed
