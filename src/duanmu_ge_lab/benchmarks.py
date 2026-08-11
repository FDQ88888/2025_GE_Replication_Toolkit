"""Analytical software-validation benchmarks kept outside generic economic classes."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core import (
    ClearingRule,
    CapacityConstrainedLinearTechnology,
    BadAbsorptionLinearUtility,
    BoxConsumptionSet,
    CobbDouglasUtility,
    Commodity,
    CommodityKind,
    Consumer,
    ExchangeEconomy,
    Firm,
    FirmOwnership,
    ProductionEconomy,
)
from duanmu_ge_lab.equilibrium.normalization import FixedNumeraire
from duanmu_ge_lab.equilibrium.prices import PriceSign, PriceSignRestrictions

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class AnalyticalBenchmarkSolution:
    """Ground truth for the two-consumer, two-good validation economy."""

    prices: FloatArray
    allocations: FloatArray

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable analytical solution."""

        return {
            "prices": self.prices.tolist(),
            "allocations": self.allocations.tolist(),
        }


@dataclass(frozen=True, slots=True)
class AnalyticalProductionBenchmarkSolution:
    """Ground truth for the Milestone 2 production benchmark."""

    prices: FloatArray
    allocations: FloatArray
    firm_plans: FloatArray
    firm_profits: FloatArray
    income_breakdowns: dict[str, dict[str, float]]

    def to_dict(self) -> dict[str, Any]:
        """Return the complete analytical solution as JSON data."""

        return {
            "prices": self.prices.tolist(),
            "allocations": self.allocations.tolist(),
            "firm_plans": self.firm_plans.tolist(),
            "firm_profits": self.firm_profits.tolist(),
            "income_breakdowns": {
                consumer_id: dict(values)
                for consumer_id, values in self.income_breakdowns.items()
            },
        }


