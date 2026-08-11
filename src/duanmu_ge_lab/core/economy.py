"""Finite exchange economy aggregation and excess-demand accounting."""

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.commodity import Commodity
from duanmu_ge_lab.core.consumer import Consumer

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class ExchangeEconomy:
    """A finite pure exchange economy.

    Economic interpretation
        Consumers trade fixed aggregate endowments. There are no firms, policies, or
        externalities in Milestone 1.
    Mathematical definition
        Aggregate excess demand uses the single project-wide sign convention
        ``z(p) = sum_i x_i(p) - sum_i omega_i``.
    Parameters
        commodities: Ordered commodity coordinates with explicit clearing rules.
        consumers: Finite collection of consumers with matching dimensions.
    Raises
        ValueError: If collections are empty, indexes are inconsistent, consumer ids
        repeat, or dimensions disagree.
    """

    commodities: Sequence[Commodity]
    consumers: Sequence[Consumer]

    def __post_init__(self) -> None:
        commodity_tuple = tuple(self.commodities)
        consumer_tuple = tuple(self.consumers)
        if not commodity_tuple:
            raise ValueError("An exchange economy must contain at least one commodity.")
        if not consumer_tuple:
            raise ValueError("An exchange economy must contain at least one consumer.")
        expected_indexes = list(range(len(commodity_tuple)))
        actual_indexes = [commodity.index for commodity in commodity_tuple]
        if actual_indexes != expected_indexes:
            raise ValueError(
                "Commodities must be ordered with contiguous zero-based indexes; "
                f"expected {expected_indexes}, got {actual_indexes}."
            )
        ids = [consumer.id for consumer in consumer_tuple]
        if len(ids) != len(set(ids)):
            raise ValueError("Consumer ids must be unique.")
        for consumer in consumer_tuple:
            if consumer.n_goods != len(commodity_tuple):
                raise ValueError(
                    f"Consumer {consumer.id!r} has {consumer.n_goods} goods but the "
                    f"economy has {len(commodity_tuple)}."
                )
        object.__setattr__(self, "commodities", commodity_tuple)
        object.__setattr__(self, "consumers", consumer_tuple)

    @property
    def n_goods(self) -> int:
        """Return the number of commodity coordinates."""

        return len(self.commodities)

    @property
    def n_consumers(self) -> int:
        """Return the number of consumers."""

        return len(self.consumers)

    def aggregate_endowment(self) -> FloatArray:
        """Return ``sum_i lambda_i omega_i``.

        Returns
            Aggregate endowment vector with one coordinate per commodity.
        """

        return np.sum(
            self.population_weights()[:, None]
            * np.vstack([np.asarray(c.endowment) for c in self.consumers]),
            axis=0,
        )

    def population_weights(self) -> FloatArray:
        """Return consumer masses; these are not social-welfare weights."""

        return np.asarray(
            [consumer.population_weight for consumer in self.consumers], dtype=float
        )

    def aggregate_allocations(
        self, allocations: Sequence[Sequence[float]] | FloatArray
    ) -> FloatArray:
        """Return the population-weighted aggregate of per-capita bundles."""

        array = np.asarray(allocations, dtype=float)
        expected = (self.n_consumers, self.n_goods)
        if array.shape != expected:
            raise ValueError(f"Allocations must have shape {expected}, got {array.shape}.")
        if not np.all(np.isfinite(array)):
            raise ValueError("Allocations must contain only finite values.")
        return np.sum(self.population_weights()[:, None] * array, axis=0)

    def individual_demands(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Compute every consumer's demand at a common price vector.

        Parameters
            prices: Finite price vector accepted by each preference model.
        Returns
            Matrix with shape ``(n_consumers, n_goods)``.
        Raises
            ValueError: For shape errors or unsupported preference price domains.
        """

        price_array = self._validated_prices(prices)
        return np.vstack([consumer.demand(price_array) for consumer in self.consumers])

    def aggregate_demand(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return ``sum_i x_i(p)`` for the supplied prices."""

        return self.aggregate_allocations(self.individual_demands(prices))

    def excess_demand(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return ``z(p) = aggregate demand - aggregate endowment``.

        Parameters
            prices: Common commodity price vector.
        Returns
            Excess demand using the only sign convention allowed in this project.
        """

        return self.aggregate_demand(prices) - self.aggregate_endowment()

    def market_residuals(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return commodity-wise market residuals, identical to excess demand."""

        return self.excess_demand(prices)

    def walras_residual(
        self, prices: Sequence[float] | FloatArray
    ) -> float:
        """Return the Walras-law diagnostic ``p dot z(p)``.

        This value is a diagnostic identity. It never replaces any commodity-level
        market-clearing check.
        """

        price_array = self._validated_prices(prices)
        return float(np.dot(price_array, self.excess_demand(price_array)))

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
