"""Finite production economy with explicit ownership and dividend accounting."""

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.commodity import Commodity
from duanmu_ge_lab.core.consumer import Consumer
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import Firm

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class ProductionEconomy:
    """A finite Arrow-Debreu production economy without policy.

    Resource accounting always uses
    ``sum_i x_i - sum_i e_i - sum_j y_j`` where firm plans follow the net-output
    convention. Consumer income is endowment value plus ownership-weighted profit.
    """

    commodities: Sequence[Commodity]
    consumers: Sequence[Consumer]
    firms: Sequence[Firm]

    def __post_init__(self) -> None:
        commodities = tuple(self.commodities)
        consumers = tuple(self.consumers)
        firms = tuple(self.firms)
        if not commodities:
            raise ValueError("A production economy needs at least one commodity.")
        if not consumers:
            raise ValueError("A production economy needs at least one consumer.")
        expected_indexes = list(range(len(commodities)))
        actual_indexes = [commodity.index for commodity in commodities]
        if actual_indexes != expected_indexes:
            raise ValueError(
                "Commodities must have contiguous ordered zero-based indexes."
            )
        consumer_ids = [consumer.id for consumer in consumers]
        firm_ids = [firm.id for firm in firms]
        if len(consumer_ids) != len(set(consumer_ids)):
            raise ValueError("Consumer ids must be unique.")
        if len(firm_ids) != len(set(firm_ids)):
            raise ValueError("Firm ids must be unique.")
        for consumer in consumers:
            if consumer.n_goods != len(commodities):
                raise ValueError("Consumer dimension does not match the economy.")
        valid_consumers = set(consumer_ids)
        for firm in firms:
            if firm.n_goods != len(commodities):
                raise ValueError("Firm dimension does not match the economy.")
            unknown = set(firm.ownership.shares) - valid_consumers
            if unknown:
                raise ValueError(
                    f"Firm {firm.id!r} has unknown owners: {sorted(unknown)}."
                )
        object.__setattr__(self, "commodities", commodities)
        object.__setattr__(self, "consumers", consumers)
        object.__setattr__(self, "firms", firms)

    @property
    def n_goods(self) -> int:
        """Return the commodity dimension."""

        return len(self.commodities)

    @property
    def n_consumers(self) -> int:
        """Return the number of consumers."""

        return len(self.consumers)

    @property
    def n_firms(self) -> int:
        """Return the number of firms."""

        return len(self.firms)

    def aggregate_endowment(self) -> FloatArray:
        """Return ``sum_i lambda_i e_i``."""

        return np.sum(
            self.population_weights()[:, None]
            * np.vstack([np.asarray(consumer.endowment) for consumer in self.consumers]),
            axis=0,
        )

    def population_weights(self) -> FloatArray:
        """Return type masses, kept separate from any welfare weights."""

        return np.asarray(
            [consumer.population_weight for consumer in self.consumers], dtype=float
        )

    def aggregate_allocations(
        self, allocations: Sequence[Sequence[float]] | FloatArray
    ) -> FloatArray:
        """Return ``sum_i lambda_i x_i`` for per-capita candidate bundles."""

        array = self._validated_allocations(allocations)
        return np.sum(self.population_weights()[:, None] * array, axis=0)

    def ownership_total(self, firm: Firm) -> float:
        """Return the population-weighted ownership density integral."""

        return float(
            sum(
                consumer.population_weight
                * firm.ownership.share_of(consumer.id)
                for consumer in self.consumers
            )
        )

    def ownership_adding_up_error(self, firm: Firm) -> float:
        """Return ``abs(sum_i lambda_i theta_ij - 1)``."""

        return abs(self.ownership_total(firm) - 1.0)

    def optimal_firm_plans(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Independently maximize every firm's profit."""

        price_array = self._validated_prices(prices)
        if not self.firms:
            return np.empty((0, self.n_goods), dtype=float)
        return np.vstack([firm.optimal_plan(price_array) for firm in self.firms])

    def firm_profits(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> FloatArray:
        """Return each firm's accounting profit at supplied candidate plans."""

        price_array = self._validated_prices(prices)
        plans = self._validated_firm_plans(firm_plans)
        if not self.firms:
            return np.empty(0, dtype=float)
        return np.asarray(
            [
                firm.profit(price_array, plans[index])
                for index, firm in enumerate(self.firms)
            ],
            dtype=float,
        )

    def income_breakdowns(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
        policy_income: Mapping[str, float] | None = None,
    ) -> dict[str, IncomeBreakdown]:
        """Compute endowment, dividend, and explicit policy income by consumer."""

        price_array = self._validated_prices(prices)
        plans = self._validated_firm_plans(firm_plans)
        policies = dict(policy_income or {})
        unknown = set(policies) - {consumer.id for consumer in self.consumers}
        if unknown:
            raise ValueError(f"Policy income has unknown consumers: {sorted(unknown)}.")
        if not all(np.isfinite(value) for value in policies.values()):
            raise ValueError("Policy income values must be finite.")
        profits = self.firm_profits(price_array, plans)
        breakdowns: dict[str, IncomeBreakdown] = {}
        for consumer in self.consumers:
            dividends = sum(
                firm.ownership.share_of(consumer.id) * profits[index]
                for index, firm in enumerate(self.firms)
            )
            breakdowns[consumer.id] = IncomeBreakdown(
                endowment_income=consumer.wealth(price_array),
                firm_dividend_income=float(dividends),
                policy_income=float(policies.get(consumer.id, 0.0)),
            )
        return breakdowns

    def individual_demands(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray | None = None,
    ) -> FloatArray:
        """Compute demands using profit income from supplied or optimal plans."""

        price_array = self._validated_prices(prices)
        plans = (
            self.optimal_firm_plans(price_array)
            if firm_plans is None
            else self._validated_firm_plans(firm_plans)
        )
        incomes = self.income_breakdowns(price_array, plans)
        return np.vstack(
            [
                consumer.demand_at_income(
                    price_array, incomes[consumer.id].total_income
                )
                for consumer in self.consumers
            ]
        )

    def candidate_resource_residual(
        self,
        allocations: Sequence[Sequence[float]] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> FloatArray:
        """Return ``sum x - sum e - sum y`` for the candidate itself."""

        allocation_array = self._validated_allocations(allocations)
        plans = self._validated_firm_plans(firm_plans)
        return (
            self.aggregate_allocations(allocation_array)
            - self.aggregate_endowment()
            - np.sum(plans, axis=0)
        )

    def excess_demand(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return reoptimized demand minus endowment and optimal production."""

        price_array = self._validated_prices(prices)
        plans = self.optimal_firm_plans(price_array)
        demands = self.individual_demands(price_array, plans)
        return self.candidate_resource_residual(demands, plans)

    def walras_residual(
        self, prices: Sequence[float] | FloatArray
    ) -> float:
        """Return ``p dot z(p)`` for the fully reoptimized production economy."""

        price_array = self._validated_prices(prices)
        return float(np.dot(price_array, self.excess_demand(price_array)))

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

    def _validated_allocations(
        self, allocations: Sequence[Sequence[float]] | FloatArray
    ) -> FloatArray:
        array = np.asarray(allocations, dtype=float)
        expected = (self.n_consumers, self.n_goods)
        if array.shape != expected:
            raise ValueError(f"Allocations must have shape {expected}, got {array.shape}.")
        if not np.all(np.isfinite(array)):
            raise ValueError("Allocations must contain only finite values.")
        return array

    def _validated_firm_plans(
        self, firm_plans: Sequence[Sequence[float]] | FloatArray
    ) -> FloatArray:
        array = np.asarray(firm_plans, dtype=float)
        expected = (self.n_firms, self.n_goods)
        if array.shape != expected:
            raise ValueError(f"Firm plans must have shape {expected}, got {array.shape}.")
        if not np.all(np.isfinite(array)):
            raise ValueError("Firm plans must contain only finite values.")
        return array