def build_two_by_two_cobb_douglas_benchmark() -> tuple[
    ExchangeEconomy, FixedNumeraire, AnalyticalBenchmarkSolution
]:
    """Construct the Milestone 1 analytical exchange-economy benchmark.

    Economic interpretation
        This is a SOFTWARE VALIDATION BENCHMARK, not an Anderson-Duanmu paper
        replication. Two consumers own opposite goods and have equal Cobb-Douglas
        expenditure shares.
    Mathematical definition
        Endowments are ``(1,0)`` and ``(0,1)``, both alpha vectors are ``(1/2,1/2)``,
        and commodity 2 is the numeraire with price one.
    Returns
        Economy, fixed-numeraire normalization, and exact solution ``p=(1,1)`` with
        both consumers demanding ``(1/2,1/2)``.
    """

    commodities = (
        Commodity(
            name="Good 1",
            index=0,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
        Commodity(
            name="Good 2",
            index=1,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
    )
    consumers = (
        Consumer(
            id="Consumer 1",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([1.0, 0.0]),
        ),
        Consumer(
            id="Consumer 2",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([0.0, 1.0]),
        ),
    )
    economy = ExchangeEconomy(commodities=commodities, consumers=consumers)
    normalization = FixedNumeraire(index=1, value=1.0)
    solution = AnalyticalBenchmarkSolution(
        prices=np.array([1.0, 1.0]),
        allocations=np.array([[0.5, 0.5], [0.5, 0.5]]),
    )
    return economy, normalization, solution


def build_analytical_production_benchmark() -> tuple[
    ProductionEconomy,
    FixedNumeraire,
    AnalyticalProductionBenchmarkSolution,
]:
    """Construct a capacity-rent production economy with a closed-form equilibrium.

    Economic interpretation
        This is an ANALYTICAL PRODUCTION BENCHMARK and OUR COMPUTATIONAL CHOICE,
        not a paper replication. Two consumers own equal input endowments but own
        one capacity-constrained conversion firm in shares 1/4 and 3/4.
    Mathematical definition
        The firm chooses ``y=a*(-1,1)`` for ``0<=a<=1/2``. Both consumers have
        equal-share Cobb-Douglas utility and endowments ``(1,0)``. Good 2 is the
        numeraire. At ``p=(1/3,1)`` the capacity plan ``(-1/2,1/2)`` earns profit
        ``1/3`` and aggregate available resources are ``(3/2,1/2)``.
    Returns
        Production economy, normalization, and exact prices, allocations, production,
        profit, and ownership-income decomposition.
    """

    commodities = (
        Commodity(
            name="Input good",
            index=0,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
        Commodity(
            name="Output good",
            index=1,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
    )
    consumers = (
        Consumer(
            id="Consumer 1",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([1.0, 0.0]),
        ),
        Consumer(
            id="Consumer 2",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([1.0, 0.0]),
        ),
    )
    firm = Firm(
        id="Conversion firm",
        technology=CapacityConstrainedLinearTechnology(
            net_output_per_unit=np.array([-1.0, 1.0]),
            capacity=0.5,
        ),
        ownership=FirmOwnership(
            {"Consumer 1": 0.25, "Consumer 2": 0.75}
        ),
    )
    economy = ProductionEconomy(
        commodities=commodities,
        consumers=consumers,
        firms=(firm,),
    )
    normalization = FixedNumeraire(index=1, value=1.0)
    solution = AnalyticalProductionBenchmarkSolution(
        prices=np.array([1.0 / 3.0, 1.0]),
        allocations=np.array(
            [
                [5.0 / 8.0, 5.0 / 24.0],
                [7.0 / 8.0, 7.0 / 24.0],
            ]
        ),
        firm_plans=np.array([[-0.5, 0.5]]),
        firm_profits=np.array([1.0 / 3.0]),
        income_breakdowns={
            "Consumer 1": {
                "endowment_income": 1.0 / 3.0,
                "firm_dividend_income": 1.0 / 12.0,
                "policy_income": 0.0,
                "total_income": 5.0 / 12.0,
            },
            "Consumer 2": {
                "endowment_income": 1.0 / 3.0,
                "firm_dividend_income": 1.0 / 4.0,
                "policy_income": 0.0,
                "total_income": 7.0 / 12.0,
            },
        },
    )
    return economy, normalization, solution


def build_split_agent_invariance_benchmarks() -> tuple[
    ProductionEconomy,
    ProductionEconomy,
    FixedNumeraire,
]:
    """Build equivalent one-type and split-type weighted production economies.

    The original consumer has population mass one. The split economy replaces that
    type by two identical types with masses ``0.4`` and ``0.6``. Endowment,
    preferences, and ownership density are identical per type, so every paper-defined
    population aggregate and the equilibrium should remain unchanged.
    """

    commodities = (
        Commodity(
            name="Input good",
            index=0,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
        Commodity(
            name="Output good",
            index=1,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
    )
    technology = CapacityConstrainedLinearTechnology(
        net_output_per_unit=np.array([-1.0, 1.0]), capacity=0.5
    )
    original_consumer = Consumer(
        id="Original type",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([2.0, 0.0]),
        population_weight=1.0,
    )
    original = ProductionEconomy(
        commodities=commodities,
        consumers=(original_consumer,),
        firms=(
            Firm(
                id="Conversion firm",
                technology=technology,
                ownership=FirmOwnership({"Original type": 1.0}),
            ),
        ),
    )
    split_consumers = (
        Consumer(
            id="Split type A",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([2.0, 0.0]),
            population_weight=0.4,
        ),
        Consumer(
            id="Split type B",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([2.0, 0.0]),
            population_weight=0.6,
        ),
    )
    split = ProductionEconomy(
        commodities=commodities,
        consumers=split_consumers,
        firms=(
            Firm(
                id="Conversion firm",
                technology=technology,
                ownership=FirmOwnership(
                    {"Split type A": 1.0, "Split type B": 1.0}
                ),
            ),
        ),
    )
    return original, split, FixedNumeraire(index=1, value=1.0)


def build_signed_bad_absorption_benchmark() -> tuple[
    ExchangeEconomy,
    FixedNumeraire,
    PriceSignRestrictions,
    AnalyticalBenchmarkSolution,
]:
    """Build a negative-price, exact-clearing bad-absorption benchmark.

    A single consumer is endowed with one unit of a bad and two units of a good.
    At ``p=(-1,1)``, absorbing the bad finances additional good consumption and is
    optimal under ``u(b,g)=g-b/2`` with absorption capacity one. The BAD kind is only
    metadata; the price restriction and consumption bound are configured separately.
    """

    commodities = (
        Commodity(
            name="Absorbed bad",
            index=0,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.BAD,
        ),
        Commodity(
            name="Ordinary good",
            index=1,
            clearing_rule=ClearingRule.EXACT,
            kind=CommodityKind.GOOD,
        ),
    )
    consumer = Consumer(
        id="Bad absorber",
        preference=BadAbsorptionLinearUtility(
            bad_disutility=0.5, max_bad=1.0
        ),
        endowment=np.array([1.0, 2.0]),
        consumption_set=BoxConsumptionSet(
            lower_bounds=np.array([0.0, 0.0]),
            upper_bounds=np.array([1.0, np.inf]),
        ),
    )
    economy = ExchangeEconomy(commodities=commodities, consumers=(consumer,))
    normalization = FixedNumeraire(index=1, value=1.0)
    restrictions = PriceSignRestrictions(
        (PriceSign.NEGATIVE, PriceSign.POSITIVE)
    )
    analytical = AnalyticalBenchmarkSolution(
        prices=np.array([-1.0, 1.0]),
        allocations=np.array([[1.0, 2.0]]),
    )
    return economy, normalization, restrictions, analytical
