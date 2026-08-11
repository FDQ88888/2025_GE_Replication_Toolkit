import numpy as np
import pytest

from duanmu_ge_lab import build_two_by_two_cobb_douglas_benchmark


def test_walras_law_holds_even_away_from_market_clearing() -> None:
    economy, _, _ = build_two_by_two_cobb_douglas_benchmark()
    prices = np.array([2.0, 1.0])

    residuals = economy.excess_demand(prices)
    walras_value = economy.walras_residual(prices)

    assert residuals[0] == pytest.approx(-0.25)
    assert residuals[1] == pytest.approx(0.5)
    assert walras_value == pytest.approx(0.0, abs=1e-14)

