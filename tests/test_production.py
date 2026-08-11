import numpy as np
import pytest

from duanmu_ge_lab import (
    CapacityConstrainedLinearTechnology,
    FirmOwnership,
    build_analytical_production_benchmark,
)


def test_capacity_constrained_technology_has_known_global_optimum() -> None:
    technology = CapacityConstrainedLinearTechnology(
        net_output_per_unit=np.array([-1.0, 1.0]), capacity=0.5
    )
    prices = np.array([1.0 / 3.0, 1.0])

    optimum = technology.optimal_plan(prices)
    result = technology.evaluate_optimality(prices, optimum)

    np.testing.assert_allclose(optimum, [-0.5, 0.5], atol=1e-14)
    assert result.feasible
    assert result.candidate_profit == pytest.approx(1.0 / 3.0)
    assert result.optimal_profit == pytest.approx(1.0 / 3.0)
    assert result.profit_gap == pytest.approx(0.0)


def test_firm_profit_optimality_is_homogeneous_under_positive_price_scale() -> None:
    technology = CapacityConstrainedLinearTechnology([-1.0, 1.0], capacity=0.5)
    prices = np.array([1.0 / 3.0, 1.0])
    plan = technology.optimal_plan(prices)

    original = technology.evaluate_optimality(prices, plan)
    scaled = technology.evaluate_optimality(7.0 * prices, plan)

    assert scaled.optimal_plan == pytest.approx(original.optimal_plan)
    assert scaled.candidate_profit == pytest.approx(7.0 * original.candidate_profit)
    assert scaled.optimal_profit == pytest.approx(7.0 * original.optimal_profit)
    assert scaled.profit_gap == pytest.approx(0.0)


def test_capacity_technology_detects_infeasible_plan_and_shutdown_price() -> None:
    technology = CapacityConstrainedLinearTechnology([-1.0, 1.0], capacity=0.5)

    assert technology.feasibility_violation([-0.75, 0.75]) == pytest.approx(0.25)
    np.testing.assert_array_equal(
        technology.optimal_plan(np.array([2.0, 1.0])), np.array([0.0, 0.0])
    )


def test_ownership_is_not_silently_normalized() -> None:
    ownership = FirmOwnership({"Consumer 1": 0.4, "Consumer 2": 0.4})

    assert ownership.total_share == pytest.approx(0.8)
    assert ownership.adding_up_error == pytest.approx(0.2)
    assert sum(ownership.dividends(10.0).values()) == pytest.approx(8.0)


def test_production_benchmark_income_decomposition() -> None:
    economy, _, analytical = build_analytical_production_benchmark()

    incomes = economy.income_breakdowns(
        analytical.prices, analytical.firm_plans
    )

    assert incomes["Consumer 1"].endowment_income == pytest.approx(1.0 / 3.0)
    assert incomes["Consumer 1"].firm_dividend_income == pytest.approx(1.0 / 12.0)
    assert incomes["Consumer 1"].total_income == pytest.approx(5.0 / 12.0)
    assert incomes["Consumer 2"].firm_dividend_income == pytest.approx(1.0 / 4.0)
    assert incomes["Consumer 2"].total_income == pytest.approx(7.0 / 12.0)


def test_candidate_resource_residual_uses_net_production() -> None:
    economy, _, analytical = build_analytical_production_benchmark()

    residual = economy.candidate_resource_residual(
        analytical.allocations, analytical.firm_plans
    )

    np.testing.assert_allclose(residual, [0.0, 0.0], atol=1e-14)
    np.testing.assert_allclose(
        np.sum(analytical.allocations, axis=0), [1.5, 0.5], atol=1e-14
    )
    np.testing.assert_allclose(
        economy.aggregate_endowment() + np.sum(analytical.firm_plans, axis=0),
        [1.5, 0.5],
        atol=1e-14,
    )
