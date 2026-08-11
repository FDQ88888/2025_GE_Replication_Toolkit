"""Explicit consumption sets kept separate from commodity semantic labels."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


class ConsumptionSet(ABC):
    """Abstract numerical feasibility oracle for consumer bundles."""

    @property
    @abstractmethod
    def n_goods(self) -> int:
        """Return the commodity dimension."""

    @abstractmethod
    def feasibility_violation(
        self, bundle: Sequence[float] | FloatArray
    ) -> float:
        """Return zero on the represented set and a positive violation outside it."""


@dataclass(frozen=True, slots=True)
class NonnegativeOrthant(ConsumptionSet):
    """The default consumption set ``R_+^L``."""

    dimension: int

    def __post_init__(self) -> None:
        if self.dimension < 1:
            raise ValueError("Consumption-set dimension must be positive.")

    @property
    def n_goods(self) -> int:
        """Return the commodity dimension."""

        return self.dimension

    def feasibility_violation(
        self, bundle: Sequence[float] | FloatArray
    ) -> float:
        """Return the maximum nonnegativity violation."""

        array = self._validated_bundle(bundle)
        return float(np.max(np.maximum(-array, 0.0), initial=0.0))

    def _validated_bundle(
        self, bundle: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(bundle, dtype=float)
        if array.shape != (self.n_goods,):
            raise ValueError(
                f"Bundle must have shape ({self.n_goods},), got {array.shape}."
            )
        if not np.all(np.isfinite(array)):
            raise ValueError("Bundle must contain only finite values.")
        return array


@dataclass(frozen=True, slots=True)
class BoxConsumptionSet(ConsumptionSet):
    """Coordinate bounds, including fixed-zero or bounded bad absorption."""

    lower_bounds: Sequence[float] | FloatArray
    upper_bounds: Sequence[float] | FloatArray

    def __post_init__(self) -> None:
        lower = np.asarray(self.lower_bounds, dtype=float)
        upper = np.asarray(self.upper_bounds, dtype=float)
        if lower.ndim != 1 or lower.size == 0 or upper.shape != lower.shape:
            raise ValueError("Consumption bounds must be non-empty matching 1D vectors.")
        if not np.all(np.isfinite(lower)):
            raise ValueError("Lower consumption bounds must be finite.")
        if np.any(np.isnan(upper)) or np.any(upper == -np.inf):
            raise ValueError("Upper bounds may be finite or positive infinity only.")
        if np.any(lower > upper):
            raise ValueError("Every lower consumption bound must not exceed its upper bound.")
        object.__setattr__(self, "lower_bounds", lower.copy())
        object.__setattr__(self, "upper_bounds", upper.copy())

    @property
    def n_goods(self) -> int:
        """Return the commodity dimension."""

        return int(np.asarray(self.lower_bounds).size)

    def feasibility_violation(
        self, bundle: Sequence[float] | FloatArray
    ) -> float:
        """Return the maximum lower- or upper-bound violation."""

        array = np.asarray(bundle, dtype=float)
        if array.shape != (self.n_goods,):
            raise ValueError(
                f"Bundle must have shape ({self.n_goods},), got {array.shape}."
            )
        if not np.all(np.isfinite(array)):
            raise ValueError("Bundle must contain only finite values.")
        lower_error = np.maximum(np.asarray(self.lower_bounds) - array, 0.0)
        upper_error = np.maximum(array - np.asarray(self.upper_bounds), 0.0)
        return float(max(np.max(lower_error), np.max(upper_error)))
