"""Exact primitives and analytical targets for paper Examples 1 and 2."""

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core import (
    BoxConsumptionSet,
    ClearingRule,
    Commodity,
    CommodityKind,
    Consumer,
    Example3Utility,
    Firm,
    FirmOwnership,
    LinearRayTechnology,
    ProductionEconomy,
    SingleGoodLinearUtility,
    ZeroTechnology,
)
from duanmu_ge_lab.policy import (
    EmissionTaxEconomy,
    EmissionTaxPolicy,
    PaperTaxConvention,
    QuotaEconomy,
    QuotaPolicy,
)

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class PaperQuotaSolution:
    """Analytical coordinates and paper-accounting values for one quota regime."""

    prices: FloatArray
    allocations: FloatArray
    firm_plans: FloatArray
    quota_prices: FloatArray
    operating_profits: dict[str, float]
    quota_profit_terms: dict[str, float]
    total_firm_profits: dict[str, float]
    income_breakdowns: dict[str, dict[str, float]]
    paper_utility_data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "prices": self.prices.tolist(),
            "allocations": self.allocations.tolist(),
            "firm_plans": self.firm_plans.tolist(),
            "quota_prices": self.quota_prices.tolist(),
            "operating_profits": dict(self.operating_profits),
            "quota_profit_terms": dict(self.quota_profit_terms),
            "total_firm_profits": dict(self.total_firm_profits),
            "income_breakdowns": {
                consumer_id: dict(values)
                for consumer_id, values in self.income_breakdowns.items()
            },
            "paper_utility_data": dict(self.paper_utility_data),
        }


def _paper_commodities() -> tuple[Commodity, ...]:
    return (
        Commodity("CO2 emissions", 0, ClearingRule.EXACT, CommodityKind.BAD),
        Commodity("coal", 1, ClearingRule.EXACT, CommodityKind.GOOD),
        Commodity("electricity", 2, ClearingRule.EXACT, CommodityKind.GOOD),
    )


def _paper_consumption_set() -> BoxConsumptionSet:
    return BoxConsumptionSet(
        lower_bounds=np.zeros(3), upper_bounds=np.array([0.0, np.inf, np.inf])
    )


def build_paper_example_1(
    emissions_quota_v: float,
) -> tuple[QuotaEconomy, PaperQuotaSolution]:
    """Build main-paper Example 1 and Claim 3.1's analytical equilibrium."""

    v = float(emissions_quota_v)
    if not np.isfinite(v) or not 0.0 < v <= 1.0:
        raise ValueError("Paper Example 1 requires emissions quota v in (0,1].")
    consumers = (
        Consumer(
            id="omega_1",
            preference=SingleGoodLinearUtility(3, 2, fixed_zero_indexes=(0,)),
            endowment=np.array([0.0, 1.0, 0.0]),
            consumption_set=_paper_consumption_set(),
        ),
        Consumer(
            id="omega_2",
            preference=SingleGoodLinearUtility(3, 1, fixed_zero_indexes=(0,)),
            endowment=np.zeros(3),
            consumption_set=_paper_consumption_set(),
        ),
    )
    firms = (
        Firm(
            "firm_0",
            ZeroTechnology(3),
            FirmOwnership({"omega_1": 0.0, "omega_2": 1.0}),
        ),
        Firm(
            "firm_1",
            LinearRayTechnology(np.array([1.0, -1.0, 1.0])),
            FirmOwnership({"omega_1": 0.5, "omega_2": 0.5}),
        ),
    )
    economy = QuotaEconomy(
        ProductionEconomy(_paper_commodities(), consumers, firms),
        QuotaPolicy(
            regulated_count=1,
            firm_quotas={"firm_0": np.array([-v]), "firm_1": np.array([0.0])},
            unregulated_rules=(ClearingRule.EXACT, ClearingRule.EXACT),
        ),
    )
    prices = np.array([(v - 1.0) / 2.0, v / 2.0, 0.5])
    allocations = np.array([[0.0, 0.0, v], [0.0, 1.0 - v, 0.0]])
    plans = np.array([[0.0, 0.0, 0.0], [v, -v, v]])
    profit_parts = economy.firm_profit_breakdowns(prices, plans)
    incomes = economy.income_breakdowns(prices, plans)
    solution = PaperQuotaSolution(
        prices=prices,
        allocations=allocations,
        firm_plans=plans,
        quota_prices=economy.policy.quota_prices(prices),
        operating_profits={
            key: value.operating_profit for key, value in profit_parts.items()
        },
        quota_profit_terms={
            key: value.quota_profit for key, value in profit_parts.items()
        },
        total_firm_profits={
            key: value.total_profit for key, value in profit_parts.items()
        },
        income_breakdowns={key: value.to_dict() for key, value in incomes.items()},
        paper_utility_data={
            "cardinal_utility_is_explicit_in_paper": True,
            "total_net_emissions_v": v,
            "omega_1": v - v**2,
            "omega_2": 1.0 - v - v**2,
        },
    )
    return economy, solution


