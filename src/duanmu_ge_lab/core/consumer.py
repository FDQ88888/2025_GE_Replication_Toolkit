"""Consumer object shared by exchange and production economies."""

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.preferences import PreferenceModel
from duanmu_ge_lab.core.consumption import ConsumptionSet, NonnegativeOrthant

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class ConsumerOptimalityResult:
    """Independent utility-based assessment of a candidate consumption bundle.

    ``unique_demand_bundle_gap`` is only an auxiliary benchmark diagnostic. The
    formal optimality check uses ``utility_gap`` because a preference can have
    multiple utility-maximizing bundles.
    """

    feasible: bool
    candidate_utility: float | None
    optimal_utility: float | None
    utility_gap: float | None
    budget_violation: float
    method: str
    feasibility_violation: float
    unique_demand_bundle_gap: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable result data."""

        return {
            "feasible": self.feasible,
            "candidate_utility": self.candidate_utility,
            "optimal_utility": self.optimal_utility,
            "utility_gap": self.utility_gap,
            "budget_violation": self.budget_violation,
            "method": self.method,
            "feasibility_violation": self.feasibility_violation,
            "unique_demand_bundle_gap": self.unique_demand_bundle_gap,
        }


@dataclass(frozen=True, slots=True)
class Consumer:
    """A consumer with preferences and an initial endowment.

    Economic interpretation
        The consumer owns an endowment and a preference model. Income sources outside
        the endowment are supplied explicitly by an economy-level accounting object.
    Mathematical definition
        Wealth is ``w_i(p) = p dot omega_i`` and demand is the preference model's
        Marshallian demand at ``(p, w_i(p))``.
    Parameters
        id: Stable consumer identifier.
        preference: Numerical preference representation.
        endowment: Nonnegative commodity endowment vector.
        population_weight: Positive type/atom mass used only in economic aggregates.
        consumption_set: Explicit feasible set; defaults to ``R_+^L``.
    Raises
        ValueError: If identifiers, dimensions, or endowment values are invalid.
    """

    id: str
    preference: PreferenceModel
    endowment: Sequence[float] | FloatArray
    population_weight: float = 1.0
    consumption_set: ConsumptionSet | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Consumer id must be non-empty.")
        endowment_array = np.asarray(self.endowment, dtype=float)
        if endowment_array.shape != (self.preference.n_goods,):
            raise ValueError(
                "Consumer endowment dimension must match the preference model: "
                f"expected ({self.preference.n_goods},), got {endowment_array.shape}."
            )
        if not np.all(np.isfinite(endowment_array)):
            raise ValueError("Consumer endowment must contain only finite values.")
        if np.any(endowment_array < 0.0):
            raise ValueError("Consumer endowment must be nonnegative.")
        if (
            not np.isfinite(self.population_weight)
            or self.population_weight <= 0.0
        ):
            raise ValueError("Consumer population weight must be finite and positive.")
        consumption_set = self.consumption_set
        if consumption_set is None:
            consumption_set = NonnegativeOrthant(self.preference.n_goods)
        if consumption_set.n_goods != self.preference.n_goods:
            raise ValueError(
                "Consumer consumption-set dimension must match preferences."
            )
        object.__setattr__(self, "endowment", endowment_array.copy())
        object.__setattr__(self, "consumption_set", consumption_set)

    @property
    def n_goods(self) -> int:
        """Return the consumer's commodity dimension."""

        return self.preference.n_goods

    def wealth(self, prices: Sequence[float] | FloatArray) -> float:
        """Compute endowment wealth ``p dot omega_i``.

        Parameters
            prices: Finite price vector matching the endowment dimension.
        Returns
            Market value of the consumer's endowment.
        Raises
            ValueError: If prices have the wrong shape or nonfinite values.
        """

        price_array = self._validated_prices(prices)
        return float(np.dot(price_array, np.asarray(self.endowment)))

    def demand(self, prices: Sequence[float] | FloatArray) -> FloatArray:
        """Compute Marshallian demand at endowment wealth.

        Parameters
            prices: Price vector accepted by the preference model.
        Returns
            Individual demand vector.
        Raises
            ValueError: For invalid dimensions or preference-specific domain errors.
        """

        price_array = self._validated_prices(prices)
        return self.demand_at_income(price_array, self.wealth(price_array))

    def demand_at_income(
        self,
        prices: Sequence[float] | FloatArray,
        total_income: float,
    ) -> FloatArray:
        """Compute demand using an explicitly accounted total income.

        Production dividends and future policy transfers belong to the economy's
        income accounting. This method accepts their already-audited total and does
        not infer or modify any income source.
        """

        price_array = self._validated_prices(prices)
        income = self._validated_income(total_income)
        return self.preference.marshallian_demand(price_array, income)

    def utility(self, bundle: Sequence[float] | FloatArray) -> float:
        """Evaluate the consumer's numerical preference representation."""

        return self.preference.utility(bundle)

    def consumption_feasibility_violation(
        self, bundle: Sequence[float] | FloatArray
    ) -> float:
        """Return the maximum violation of the current domain ``R_+^L``.

        Shape and finiteness errors raise instead of being repaired. Commodity kind
        does not alter this set; the configured ``ConsumptionSet`` is authoritative.
        """

        bundle_array = self._validated_bundle(bundle)
        return self.consumption_set.feasibility_violation(bundle_array)

    def is_consumption_feasible(
        self,
        bundle: Sequence[float] | FloatArray,
        tolerance: float = 0.0,
    ) -> bool:
        """Check membership in ``R_+^L`` up to an explicit numerical tolerance."""

        if not np.isfinite(tolerance) or tolerance < 0.0:
            raise ValueError("Feasibility tolerance must be finite and nonnegative.")
        return self.consumption_feasibility_violation(bundle) <= tolerance

    def evaluate_optimality(
        self,
        prices: Sequence[float] | FloatArray,
        bundle: Sequence[float] | FloatArray,
    ) -> ConsumerOptimalityResult:
        """Compare candidate and independently optimized utility under the budget.

        This method supports numerical utility representations with a valid
        Marshallian-demand oracle. Relation-only paper preferences without such an
        oracle are not supported by this Milestone 1 verifier.
        """

        price_array = self._validated_prices(prices)
        return self.evaluate_optimality_at_income(
            price_array, bundle, self.wealth(price_array)
        )

    def evaluate_optimality_at_income(
        self,
        prices: Sequence[float] | FloatArray,
        bundle: Sequence[float] | FloatArray,
        total_income: float,
    ) -> ConsumerOptimalityResult:
        """Evaluate utility optimality at an explicit total budget income."""

        price_array = self._validated_prices(prices)
        bundle_array = self._validated_bundle(bundle)
        income = self._validated_income(total_income)
        feasibility_violation = self.consumption_feasibility_violation(bundle_array)
        feasible = feasibility_violation == 0.0
        budget_residual = self.budget_residual_at_income(
            price_array, bundle_array, income
        )
        budget_violation = max(0.0, -budget_residual)

        optimal_bundle = self.demand_at_income(price_array, income)
        optimal_utility = self.utility(optimal_bundle)
        candidate_utility: float | None = None
        utility_gap: float | None = None
        if feasible:
            candidate_utility = self.utility(bundle_array)
            utility_gap = optimal_utility - candidate_utility

        unique_gap: float | None = None
        if self.preference.has_unique_marshallian_demand:
            unique_gap = float(np.max(np.abs(bundle_array - optimal_bundle)))
            method = (
                "UTILITY_GAP_WITH_UNIQUE_DEMAND_BENCHMARK_CHECK:"
                f"{type(self.preference).__name__}.marshallian_demand"
            )
        else:
            method = (
                "UTILITY_GAP:"
                f"{type(self.preference).__name__}.marshallian_demand"
            )

        return ConsumerOptimalityResult(
            feasible=feasible,
            candidate_utility=candidate_utility,
            optimal_utility=optimal_utility,
            utility_gap=utility_gap,
            budget_violation=budget_violation,
            method=method,
            feasibility_violation=feasibility_violation,
            unique_demand_bundle_gap=unique_gap,
        )

    def budget_residual(
        self, prices: Sequence[float] | FloatArray, bundle: Sequence[float] | FloatArray
    ) -> float:
        """Return budget slack ``p dot omega_i - p dot x_i``.

        Economic interpretation
            A feasible bundle has residual at least zero. Budget exhaustion is a
            separate equality diagnostic and is not substituted for feasibility.
        Parameters
            prices: Finite price vector.
            bundle: Candidate consumption bundle.
        Returns
            Positive slack, zero exhaustion, or a negative budget violation.
        Raises
            ValueError: If dimensions or values are invalid.
        """

        price_array = self._validated_prices(prices)
        return self.budget_residual_at_income(
            price_array, bundle, self.wealth(price_array)
        )

    def budget_residual_at_income(
        self,
        prices: Sequence[float] | FloatArray,
        bundle: Sequence[float] | FloatArray,
        total_income: float,
    ) -> float:
        """Return explicit income minus candidate expenditure."""

        price_array = self._validated_prices(prices)
        bundle_array = self._validated_bundle(bundle)
        income = self._validated_income(total_income)
        return income - float(np.dot(price_array, bundle_array))

    def _validated_bundle(
        self, bundle: Sequence[float] | FloatArray
    ) -> FloatArray:
        bundle_array = np.asarray(bundle, dtype=float)
        if bundle_array.shape != (self.n_goods,):
            raise ValueError(
                f"Bundle must have shape ({self.n_goods},), got {bundle_array.shape}."
            )
        if not np.all(np.isfinite(bundle_array)):
            raise ValueError("Bundle must contain only finite values.")
        return bundle_array

    def _validated_prices(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        price_array = np.asarray(prices, dtype=float)
        if price_array.shape != (self.n_goods,):
            raise ValueError(
                f"Prices must have shape ({self.n_goods},), got {price_array.shape}."
            )
        if not np.all(np.isfinite(price_array)):
            raise ValueError("Prices must contain only finite values.")
        return price_array

    @staticmethod
    def _validated_income(total_income: float) -> float:
        income = float(total_income)
        if not np.isfinite(income):
            raise ValueError("Total consumer income must be finite.")
        return income
