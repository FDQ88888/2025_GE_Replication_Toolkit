import numpy as np
import pytest

from duanmu_ge_lab.core import (
    CobbDouglasUtility,
    UnsupportedPriceDomainError,
)


def test_cobb_douglas_closed_form_demand() -> None:
    preference = CobbDouglasUtility(np.array([0.5, 0.5]))

    demand = preference.marshallian_demand(np.array([1.0, 1.0]), wealth=2.0)

    np.testing.assert_allclose(demand, np.array([1.0, 1.0]), atol=1e-14)


@pytest.mark.parametrize(
    "alphas",
    [
        np.array([-0.1, 1.1]),
        np.array([0.4, 0.4]),
        np.array([0.0, 1.0]),
        np.array([np.nan, np.nan]),
    ],
)
def test_cobb_douglas_rejects_invalid_alphas(alphas: np.ndarray) -> None:
    with pytest.raises(ValueError):
        CobbDouglasUtility(alphas)


@pytest.mark.parametrize(
    "prices",
    [np.array([0.0, 1.0]), np.array([-1.0, 1.0])],
)
def test_cobb_douglas_rejects_unsupported_price_domain(
    prices: np.ndarray,
) -> None:
    preference = CobbDouglasUtility(np.array([0.5, 0.5]))

    with pytest.raises(UnsupportedPriceDomainError, match="strictly positive"):
        preference.marshallian_demand(prices, wealth=1.0)


def test_cobb_douglas_rejects_dimension_mismatch() -> None:
    preference = CobbDouglasUtility(np.array([0.5, 0.5]))

    with pytest.raises(ValueError, match="shape"):
        preference.marshallian_demand(np.array([1.0]), wealth=1.0)