def build_paper_example_2(
    emissions_quota_v: float,
    regime: Literal["global_quota", "cap_and_trade"],
) -> tuple[QuotaEconomy, PaperQuotaSolution]:
    """Build main-paper Example 2 under one quota-rights allocation."""

    v = float(emissions_quota_v)
    if not np.isfinite(v) or not 0.0 <= v < 6.0:
        raise ValueError("Paper Example 2 requires emissions quota v in [0,6).")
    if regime not in ("global_quota", "cap_and_trade"):
        raise ValueError("Unknown Example 2 quota regime.")
    consumers = tuple(
        Consumer(
            id=f"omega_{omega}",
            preference=SingleGoodLinearUtility(3, 2, fixed_zero_indexes=(0,)),
            endowment=np.array([0.0, float(omega), 0.0]),
            consumption_set=_paper_consumption_set(),
        )
        for omega in (1, 2, 3)
    )
    equal = {f"omega_{omega}": 1.0 / 3.0 for omega in (1, 2, 3)}
    firm_1_ownership = {
        f"omega_{omega}": float(omega) / 6.0 for omega in (1, 2, 3)
    }
    firms = (
        Firm("firm_0", ZeroTechnology(3), FirmOwnership(equal)),
        Firm(
            "firm_1",
            LinearRayTechnology(np.array([1.0, -1.0, 1.0])),
            FirmOwnership(firm_1_ownership),
        ),
        Firm(
            "firm_2",
            LinearRayTechnology(np.array([-2.0, 0.0, -1.0])),
            FirmOwnership(equal),
        ),
    )
    firm_quotas = {
        "firm_0": np.array([-v if regime == "global_quota" else 0.0]),
        "firm_1": np.array([-v if regime == "cap_and_trade" else 0.0]),
        "firm_2": np.array([0.0]),
    }
    economy = QuotaEconomy(
        ProductionEconomy(_paper_commodities(), consumers, firms),
        QuotaPolicy(
            regulated_count=1,
            firm_quotas=firm_quotas,
            unregulated_rules=(ClearingRule.EXACT, ClearingRule.EXACT),
        ),
    )
    prices = np.array([-0.25, 0.25, 0.5])
    electricity = np.array(
        [
            omega / 2.0
            + (v / 6.0 if regime == "global_quota" else v * omega / 12.0)
            for omega in (1, 2, 3)
        ]
    )
    allocations = np.column_stack([np.zeros(3), np.zeros(3), electricity])
    sequestration = (6.0 - v) / 2.0
    plans = np.array(
        [
            [0.0, 0.0, 0.0],
            [6.0, -6.0, 6.0],
            [-2.0 * sequestration, 0.0, -sequestration],
        ]
    )
    profit_parts = economy.firm_profit_breakdowns(prices, plans)
    incomes = economy.income_breakdowns(prices, plans)
    solution = PaperQuotaSolution(
        prices=prices,
        allocations=allocations,
        firm_plans=plans,
        quota_prices=economy.policy.quota_prices(prices),
        operating_profits={
            key: value.operating_profit for key, value in profit_parts.items()
        },
        quota_profit_terms={
            key: value.quota_profit for key, value in profit_parts.items()
        },
        total_firm_profits={
            key: value.total_profit for key, value in profit_parts.items()
        },
        income_breakdowns={key: value.to_dict() for key, value in incomes.items()},
        paper_utility_data={
            "cardinal_utility_is_explicit_in_paper": False,
            "reason": (
                "Example 2 specifies monotone electricity preferences and an "
                "emissions externality, but no cardinal utility formula."
            ),
            "own_electricity_components": {
                f"omega_{omega}": float(electricity[omega - 1])
                for omega in (1, 2, 3)
            },
        },
    )
    return economy, solution


