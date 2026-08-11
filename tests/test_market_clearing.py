import numpy as np

from duanmu_ge_lab import build_two_by_two_cobb_douglas_benchmark


def test_benchmark_markets_clear_at_analytical_price() -> None:
    economy, _, analytical = build_two_by_two_cobb_douglas_benchmark()

    residuals = economy.market_residuals(analytical.prices)

    np.testing.assert_allclose(residuals, np.array([0.0, 0.0]), atol=1e-14)


def test_excess_demand_sign_is_demand_minus_endowment() -> None:
    economy, _, _ = build_two_by_two_cobb_douglas_benchmark()

    residuals = economy.market_residuals(np.array([2.0, 1.0]))

    np.testing.assert_allclose(residuals, np.array([-0.25, 0.5]), atol=1e-14)

