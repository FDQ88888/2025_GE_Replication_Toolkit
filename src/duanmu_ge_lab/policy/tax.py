"""Emission-tax accounting and quota-tax mappings from the paper."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import Firm, FirmOwnership, ZeroTechnology
from duanmu_ge_lab.core.production_economy import ProductionEconomy
from duanmu_ge_lab.equilibrium.normalization import FixedNumeraire
from duanmu_ge_lab.policy.quota import QuotaEconomy, QuotaPolicy

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class TaxCoordinateConversion:
    """One positive rescaling of prices and tax rates."""

    prices: FloatArray
    tax_rates: FloatArray
    scale: float
    source: str
    target: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "prices": self.prices.tolist(),
            "tax_rates": self.tax_rates.tolist(),
            "scale": self.scale,
            "source": self.source,
            "target": self.target,
        }


class PaperTaxConvention:
    """Convert `(p,t)` together while preserving `proj_k(p)=-t`."""

    @staticmethod
    def to_fixed_numeraire(
        paper_prices: Sequence[float] | FloatArray,
        paper_tax_rates: Sequence[float] | FloatArray,
        normalization: FixedNumeraire,
    ) -> TaxCoordinateConversion:
        prices, taxes = PaperTaxConvention._validated_pair(
            paper_prices, paper_tax_rates
        )
        l1 = float(np.sum(np.abs(prices)))
        if not np.isclose(l1, 1.0, atol=1e-12, rtol=0.0):
            raise ValueError("Paper tax prices must be signed-L1 normalized.")
        if normalization.index >= prices.size:
            raise ValueError("Numeraire index is outside the price vector.")
        coordinate = float(prices[normalization.index])
        if coordinate == 0.0:
            raise ValueError("Cannot use a zero price as numeraire.")
        scale = normalization.value / coordinate
        if scale <= 0.0:
            raise ValueError("Paper-to-numeraire conversion requires a positive scale.")
        converted_prices = scale * prices
        converted_taxes = scale * taxes
        normalization.encode(converted_prices)
        PaperTaxConvention._check_price_tax_identity(
            converted_prices, converted_taxes
        )
        return TaxCoordinateConversion(
            prices=converted_prices,
            tax_rates=converted_taxes,
            scale=float(scale),
            source="paper_signed_l1",
            target=f"fixed_numeraire_index_{normalization.index}",
        )

    @staticmethod
    def to_paper_l1(
        internal_prices: Sequence[float] | FloatArray,
        internal_tax_rates: Sequence[float] | FloatArray,
    ) -> TaxCoordinateConversion:
        prices, taxes = PaperTaxConvention._validated_pair(
            internal_prices, internal_tax_rates
        )
        norm = float(np.sum(np.abs(prices)))
        if norm <= 0.0:
            raise ValueError("Cannot normalize the zero price vector.")
        scale = 1.0 / norm
        converted_prices = scale * prices
        converted_taxes = scale * taxes
        PaperTaxConvention._check_price_tax_identity(
            converted_prices, converted_taxes
        )
        return TaxCoordinateConversion(
            prices=converted_prices,
            tax_rates=converted_taxes,
            scale=scale,
            source="internal_positive_scale",
            target="paper_signed_l1",
        )

    @staticmethod
    def _validated_pair(
        prices: Sequence[float] | FloatArray,
        tax_rates: Sequence[float] | FloatArray,
    ) -> tuple[FloatArray, FloatArray]:
        price_array = np.asarray(prices, dtype=float)
        tax_array = np.asarray(tax_rates, dtype=float)
        if price_array.ndim != 1 or price_array.size == 0:
            raise ValueError("Prices must be a non-empty 1D vector.")
        if tax_array.ndim != 1 or tax_array.size == 0:
            raise ValueError("Tax rates must be a non-empty 1D vector.")
        if tax_array.size > price_array.size:
            raise ValueError("Tax dimension cannot exceed the commodity dimension.")
        if not np.all(np.isfinite(price_array)) or not np.all(np.isfinite(tax_array)):
            raise ValueError("Prices and tax rates must contain only finite values.")
        if np.any(tax_array < 0.0):
            raise ValueError("Emission tax rates must be nonnegative.")
        PaperTaxConvention._check_price_tax_identity(price_array, tax_array)
        return price_array, tax_array

    @staticmethod
    def _check_price_tax_identity(prices: FloatArray, taxes: FloatArray) -> None:
        if not np.allclose(
            prices[: taxes.size], -taxes, atol=1e-12, rtol=0.0
        ):
            raise ValueError("Regulated prices must satisfy proj_k(p)=-t.")


@dataclass(frozen=True, slots=True)
class EmissionTaxPolicy:
    """Tax rates, rebates, and the paper compliance region `V`."""

    regulated_count: int
    tax_rates: Sequence[float] | FloatArray
    rebate_shares: Mapping[str, float]
    unregulated_rules: Sequence[ClearingRule]

    def __post_init__(self) -> None:
        if self.regulated_count < 1:
            raise ValueError("An emission tax must regulate at least one commodity.")
        taxes = np.asarray(self.tax_rates, dtype=float)
        if taxes.shape != (self.regulated_count,):
            raise ValueError(
                f"Tax rates must have shape ({self.regulated_count},)."
            )
        if not np.all(np.isfinite(taxes)) or np.any(taxes < 0.0):
            raise ValueError("Tax rates must be finite and nonnegative.")
        rebates = dict(self.rebate_shares)
        if not rebates:
            raise ValueError("A tax policy must define rebate shares.")
        for consumer_id, share in rebates.items():
            if not consumer_id.strip():
                raise ValueError("Rebate consumer ids must be non-empty.")
            if not np.isfinite(share) or share < 0.0:
                raise ValueError("Rebate shares must be finite and nonnegative.")
        rules = tuple(ClearingRule(rule) for rule in self.unregulated_rules)
        object.__setattr__(self, "tax_rates", taxes.copy())
        object.__setattr__(self, "rebate_shares", MappingProxyType(rebates))
        object.__setattr__(self, "unregulated_rules", rules)

    @property
    def n_goods(self) -> int:
        return self.regulated_count + len(self.unregulated_rules)

    def price_constraint_violations(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return `abs(proj_k(p)+t)` without modifying either vector."""

        price_array = self._validated_prices(prices)
        return np.abs(price_array[: self.regulated_count] + self.tax_rates)

    def total_net_emissions(
        self, resource_residual: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return paper `C(x,y)=-proj_k(r(x,y))`."""

        residual = self._validated_residual(resource_residual)
        return -residual[: self.regulated_count]

    def tax_revenue(
        self, resource_residual: Sequence[float] | FloatArray
    ) -> float:
        """Return `t dot C(x,y)`."""

        return float(np.dot(self.tax_rates, self.total_net_emissions(resource_residual)))

    def compliance_violations(
        self, resource_residual: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return coordinate violations of membership in `V`."""

        residual = self._validated_residual(resource_residual)
        violations = np.zeros(self.n_goods, dtype=float)
        violations[: self.regulated_count] = np.maximum(
            residual[: self.regulated_count], 0.0
        )
        for offset, rule in enumerate(self.unregulated_rules):
            index = self.regulated_count + offset
            violations[index] = (
                abs(float(residual[index]))
                if rule is ClearingRule.EXACT
                else max(0.0, float(residual[index]))
            )
        return violations

    def _validated_prices(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(prices, dtype=float)
        if array.shape != (self.n_goods,) or not np.all(np.isfinite(array)):
            raise ValueError(f"Prices must be finite with shape ({self.n_goods},).")
        return array

    def _validated_residual(
        self, residual: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(residual, dtype=float)
        if array.shape != (self.n_goods,) or not np.all(np.isfinite(array)):
            raise ValueError(
                f"Resource residual must be finite with shape ({self.n_goods},)."
            )
        return array

    def to_dict(self) -> dict[str, Any]:
        return {
            "regulated_count": self.regulated_count,
            "tax_rates": np.asarray(self.tax_rates).tolist(),
            "rebate_shares": dict(self.rebate_shares),
            "unregulated_rules": [rule.value for rule in self.unregulated_rules],
            "price_constraint": "proj_k(p) = -t",
        }


@dataclass(frozen=True, slots=True)
class EmissionTaxEconomy:
    """Production economy with candidate-dependent tax rebates."""

    production_economy: ProductionEconomy
    policy: EmissionTaxPolicy

    def __post_init__(self) -> None:
        if self.policy.n_goods != self.production_economy.n_goods:
            raise ValueError("Emission tax policy dimension does not match economy.")
        consumer_ids = {consumer.id for consumer in self.production_economy.consumers}
        if set(self.policy.rebate_shares) != consumer_ids:
            raise ValueError("Rebate shares must exactly match economy consumers.")
        weighted_total = sum(
            consumer.population_weight
            * self.policy.rebate_shares[consumer.id]
            for consumer in self.production_economy.consumers
        )
        if not np.isclose(weighted_total, 1.0, atol=1e-12, rtol=0.0):
            raise ValueError(
                "Population-weighted rebate shares must add to one."
            )
        for offset, rule in enumerate(self.policy.unregulated_rules):
            index = self.policy.regulated_count + offset
            if self.production_economy.commodities[index].clearing_rule is not rule:
                raise ValueError(
                    "Commodity clearing metadata conflicts with tax compliance rules."
                )

    @property
    def n_goods(self) -> int:
        return self.production_economy.n_goods

    @property
    def n_consumers(self) -> int:
        return self.production_economy.n_consumers

    @property
    def n_firms(self) -> int:
        return self.production_economy.n_firms

    @property
    def consumers(self):
        return self.production_economy.consumers

    @property
    def firms(self):
        return self.production_economy.firms

    def candidate_resource_residual(self, allocations, firm_plans) -> FloatArray:
        return self.production_economy.candidate_resource_residual(
            allocations, firm_plans
        )

    def total_net_emissions(self, allocations, firm_plans) -> FloatArray:
        return self.policy.total_net_emissions(
            self.candidate_resource_residual(allocations, firm_plans)
        )

    def tax_revenue(self, allocations, firm_plans) -> float:
        return self.policy.tax_revenue(
            self.candidate_resource_residual(allocations, firm_plans)
        )

    def firm_profits(self, prices, firm_plans) -> FloatArray:
        return self.production_economy.firm_profits(prices, firm_plans)

    def income_breakdowns(
        self, prices, allocations, firm_plans
    ) -> dict[str, IncomeBreakdown]:
        """Compute budgets from one candidate-dependent tax accounting source."""

        profits = self.firm_profits(prices, firm_plans)
        revenue = self.tax_revenue(allocations, firm_plans)
        result: dict[str, IncomeBreakdown] = {}
        for consumer in self.consumers:
            dividends = sum(
                firm.ownership.share_of(consumer.id) * profits[index]
                for index, firm in enumerate(self.firms)
            )
            result[consumer.id] = IncomeBreakdown(
                endowment_income=consumer.wealth(prices),
                firm_dividend_income=float(dividends),
                policy_income=float(
                    self.policy.rebate_shares[consumer.id] * revenue
                ),
            )
        return result

    def individual_demands(self, prices, allocations, firm_plans) -> FloatArray:
        incomes = self.income_breakdowns(prices, allocations, firm_plans)
        return np.vstack(
            [
                consumer.demand_at_income(prices, incomes[consumer.id].total_income)
                for consumer in self.consumers
            ]
        )

    def aggregate_allocations(self, allocations) -> FloatArray:
        return self.production_economy.aggregate_allocations(allocations)

    def aggregate_endowment(self) -> FloatArray:
        return self.production_economy.aggregate_endowment()

    def ownership_adding_up_error(self, firm: Firm) -> float:
        return self.production_economy.ownership_adding_up_error(firm)

    def rebate_adjusted_walras_residual(
        self, prices, allocations, firm_plans
    ) -> float:
        residual = self.candidate_resource_residual(allocations, firm_plans)
        revenue = self.policy.tax_revenue(residual)
        return float(np.dot(np.asarray(prices, dtype=float), residual) - revenue)


def map_quota_to_emission_tax(
    quota_economy: QuotaEconomy,
    equilibrium_prices: Sequence[float] | FloatArray,
) -> EmissionTaxEconomy:
    """Construct the Theorem 3 tax economy for one quota-equilibrium price."""

    prices = quota_economy.policy._validated_prices(equilibrium_prices)
    government_id = quota_economy.policy.government_firm_id
    private_firms = tuple(
        firm for firm in quota_economy.firms if firm.id != government_id
    )
    denominator = float(
        np.dot(
            prices[: quota_economy.policy.regulated_count],
            quota_economy.policy.total_m,
        )
    )
    if denominator == 0.0:
        raise ValueError("Theorem 3 rebate formula has zero total quota value.")
    rebate_shares: dict[str, float] = {}
    for consumer in quota_economy.consumers:
        numerator = sum(
            firm.ownership.share_of(consumer.id)
            * quota_economy.policy.quota_profit_term(firm.id, prices)
            for firm in quota_economy.firms
        )
        rebate_shares[consumer.id] = float(numerator / denominator)
    tax_policy = EmissionTaxPolicy(
        regulated_count=quota_economy.policy.regulated_count,
        tax_rates=-prices[: quota_economy.policy.regulated_count],
        rebate_shares=rebate_shares,
        unregulated_rules=quota_economy.policy.unregulated_rules,
    )
    return EmissionTaxEconomy(
        ProductionEconomy(
            quota_economy.production_economy.commodities,
            quota_economy.consumers,
            private_firms,
        ),
        tax_policy,
    )


def map_emission_tax_to_global_quota(
    tax_economy: EmissionTaxEconomy,
    allocations,
    firm_plans,
    government_firm_id: str = "firm_0",
) -> QuotaEconomy:
    """Construct Theorem 4's global quota economy at one tax candidate."""

    if any(firm.id == government_firm_id for firm in tax_economy.firms):
        raise ValueError("Government firm id collides with a private firm id.")
    emissions = tax_economy.total_net_emissions(allocations, firm_plans)
    government = Firm(
        government_firm_id,
        ZeroTechnology(tax_economy.n_goods),
        FirmOwnership(dict(tax_economy.policy.rebate_shares)),
    )
    firms = (government, *tax_economy.firms)
    quotas = {government_firm_id: -emissions}
    quotas.update(
        {
            firm.id: np.zeros(tax_economy.policy.regulated_count, dtype=float)
            for firm in tax_economy.firms
        }
    )
    return QuotaEconomy(
        ProductionEconomy(
            tax_economy.production_economy.commodities,
            tax_economy.consumers,
            firms,
        ),
        QuotaPolicy(
            regulated_count=tax_economy.policy.regulated_count,
            firm_quotas=quotas,
            unregulated_rules=tax_economy.policy.unregulated_rules,
            government_firm_id=government_firm_id,
        ),
    )
