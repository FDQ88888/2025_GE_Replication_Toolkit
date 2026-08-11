import numpy as np
import pytest

from duanmu_ge_lab.equilibrium import (
    FixedNumeraire,
    normalize_l1_signed_price,
    normalize_signed_l1,
)


def test_fixed_numeraire_encode_decode() -> None:
    normalization = FixedNumeraire(index=1, value=1.0)

    full = normalization.decode(np.array([2.0]), n_goods=2)
    independent = normalization.encode(full)

    np.testing.assert_array_equal(full, np.array([2.0, 1.0]))
    np.testing.assert_array_equal(independent, np.array([2.0]))


def test_signed_l1_normalization_preserves_signs() -> None:
    normalized = normalize_signed_l1(np.array([-2.0, 1.0]))

    np.testing.assert_allclose(
        normalized, np.array([-2.0 / 3.0, 1.0 / 3.0]), atol=1e-14
    )


def test_signed_l1_normalization_is_positive_scale_invariant() -> None:
    prices = np.array([-2.0, 1.0])

    np.testing.assert_allclose(
        normalize_l1_signed_price(5.0 * prices),
        normalize_l1_signed_price(prices),
        atol=1e-14,
    )


def test_signed_l1_normalization_rejects_zero_vector() -> None:
    with pytest.raises(ValueError, match="zero price vector"):
        normalize_signed_l1(np.array([0.0, 0.0]))


def test_fixed_numeraire_rejects_dimension_mismatch() -> None:
    normalization = FixedNumeraire(index=1, value=1.0)

    with pytest.raises(ValueError, match="shape"):
        normalization.decode(np.array([1.0, 2.0]), n_goods=2)


def test_fixed_numeraire_encode_uses_tolerance_without_modifying_input() -> None:
    normalization = FixedNumeraire(index=1, value=1.0, tolerance=1e-8)
    prices = np.array([2.0, 1.0 + 5e-9])

    independent = normalization.encode(prices)

    np.testing.assert_array_equal(independent, np.array([2.0]))
    assert prices[1] == 1.0 + 5e-9


def test_fixed_numeraire_encode_rejects_value_outside_tolerance() -> None:
    normalization = FixedNumeraire(index=1, value=1.0, tolerance=1e-8)

    with pytest.raises(ValueError, match="input was not modified"):
        normalization.encode(np.array([2.0, 1.0 + 2e-8]))
