"""Preference interfaces and the Milestone 1 Cobb-Douglas implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


class UnsupportedPriceDomainError(ValueError):
    """Raised when a preference-specific demand formula does not support the prices."""


class PreferenceModel(ABC):
    """Abstract interface for a numerically represented consumer preference."""

    @property
    def has_unique_marshallian_demand(self) -> bool:
        """Whether the implemented demand oracle is known to be single-valued.

        Bundle-distance diagnostics are meaningful only when this property is true.
        General optimality verification must use utility values instead.
        """

        return False

    @property
    @abstractmethod
    def n_goods(self) -> int:
        """Return the number of commodity coordinates accepted by the model."""

    @abstractmethod
    def validate(self) -> None:
        """Validate the preference parameters and raise a clear error if invalid."""

    @abstractmethod
    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        """Evaluate the numerical preference representation at a consumption bundle."""

    @abstractmethod
    def marshallian_demand(
        self, prices: Sequence[float] | FloatArray, wealth: float
    ) -> FloatArray:
        """Return Marshallian demand in the price domain supported by the model."""


@dataclass(frozen=True, slots=True)
class CobbDouglasUtility(PreferenceModel):
    """Cobb-Douglas preference used as a software-validation benchmark.

    Economic interpretation
        This is an OUR COMPUTATIONAL CHOICE for Milestone 1. It is not the general
        preference relation used in Anderson-Duanmu models.
    Mathematical definition
        ``u(x) = product_l x_l ** alpha_l`` with every ``alpha_l > 0`` and
        ``sum_l alpha_l = 1``. For strictly positive prices, Marshallian demand is
        ``x_l = alpha_l * wealth / p_l``.
    Parameters
        alphas: Positive expenditure shares summing to one.
    Returns
        Utility values or closed-form Marshallian demand, depending on the method.
    Raises
        ValueError: If parameters, dimensions, bundles, or wealth are invalid.
        UnsupportedPriceDomainError: If any price is zero or negative. The method
        never takes absolute values, clips prices, or changes the economic model.
    """

    alphas: Sequence[float] | FloatArray

    def __post_init__(self) -> None:
        alpha_array = np.asarray(self.alphas, dtype=float)
        object.__setattr__(self, "alphas", alpha_array.copy())
        self.validate()

    @property
    def n_goods(self) -> int:
        """Return the number of Cobb-Douglas commodity shares."""

        return int(np.asarray(self.alphas).size)

    @property
    def has_unique_marshallian_demand(self) -> bool:
        """Return true for the strictly positive-price benchmark domain."""

        return True

    def validate(self) -> None:
        """Validate positivity, finiteness, dimensionality, and adding-up."""

        alphas = np.asarray(self.alphas, dtype=float)
        if alphas.ndim != 1 or alphas.size == 0:
            raise ValueError("Cobb-Douglas alphas must be a non-empty 1D vector.")
        if not np.all(np.isfinite(alphas)):
            raise ValueError("Cobb-Douglas alphas must be finite.")
        if np.any(alphas <= 0.0):
            raise ValueError("Every Cobb-Douglas alpha must be strictly positive.")
        if not np.isclose(float(np.sum(alphas)), 1.0, atol=1e-12, rtol=0.0):
            raise ValueError("Cobb-Douglas alphas must sum to one.")

    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        """Evaluate ``product_l x_l ** alpha_l``.

        Parameters
            bundle: Nonnegative consumption vector with the same dimension as alphas.
        Returns
            Cobb-Douglas utility as a finite float when representable.
        Raises
            ValueError: If the bundle has the wrong shape, is nonfinite, or is negative.
        """

        quantities = np.asarray(bundle, dtype=float)
        if quantities.shape != (self.n_goods,):
            raise ValueError(
                f"Bundle must have shape ({self.n_goods},), got {quantities.shape}."
            )
        if not np.all(np.isfinite(quantities)):
            raise ValueError("Consumption bundle must contain only finite values.")
        if np.any(quantities < 0.0):
            raise ValueError("Cobb-Douglas consumption must be nonnegative.")
        return float(np.prod(np.power(quantities, np.asarray(self.alphas))))

    def marshallian_demand(
        self, prices: Sequence[float] | FloatArray, wealth: float
    ) -> FloatArray:
        """Compute closed-form Cobb-Douglas Marshallian demand.

        Economic interpretation
            The consumer spends share ``alpha_l`` of wealth on commodity ``l``.
        Mathematical definition
            ``x_l = alpha_l * wealth / p_l`` for strictly positive prices.
        Parameters
            prices: Strictly positive finite price vector.
            wealth: Finite, nonnegative budget wealth.
        Returns
            The unique closed-form demand vector in this supported domain.
        Raises
            ValueError: For dimension, finiteness, or negative-wealth errors.
            UnsupportedPriceDomainError: If at least one price is nonpositive.
        """

        price_array = np.asarray(prices, dtype=float)
        if price_array.shape != (self.n_goods,):
            raise ValueError(
                f"Prices must have shape ({self.n_goods},), got {price_array.shape}."
            )
        if not np.all(np.isfinite(price_array)):
            raise ValueError("Prices must contain only finite values.")
        if np.any(price_array <= 0.0):
            raise UnsupportedPriceDomainError(
                "Closed-form Cobb-Douglas demand requires every price to be "
                "strictly positive; prices are never clipped or replaced."
            )
        if not np.isfinite(wealth) or wealth < 0.0:
            raise ValueError("Wealth must be finite and nonnegative.")
        return np.asarray(self.alphas, dtype=float) * float(wealth) / price_array


@dataclass(frozen=True, slots=True)
class BadAbsorptionLinearUtility(PreferenceModel):
    """Two-coordinate utility ``u(b,g)=g-d*b`` with bounded bad absorption.

    This is an OUR COMPUTATIONAL CHOICE for the signed-price accounting benchmark.
    Coordinate 0 is a nonnegative absorbed bad bounded by ``max_bad``; coordinate 1
    is a nonnegative ordinary good. The demand formula supports ``p_bad<0<p_good``
    and never changes price signs.
    """

    bad_disutility: float
    max_bad: float

    def __post_init__(self) -> None:
        self.validate()

    @property
    def n_goods(self) -> int:
        """Return the fixed bad/good dimension two."""

        return 2

    def validate(self) -> None:
        """Validate finite positive disutility and absorption capacity."""

        if not np.isfinite(self.bad_disutility) or self.bad_disutility <= 0.0:
            raise ValueError("Bad disutility must be finite and positive.")
        if not np.isfinite(self.max_bad) or self.max_bad <= 0.0:
            raise ValueError("Maximum bad absorption must be finite and positive.")

    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        """Evaluate linear good utility net of bad-absorption disutility."""

        array = np.asarray(bundle, dtype=float)
        if array.shape != (2,) or not np.all(np.isfinite(array)):
            raise ValueError("Bad/good bundle must be a finite vector of shape (2,).")
        bad, good = array
        if bad < 0.0 or bad > self.max_bad or good < 0.0:
            raise ValueError("Bundle is outside the bounded bad-absorption domain.")
        return float(good - self.bad_disutility * bad)

    def marshallian_demand(
        self, prices: Sequence[float] | FloatArray, wealth: float
    ) -> FloatArray:
        """Solve the bounded linear budget problem at a negative bad price."""

        price_array = np.asarray(prices, dtype=float)
        if price_array.shape != (2,) or not np.all(np.isfinite(price_array)):
            raise ValueError("Bad/good prices must be a finite vector of shape (2,).")
        bad_price, good_price = price_array
        if bad_price >= 0.0 or good_price <= 0.0:
            raise UnsupportedPriceDomainError(
                "Bad-absorption demand requires p_bad < 0 < p_good; prices are "
                "never clipped, absolutized, or replaced."
            )
        if not np.isfinite(wealth):
            raise ValueError("Wealth must be finite.")
        minimum_bad = max(0.0, float(wealth / bad_price))
        if minimum_bad > self.max_bad:
            raise ValueError("The budget set is empty within the bad-absorption bound.")
        marginal_value = -bad_price / good_price - self.bad_disutility
        bad = self.max_bad if marginal_value > 0.0 else minimum_bad
        good = (wealth - bad_price * bad) / good_price
        if good < -1e-12:
            raise ArithmeticError("Computed demand violates nonnegative good consumption.")
        return np.array([bad, max(0.0, float(good))], dtype=float)


@dataclass(frozen=True, slots=True)
class SingleGoodLinearUtility(PreferenceModel):
    """Linear own-consumption utility for one desired commodity.

    The model represents the own-demand part of paper examples in which some
    coordinates are fixed at zero by the consumption set and the consumer spends
    all income on one positively priced good. Aggregate externality terms are kept
    outside this oracle because they are constant in the consumer's own choice.
    """

    dimension: int
    desired_good_index: int
    fixed_zero_indexes: Sequence[int] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "fixed_zero_indexes", tuple(self.fixed_zero_indexes))
        self.validate()

    @property
    def n_goods(self) -> int:
        """Return the configured commodity dimension."""

        return self.dimension

    def validate(self) -> None:
        """Validate dimensions and fixed-zero coordinates."""

        if self.dimension < 1:
            raise ValueError("Single-good utility dimension must be positive.")
        if not 0 <= self.desired_good_index < self.dimension:
            raise ValueError("Desired-good index is outside the commodity dimension.")
        fixed = tuple(self.fixed_zero_indexes)
        if len(fixed) != len(set(fixed)):
            raise ValueError("Fixed-zero indexes must be unique.")
        if any(index < 0 or index >= self.dimension for index in fixed):
            raise ValueError("A fixed-zero index is outside the commodity dimension.")
        if self.desired_good_index in fixed:
            raise ValueError("The desired good cannot also be fixed at zero.")

    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        """Return consumption of the desired commodity."""

        array = np.asarray(bundle, dtype=float)
        if array.shape != (self.n_goods,) or not np.all(np.isfinite(array)):
            raise ValueError(
                f"Bundle must be a finite vector of shape ({self.n_goods},)."
            )
        if np.any(array < 0.0):
            raise ValueError("Single-good linear utility requires nonnegative bundles.")
        if any(array[index] != 0.0 for index in self.fixed_zero_indexes):
            raise ValueError("Bundle violates a fixed-zero consumption coordinate.")
        return float(array[self.desired_good_index])

    def marshallian_demand(
        self, prices: Sequence[float] | FloatArray, wealth: float
    ) -> FloatArray:
        """Spend all nonnegative wealth on the desired commodity."""

        price_array = np.asarray(prices, dtype=float)
        if price_array.shape != (self.n_goods,) or not np.all(np.isfinite(price_array)):
            raise ValueError(
                f"Prices must be a finite vector of shape ({self.n_goods},)."
            )
        desired_price = float(price_array[self.desired_good_index])
        if desired_price <= 0.0:
            raise UnsupportedPriceDomainError(
                "Single-good demand requires a strictly positive desired-good price."
            )
        unrestricted_indexes = set(range(self.n_goods)) - set(self.fixed_zero_indexes)
        unrestricted_indexes.remove(self.desired_good_index)
        if any(price_array[index] < 0.0 for index in unrestricted_indexes):
            raise UnsupportedPriceDomainError(
                "A negative-priced, non-fixed indifferent commodity makes the "
                "single-good demand problem unbounded."
            )
        if not np.isfinite(wealth) or wealth < 0.0:
            raise ValueError("Single-good demand wealth must be finite and nonnegative.")
        demand = np.zeros(self.n_goods, dtype=float)
        demand[self.desired_good_index] = float(wealth) / desired_price
        return demand


@dataclass(frozen=True, slots=True)
class Example3Utility(PreferenceModel):
    """Strictly concave utility and closed-form demand from paper Example 3.

    ``agent=1`` represents ``x1-(1/8)x2^-8-(1/10)x0^2`` and ``agent=2``
    represents ``x2-(1/8)x1^-8-(1/2)x0^2``. The oracle supports the paper domain
    ``p0<=0<p1,p2`` and uses total budget income including the tax rebate.
    """

    agent: int

    def __post_init__(self) -> None:
        self.validate()

    @property
    def n_goods(self) -> int:
        return 3

    @property
    def has_unique_marshallian_demand(self) -> bool:
        return True

    def validate(self) -> None:
        if self.agent not in (1, 2):
            raise ValueError("Example 3 utility agent must be 1 or 2.")

    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        array = np.asarray(bundle, dtype=float)
        if array.shape != (3,) or not np.all(np.isfinite(array)):
            raise ValueError("Example 3 bundle must be a finite vector of shape (3,).")
        if np.any(array < 0.0):
            raise ValueError("Example 3 consumption must be nonnegative.")
        x0, x1, x2 = array
        if (self.agent == 1 and x2 <= 0.0) or (
            self.agent == 2 and x1 <= 0.0
        ):
            return float("-inf")
        if self.agent == 1:
            return float(x1 - 0.125 * x2 ** (-8.0) - 0.1 * x0**2)
        return float(x2 - 0.125 * x1 ** (-8.0) - 0.5 * x0**2)

    def marshallian_demand(
        self, prices: Sequence[float] | FloatArray, wealth: float
    ) -> FloatArray:
        price_array = np.asarray(prices, dtype=float)
        if price_array.shape != (3,) or not np.all(np.isfinite(price_array)):
            raise ValueError("Example 3 prices must be a finite vector of shape (3,).")
        p0, p1, p2 = price_array
        if p0 > 0.0 or p1 <= 0.0 or p2 <= 0.0:
            raise UnsupportedPriceDomainError(
                "Example 3 demand requires p0<=0<p1,p2."
            )
        if not np.isfinite(wealth):
            raise ValueError("Example 3 wealth must be finite.")
        if self.agent == 1:
            x0 = -5.0 * p0 / p1
            x2 = (p1 / p2) ** (1.0 / 9.0)
            x1 = (wealth - p0 * x0 - p2 * x2) / p1
        else:
            x0 = -p0 / p2
            x1 = (p2 / p1) ** (1.0 / 9.0)
            x2 = (wealth - p0 * x0 - p1 * x1) / p2
        demand = np.array([x0, x1, x2], dtype=float)
        if np.any(demand < -1e-12):
            raise ValueError("Example 3 closed-form demand leaves R_+^3.")
        return np.maximum(demand, 0.0)