def paper_example_3_r() -> float:
    """Return the endowment parameter `2^(8/9)-2^(1/9)`."""

    return float(2.0 ** (8.0 / 9.0) - 2.0 ** (1.0 / 9.0))


def build_paper_example_3_tax_economy(
    table_goods_sum_tax_rate: float,
) -> EmissionTaxEconomy:
    """Build Example 3 in signed-L1 core coordinates with no firms."""

    tau = float(table_goods_sum_tax_rate)
    if not np.isfinite(tau) or tau < 0.0:
        raise ValueError("Example 3 table tax rate must be finite and nonnegative.")
    r = paper_example_3_r()
    commodities = (
        Commodity(
            "commodity 0 emissions",
            0,
            ClearingRule.FREE_DISPOSAL,
            CommodityKind.BAD,
        ),
        Commodity("commodity 1", 1, ClearingRule.EXACT, CommodityKind.GOOD),
        Commodity("commodity 2", 2, ClearingRule.EXACT, CommodityKind.GOOD),
    )
    consumers = (
        Consumer("omega_1", Example3Utility(1), np.array([0.2, 2.0, r])),
        Consumer("omega_2", Example3Utility(2), np.array([0.2, r, 2.0])),
    )
    signed_l1_tax = tau / (1.0 + tau)
    return EmissionTaxEconomy(
        ProductionEconomy(commodities, consumers, ()),
        EmissionTaxPolicy(
            regulated_count=1,
            tax_rates=np.array([signed_l1_tax]),
            rebate_shares={"omega_1": 0.5, "omega_2": 0.5},
            unregulated_rules=(ClearingRule.EXACT, ClearingRule.EXACT),
        ),
    )


def paper_example_3_table_prices(tau: float, eta: float) -> FloatArray:
    """Return Example 3 prices under `p1+p2=1`."""

    if not np.isfinite(tau) or tau < 0.0:
        raise ValueError("Example 3 tau must be finite and nonnegative.")
    if not np.isfinite(eta) or eta <= 0.0:
        raise ValueError("Example 3 eta must be finite and positive.")
    return np.array([-tau, eta / (1.0 + eta), 1.0 / (1.0 + eta)])


def paper_example_3_signed_l1_prices(tau: float, eta: float) -> FloatArray:
    """Convert the example's goods-sum convention to core signed-L1 prices."""

    table_prices = paper_example_3_table_prices(tau, eta)
    return PaperTaxConvention.to_paper_l1(table_prices, np.array([tau])).prices


def paper_example_3_allocations(tau: float, eta: float) -> FloatArray:
    """Evaluate the Supplement Section 3.3 closed-form demand equations."""

    _, p1, p2 = paper_example_3_table_prices(tau, eta)
    r = paper_example_3_r()
    x01 = 5.0 * tau * (1.0 + eta) / eta
    x02 = tau * (1.0 + eta)
    income_goods_1 = (
        2.0 * p1 + r * p2 - 0.5 * tau * (x02 - x01)
    )
    income_goods_2 = (
        r * p1 + 2.0 * p2 - 0.5 * tau * (x01 - x02)
    )
    x21 = eta ** (1.0 / 9.0)
    x12 = eta ** (-1.0 / 9.0)
    x11 = income_goods_1 / p1 - (p2 / p1) ** (8.0 / 9.0)
    x22 = income_goods_2 / p2 - (p1 / p2) ** (8.0 / 9.0)
    return np.array([[x01, x11, x21], [x02, x12, x22]])


