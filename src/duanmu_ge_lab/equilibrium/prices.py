"""Explicit signed-price restrictions, separate from price normalization."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.equilibrium.normalization import FixedNumeraire

FloatArray = NDArray[np.float64]


class PriceSign(str, Enum):
    """Coordinate-level sign restrictions chosen by an economic specification."""

    ANY = "any"
    NONNEGATIVE = "nonnegative"
    NONPOSITIVE = "nonpositive"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ZERO = "zero"


@dataclass(frozen=True, slots=True)
class PriceSignRestrictions:
    """A price-sign region that is not inferred from commodity metadata."""

    signs: Sequence[PriceSign]

    def __post_init__(self) -> None:
        converted = tuple(PriceSign(sign) for sign in self.signs)
        if not converted:
            raise ValueError("Price-sign restrictions must be non-empty.")
        object.__setattr__(self, "signs", converted)

    @property
    def n_goods(self) -> int:
        """Return the price dimension."""

        return len(self.signs)

    def violations(
        self,
        prices: Sequence[float] | FloatArray,
        strict_tolerance: float = 1e-12,
    ) -> FloatArray:
        """Return coordinate violations without modifying any price."""

        array = np.asarray(prices, dtype=float)
        if array.shape != (self.n_goods,) or not np.all(np.isfinite(array)):
            raise ValueError(
                f"Prices must be a finite vector of shape ({self.n_goods},)."
            )
        if not np.isfinite(strict_tolerance) or strict_tolerance <= 0.0:
            raise ValueError("Strict sign tolerance must be finite and positive.")
        result = np.zeros(self.n_goods, dtype=float)
        for index, (price, sign) in enumerate(zip(array, self.signs, strict=True)):
            if sign is PriceSign.ANY:
                result[index] = 0.0
            elif sign is PriceSign.NONNEGATIVE:
                result[index] = max(0.0, -float(price))
            elif sign is PriceSign.NONPOSITIVE:
                result[index] = max(0.0, float(price))
            elif sign is PriceSign.POSITIVE:
                result[index] = max(0.0, strict_tolerance - float(price))
            elif sign is PriceSign.NEGATIVE:
                result[index] = max(0.0, float(price) + strict_tolerance)
            else:
                result[index] = abs(float(price))
        return result

    def max_violation(
        self,
        prices: Sequence[float] | FloatArray,
        strict_tolerance: float = 1e-12,
    ) -> float:
        """Return the largest coordinate sign violation."""

        return float(np.max(self.violations(prices, strict_tolerance)))

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable restriction names."""

        return {"signs": [sign.value for sign in self.signs]}


def rescale_to_fixed_numeraire(
    prices: Sequence[float] | FloatArray,
    normalization: FixedNumeraire,
) -> FloatArray:
    """Apply a positive scale so one coordinate equals a fixed numeraire.

    A negative scale would reverse every price sign and is rejected. The input is
    never clipped, absolutized, or modified.
    """

    array = np.asarray(prices, dtype=float)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("Prices must be a non-empty finite 1D vector.")
    if normalization.index >= array.size:
        raise ValueError("Numeraire index is outside the price vector.")
    coordinate = float(array[normalization.index])
    if coordinate == 0.0:
        raise ValueError("Cannot rescale a zero numeraire coordinate.")
    scale = normalization.value / coordinate
    if scale <= 0.0:
        raise ValueError(
            "Fixed numeraire requires a positive scale; requested value has an "
            "incompatible sign."
        )
    result = scale * array
    normalization.encode(result)
    return result
