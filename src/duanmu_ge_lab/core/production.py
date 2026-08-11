"""Firm ownership and production technologies under a net-output convention."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.numerics import (
    PROFIT_MARGIN_ABS_TOL,
    PROFIT_MARGIN_REL_TOL,
)

FloatArray = NDArray[np.float64]


class UnboundedProfitError(ValueError):
    """Raised when a represented production set has unbounded positive profit."""


class ProfitMarginRegime(str, Enum):
    """Numerically resolved sign of a linear activity's unit profit."""

    NEGATIVE_SHUTDOWN = "NEGATIVE_SHUTDOWN"
    NUMERICAL_ZERO = "NUMERICAL_ZERO"
    POSITIVE_UNBOUNDED = "POSITIVE_UNBOUNDED"


@dataclass(frozen=True, slots=True)
class ProfitMarginAssessment:
    """Scale-aware sign assessment for ``p dot v``."""

    margin: float
    scale: float
    tolerance: float
    regime: ProfitMarginRegime

    def to_dict(self) -> dict[str, Any]:
        return {
            "margin": self.margin,
            "scale_l2_product": self.scale,
            "effective_zero_tolerance": self.tolerance,
            "regime": self.regime.value,
        }


@dataclass(frozen=True, slots=True)
class FirmOwnership:
    """Consumer shares in one firm.

    Shares are finite and nonnegative. They are deliberately not normalized here:
    the independent diagnostics must detect a failure to add up to one.
    """

    shares: Mapping[str, float]

    def __post_init__(self) -> None:
        copied = dict(self.shares)
        if not copied:
            raise ValueError("Firm ownership must name at least one consumer.")
        for consumer_id, share in copied.items():
            if not consumer_id.strip():
                raise ValueError("Ownership consumer ids must be non-empty.")
            if not np.isfinite(share) or share < 0.0:
                raise ValueError("Ownership shares must be finite and nonnegative.")
        object.__setattr__(self, "shares", MappingProxyType(copied))

    @property
    def total_share(self) -> float:
        """Return the raw, unweighted share sum without normalizing it.

        A weighted economy must instead evaluate ``sum_i lambda_i theta_ij`` with
        its own population masses.
        """

        return float(sum(self.shares.values()))

    @property
    def adding_up_error(self) -> float:
        """Return ``abs(sum_i theta_ij - 1)``."""

        return abs(self.total_share - 1.0)

    def share_of(self, consumer_id: str) -> float:
        """Return a consumer's share, treating an omitted owner as zero."""

        return float(self.shares.get(consumer_id, 0.0))

    def dividends(self, profit: float) -> dict[str, float]:
        """Distribute a firm's signed profit according to unmodified shares."""

        if not np.isfinite(profit):
            raise ValueError("Firm profit must be finite.")
        return {
            consumer_id: float(share * profit)
            for consumer_id, share in self.shares.items()
        }

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable ownership data."""

        return {
            "shares": dict(self.shares),
            "raw_total_share_not_population_weighted": self.total_share,
            "raw_adding_up_error_not_population_weighted": self.adding_up_error,
        }


@dataclass(frozen=True, slots=True)
class FirmOptimalityResult:
    """Independent feasibility and profit-maximization assessment."""

    feasible: bool
    candidate_profit: float
    optimal_profit: float
    profit_gap: float
    feasibility_violation: float
    method: str
    optimal_plan: list[float]
    profit_margin_assessment: ProfitMarginAssessment | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable result data."""

        result = {
            "feasible": self.feasible,
            "candidate_profit": self.candidate_profit,
            "optimal_profit": self.optimal_profit,
            "profit_gap": self.profit_gap,
            "feasibility_violation": self.feasibility_violation,
            "method": self.method,
            "optimal_plan": list(self.optimal_plan),
        }
        if self.profit_margin_assessment is not None:
            result["profit_margin_assessment"] = (
                self.profit_margin_assessment.to_dict()
            )
        return result