def paper_example_3_good_1_excess(tau: float, eta: float) -> float:
    """Return the scalar root equation used by the Supplement."""

    allocations = paper_example_3_allocations(tau, eta)
    total_endowment = 2.0 + paper_example_3_r()
    return float(np.sum(allocations[:, 1]) - total_endowment)


def paper_example_3_reduction_percent(tau: float, eta: float) -> float:
    """Return consumption of commodity 0 as a percent of its 0.4 endowment."""

    allocations = paper_example_3_allocations(tau, eta)
    return float(100.0 * np.sum(allocations[:, 0]) / 0.4)


def build_paper_example_4_tax_economy(tax_rate: float) -> EmissionTaxEconomy:
    """Build the one-agent linear-technology tax economy in Example 4."""

    tax = float(tax_rate)
    if not np.isfinite(tax) or tax < 0.0:
        raise ValueError("Example 4 tax rate must be finite and nonnegative.")
    commodities = (
        Commodity("CO2 emissions", 0, ClearingRule.FREE_DISPOSAL, CommodityKind.BAD),
        Commodity("coal", 1, ClearingRule.EXACT, CommodityKind.GOOD),
        Commodity("electricity", 2, ClearingRule.EXACT, CommodityKind.GOOD),
    )
    consumer = Consumer(
        "omega",
        SingleGoodLinearUtility(3, 2, fixed_zero_indexes=(0,)),
        np.array([0.0, 1.0, 0.0]),
        consumption_set=_paper_consumption_set(),
    )
    ownership = FirmOwnership({"omega": 1.0})
    firms = (
        Firm(
            "firm_1",
            LinearRayTechnology(np.array([1.0, -1.0, 1.0])),
            ownership,
        ),
        Firm(
            "firm_2",
            LinearRayTechnology(np.array([-2.0, 0.0, -1.0])),
            ownership,
        ),
    )
    return EmissionTaxEconomy(
        ProductionEconomy(commodities, (consumer,), firms),
        EmissionTaxPolicy(
            regulated_count=1,
            tax_rates=np.array([tax]),
            rebate_shares={"omega": 1.0},
            unregulated_rules=(ClearingRule.EXACT, ClearingRule.EXACT),
        ),
    )


def paper_example_4_coordinates(
    tax_rate: float, emissions: float | None = None
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Return the candidates in Supplement Claims 5.1-5.3."""

    tax = float(tax_rate)
    if tax < 0.0 or tax > 0.25:
        raise ValueError("Example 4 candidate formulas require 0<=t<=1/4.")
    if tax < 0.25:
        if emissions is not None and not np.isclose(emissions, 1.0):
            raise ValueError("Every Example 4 equilibrium below t=1/4 emits one.")
        v = 1.0
        prices = np.array([-tax, 0.5 - tax, 0.5])
        allocations = np.array([[0.0, 0.0, 1.0]])
        plans = np.array([[1.0, -1.0, 1.0], [0.0, 0.0, 0.0]])
        return prices, allocations, plans
    if emissions is None:
        raise ValueError("At t=1/4 an emissions branch value v is required.")
    v = float(emissions)
    if not np.isfinite(v) or not 0.0 <= v <= 1.0:
        raise ValueError("Example 4 boundary emissions must lie in [0,1].")
    prices = np.array([-0.25, 0.25, 0.5])
    allocations = np.array([[0.0, 0.0, (1.0 + v) / 2.0]])
    plans = np.array(
        [[1.0, -1.0, 1.0], [v - 1.0, 0.0, (v - 1.0) / 2.0]]
    )
    return prices, allocations, plans
