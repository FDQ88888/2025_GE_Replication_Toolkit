"""Price-coordinate normalizations kept separate from price-sign restrictions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


class PriceNormalization(ABC):
    """Abstract mapping between independent and full price coordinates."""

    @abstractmethod
    def encode(self, full_prices: Sequence[float] | FloatArray) -> FloatArray:
        """Remove normalization-fixed coordinates from a full price vector."""

    @abstractmethod
    def decode(
        self, independent_prices: Sequence[float] | FloatArray, n_goods: int
    ) -> FloatArray:
        """Construct a full price vector from independent coordinates."""


@dataclass(frozen=True, slots=True)
class FixedNumeraire(PriceNormalization):
    """Fix one price coordinate as a numerical numeraire.

    Economic interpretation
        This is an OUR COMPUTATIONAL CHOICE. It selects coordinates for relative
        prices and does not impose a universal economic sign restriction.
    Mathematical definition
        ``p[index] = value``; all other price coordinates remain independent.
    Parameters
        index: Zero-based numeraire commodity index.
        value: Finite nonzero numeraire value.
        tolerance: Absolute comparison tolerance used by ``encode``.
    Raises
        ValueError: If configuration, dimensions, or fixed coordinates are invalid.
    """

    index: int
    value: float
    tolerance: float = 1e-12

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("Numeraire index must be nonnegative.")
        if not np.isfinite(self.value) or self.value == 0.0:
            raise ValueError("Numeraire value must be finite and nonzero.")
        if not np.isfinite(self.tolerance) or self.tolerance <= 0.0:
            raise ValueError("Numeraire tolerance must be finite and positive.")

    def encode(self, full_prices: Sequence[float] | FloatArray) -> FloatArray:
        """Remove the fixed numeraire coordinate from normalized full prices.

        Parameters
            full_prices: Full finite vector whose numeraire equals ``value``.
        Returns
            Independent price coordinates in their original order.
        Raises
            ValueError: If shape, finiteness, index, or normalization is invalid.
        """

        prices = np.asarray(full_prices, dtype=float)
        if prices.ndim != 1 or prices.size == 0:
            raise ValueError("Full prices must be a non-empty 1D vector.")
        if self.index >= prices.size:
            raise ValueError("Numeraire index is outside the full price vector.")
        if not np.all(np.isfinite(prices)):
            raise ValueError("Full prices must contain only finite values.")
        if not np.isclose(
            prices[self.index], self.value, atol=self.tolerance, rtol=0.0
        ):
            raise ValueError(
                f"Expected numeraire price {self.value} within absolute tolerance "
                f"{self.tolerance}, got {prices[self.index]}; the input was not "
                "modified."
            )
        return np.delete(prices, self.index)

    def decode(
        self, independent_prices: Sequence[float] | FloatArray, n_goods: int
    ) -> FloatArray:
        """Insert the fixed numeraire into independent price coordinates.

        Parameters
            independent_prices: Vector with ``n_goods - 1`` finite coordinates.
            n_goods: Dimension of the full commodity space.
        Returns
            Full price vector with ``p[index] = value``.
        Raises
            ValueError: If dimensions, index, or values are invalid.
        """

        if n_goods < 1:
            raise ValueError("n_goods must be positive.")
        if self.index >= n_goods:
            raise ValueError("Numeraire index is outside the commodity dimension.")
        independent = np.asarray(independent_prices, dtype=float)
        if independent.shape != (n_goods - 1,):
            raise ValueError(
                f"Independent prices must have shape ({n_goods - 1},), "
                f"got {independent.shape}."
            )
        if not np.all(np.isfinite(independent)):
            raise ValueError("Independent prices must contain only finite values.")
        return np.insert(independent, self.index, self.value).astype(float)


def normalize_signed_l1(prices: Sequence[float] | FloatArray) -> FloatArray:
    """Normalize a nonzero signed price vector by its L1 norm.

    Economic interpretation
        This reporting normalization matches the signed price convention used in the
        Duanmu-related general-equilibrium papers. It preserves every price sign.
    Mathematical definition
        ``p_normalized = p / sum_l abs(p_l)``.
    Parameters
        prices: Finite, nonzero, one-dimensional signed price vector.
    Returns
        Signed L1-normalized price vector.
    Raises
        ValueError: If the vector is empty, nonfinite, not one-dimensional, or zero.
    """

    price_array = np.asarray(prices, dtype=float)
    if price_array.ndim != 1 or price_array.size == 0:
        raise ValueError("Prices must be a non-empty 1D vector.")
    if not np.all(np.isfinite(price_array)):
        raise ValueError("Prices must contain only finite values.")
    norm = float(np.sum(np.abs(price_array)))
    if norm == 0.0:
        raise ValueError("Cannot L1-normalize the zero price vector.")
    return price_array / norm


def normalize_l1_signed_price(
    prices: Sequence[float] | FloatArray,
) -> FloatArray:
    """Compatibility name for :func:`normalize_signed_l1`."""

    return normalize_signed_l1(prices)