class ProductionTechnology(ABC):
    """Abstract feasible set and profit oracle for net production vectors."""

    @property
    @abstractmethod
    def n_goods(self) -> int:
        """Return the number of net-output coordinates."""

    @abstractmethod
    def feasibility_violation(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Return zero exactly on the represented production set."""

    @abstractmethod
    def optimal_plan(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return one independently computed profit-maximizing plan."""

    def profit(
        self,
        prices: Sequence[float] | FloatArray,
        plan: Sequence[float] | FloatArray,
    ) -> float:
        """Return ``p dot y`` under the project net-output convention."""

        price_array = self._validated_prices(prices)
        plan_array = self._validated_plan(plan)
        return float(np.dot(price_array, plan_array))

    def evaluate_optimality(
        self,
        prices: Sequence[float] | FloatArray,
        candidate_plan: Sequence[float] | FloatArray,
    ) -> FirmOptimalityResult:
        """Compare candidate profit with an independent global profit oracle."""

        price_array = self._validated_prices(prices)
        plan_array = self._validated_plan(candidate_plan)
        violation = self.feasibility_violation(plan_array)
        optimum = self.optimal_plan(price_array)
        candidate_profit = self.profit(price_array, plan_array)
        optimal_profit = self.profit(price_array, optimum)
        return FirmOptimalityResult(
            feasible=violation == 0.0,
            candidate_profit=candidate_profit,
            optimal_profit=optimal_profit,
            profit_gap=optimal_profit - candidate_profit,
            feasibility_violation=violation,
            method=f"{type(self).__name__}.global_profit_oracle",
            optimal_plan=optimum.tolist(),
        )

    def _validated_prices(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(prices, dtype=float)
        if array.shape != (self.n_goods,):
            raise ValueError(
                f"Prices must have shape ({self.n_goods},), got {array.shape}."
            )
        if not np.all(np.isfinite(array)):
            raise ValueError("Prices must contain only finite values.")
        return array

    def _validated_plan(
        self, plan: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(plan, dtype=float)
        if array.shape != (self.n_goods,):
            raise ValueError(
                f"Production plan must have shape ({self.n_goods},), "
                f"got {array.shape}."
            )
        if not np.all(np.isfinite(array)):
            raise ValueError("Production plan must contain only finite values.")
        return array


@dataclass(frozen=True, slots=True)
class CapacityConstrainedLinearTechnology(ProductionTechnology):
    """Bounded one-activity technology ``Y={a*v: 0<=a<=capacity}``.

    This is an OUR COMPUTATIONAL CHOICE for the analytical production benchmark.
    Positive net-output coordinates are outputs and negative coordinates are inputs.
    The bounded activity gives a finite global profit maximum at every finite price.
    """

    net_output_per_unit: Sequence[float] | FloatArray
    capacity: float

    def __post_init__(self) -> None:
        vector = np.asarray(self.net_output_per_unit, dtype=float)
        if vector.ndim != 1 or vector.size == 0:
            raise ValueError("Net output per unit must be a non-empty 1D vector.")
        if not np.all(np.isfinite(vector)) or np.all(vector == 0.0):
            raise ValueError("Net output per unit must be finite and nonzero.")
        if not np.isfinite(self.capacity) or self.capacity <= 0.0:
            raise ValueError("Production capacity must be finite and positive.")
        object.__setattr__(self, "net_output_per_unit", vector.copy())

    @property
    def n_goods(self) -> int:
        """Return the net-output dimension."""

        return int(np.asarray(self.net_output_per_unit).size)

    def activity_level(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Return the least-squares activity coordinate of a candidate plan."""

        plan_array = self._validated_plan(plan)
        vector = np.asarray(self.net_output_per_unit)
        return float(np.dot(plan_array, vector) / np.dot(vector, vector))

    def feasibility_violation(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Measure ray-membership and activity-bound violations."""

        plan_array = self._validated_plan(plan)
        vector = np.asarray(self.net_output_per_unit)
        activity = self.activity_level(plan_array)
        ray_error = float(np.max(np.abs(plan_array - activity * vector)))
        return max(ray_error, max(0.0, -activity), max(0.0, activity - self.capacity))

    def optimal_plan(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return capacity production for positive margin and shutdown otherwise."""

        price_array = self._validated_prices(prices)
        vector = np.asarray(self.net_output_per_unit)
        unit_margin = float(np.dot(price_array, vector))
        activity = self.capacity if unit_margin > 0.0 else 0.0
        return activity * vector


@dataclass(frozen=True, slots=True)
class ZeroTechnology(ProductionTechnology):
    """Singleton production set ``Y={0}``, used by the government firm."""

    dimension: int

    def __post_init__(self) -> None:
        if self.dimension < 1:
            raise ValueError("Zero-technology dimension must be positive.")

    @property
    def n_goods(self) -> int:
        """Return the commodity dimension."""

        return self.dimension

    def feasibility_violation(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Return the largest absolute coordinate of the candidate plan."""

        array = self._validated_plan(plan)
        return float(np.max(np.abs(array), initial=0.0))

    def optimal_plan(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return the unique zero production plan."""

        self._validated_prices(prices)
        return np.zeros(self.n_goods, dtype=float)


@dataclass(frozen=True, slots=True)
class LinearRayTechnology(ProductionTechnology):
    """Unbounded one-activity technology ``Y={a*v:a>=0}``.

    A scale-aware sign test classifies ``p dot v`` using
    ``abs_tol + rel_tol * ||p||_2 * ||v||_2``. A positive margin implies
    unbounded profit. A negative margin implies shutdown. In the numerical-zero
    regime every feasible activity is accepted as an optimal plan, reflecting
    the theoretical non-uniqueness without comparing bundles.
    """

    net_output_per_unit: Sequence[float] | FloatArray
    profit_margin_abs_tol: float = PROFIT_MARGIN_ABS_TOL
    profit_margin_rel_tol: float = PROFIT_MARGIN_REL_TOL

    def __post_init__(self) -> None:
        vector = np.asarray(self.net_output_per_unit, dtype=float)
        if vector.ndim != 1 or vector.size == 0:
            raise ValueError("Net output per unit must be a non-empty 1D vector.")
        if not np.all(np.isfinite(vector)) or np.all(vector == 0.0):
            raise ValueError("Net output per unit must be finite and nonzero.")
        if not np.isfinite(self.profit_margin_abs_tol) or self.profit_margin_abs_tol <= 0.0:
            raise ValueError("Profit-margin absolute tolerance must be finite and positive.")
        if not np.isfinite(self.profit_margin_rel_tol) or self.profit_margin_rel_tol <= 0.0:
            raise ValueError("Profit-margin relative tolerance must be finite and positive.")
        object.__setattr__(self, "net_output_per_unit", vector.copy())

    @property
    def n_goods(self) -> int:
        """Return the net-output dimension."""

        return int(np.asarray(self.net_output_per_unit).size)

    def activity_level(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Return the least-squares activity coordinate."""

        plan_array = self._validated_plan(plan)
        vector = np.asarray(self.net_output_per_unit)
        return float(np.dot(plan_array, vector) / np.dot(vector, vector))

    def feasibility_violation(
        self, plan: Sequence[float] | FloatArray
    ) -> float:
        """Measure ray-membership and nonnegative-activity violations."""

        plan_array = self._validated_plan(plan)
        vector = np.asarray(self.net_output_per_unit)
        activity = self.activity_level(plan_array)
        ray_error = float(np.max(np.abs(plan_array - activity * vector)))
        return max(ray_error, max(0.0, -activity))

    def unit_margin(self, prices: Sequence[float] | FloatArray) -> float:
        """Return profit per unit of activity."""

        price_array = self._validated_prices(prices)
        return float(np.dot(price_array, np.asarray(self.net_output_per_unit)))

    def assess_unit_margin(
        self, prices: Sequence[float] | FloatArray
    ) -> ProfitMarginAssessment:
        """Classify unit profit with a norm-scaled numerical-zero region."""

        price_array = self._validated_prices(prices)
        vector = np.asarray(self.net_output_per_unit)
        margin = float(np.dot(price_array, vector))
        scale = float(np.linalg.norm(price_array, ord=2) * np.linalg.norm(vector, ord=2))
        tolerance = self.profit_margin_abs_tol + self.profit_margin_rel_tol * scale
        if margin > tolerance:
            regime = ProfitMarginRegime.POSITIVE_UNBOUNDED
        elif margin < -tolerance:
            regime = ProfitMarginRegime.NEGATIVE_SHUTDOWN
        else:
            regime = ProfitMarginRegime.NUMERICAL_ZERO
        return ProfitMarginAssessment(margin, scale, tolerance, regime)

    def optimal_plan(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return shutdown, or reject an unbounded positive-margin problem."""

        assessment = self.assess_unit_margin(prices)
        if assessment.regime is ProfitMarginRegime.POSITIVE_UNBOUNDED:
            raise UnboundedProfitError(
                "Linear-ray profit is unbounded because unit margin "
                f"{assessment.margin:.16g} exceeds the scale-aware tolerance "
                f"{assessment.tolerance:.16g}."
            )
        return np.zeros(self.n_goods, dtype=float)

    def evaluate_optimality(
        self,
        prices: Sequence[float] | FloatArray,
        candidate_plan: Sequence[float] | FloatArray,
    ) -> FirmOptimalityResult:
        """Assess profit without rejecting non-unique zero-margin optima."""

        price_array = self._validated_prices(prices)
        plan_array = self._validated_plan(candidate_plan)
        violation = self.feasibility_violation(plan_array)
        assessment = self.assess_unit_margin(price_array)
        if assessment.regime is ProfitMarginRegime.POSITIVE_UNBOUNDED:
            self.optimal_plan(price_array)
        candidate_profit = self.profit(price_array, plan_array)
        if assessment.regime is ProfitMarginRegime.NUMERICAL_ZERO and violation == 0.0:
            optimum = plan_array
            optimal_profit = candidate_profit
        else:
            optimum = np.zeros(self.n_goods, dtype=float)
            optimal_profit = 0.0
        return FirmOptimalityResult(
            feasible=violation == 0.0,
            candidate_profit=candidate_profit,
            optimal_profit=optimal_profit,
            profit_gap=optimal_profit - candidate_profit,
            feasibility_violation=violation,
            method="LinearRayTechnology.scaled_margin_global_profit_oracle",
            optimal_plan=optimum.tolist(),
            profit_margin_assessment=assessment,
        )


@dataclass(frozen=True, slots=True)
class Firm:
    """A profit-maximizing firm with explicit consumer ownership."""

    id: str
    technology: ProductionTechnology
    ownership: FirmOwnership

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Firm id must be non-empty.")

    @property
    def n_goods(self) -> int:
        """Return the firm's commodity dimension."""

        return self.technology.n_goods

    def optimal_plan(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return one independently profit-maximizing net-output vector."""

        return self.technology.optimal_plan(prices)

    def profit(
        self,
        prices: Sequence[float] | FloatArray,
        plan: Sequence[float] | FloatArray,
    ) -> float:
        """Return signed accounting profit ``p dot y``."""

        return self.technology.profit(prices, plan)

    def evaluate_optimality(
        self,
        prices: Sequence[float] | FloatArray,
        candidate_plan: Sequence[float] | FloatArray,
    ) -> FirmOptimalityResult:
        """Independently assess production feasibility and profit optimality."""

        return self.technology.evaluate_optimality(prices, candidate_plan)
