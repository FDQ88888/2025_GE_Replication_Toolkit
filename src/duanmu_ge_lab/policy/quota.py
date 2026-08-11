"""Quota property-rights accounting for Anderson-Duanmu economies."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import ZeroTechnology
from duanmu_ge_lab.core.production_economy import ProductionEconomy

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class QuotaFirmProfitBreakdown:
    """Operating and quota-right components of one firm's paper profit."""

    firm_id: str
    operating_profit: float
    quota_profit: float

    def __post_init__(self) -> None:
        if not self.firm_id.strip():
            raise ValueError("Quota profit firm id must be non-empty.")
        if not np.isfinite(self.operating_profit) or not np.isfinite(self.quota_profit):
            raise ValueError("Quota firm profit components must be finite.")

    @property
    def total_profit(self) -> float:
        """Return paper profit ``p dot y_j + proj_k(p) dot m^(j)``."""

        return float(self.operating_profit + self.quota_profit)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable accounting data."""

        return {
            "firm_id": self.firm_id,
            "operating_profit": self.operating_profit,
            "quota_profit": self.quota_profit,
            "total_profit": self.total_profit,
        }


@dataclass(frozen=True, slots=True)
class QuotaPolicy:
    """Paper quota assignments and the compliance region ``Z(m)``.

    The first ``regulated_count`` existing commodity coordinates are regulated.
    Each ``m^(j)`` is nonpositive and is the negative of firm ``j``'s quota. No
    permit commodity is created.
    """

    regulated_count: int
    firm_quotas: Mapping[str, Sequence[float] | FloatArray]
    unregulated_rules: Sequence[ClearingRule]
    government_firm_id: str = "firm_0"

    def __post_init__(self) -> None:
        if self.regulated_count < 1:
            raise ValueError("A quota policy must regulate at least one commodity.")
        if not self.government_firm_id.strip():
            raise ValueError("Government firm id must be non-empty.")
        copied: dict[str, FloatArray] = {}
        for firm_id, quota in self.firm_quotas.items():
            if not firm_id.strip():
                raise ValueError("Quota firm ids must be non-empty.")
            array = np.asarray(quota, dtype=float)
            if array.shape != (self.regulated_count,):
                raise ValueError(
                    "Every firm quota vector must have shape "
                    f"({self.regulated_count},)."
                )
            if not np.all(np.isfinite(array)):
                raise ValueError("Firm quota vectors must contain only finite values.")
            if np.any(array > 0.0):
                raise ValueError("Each m^(j) must be nonpositive, as in Definition 3.2.")
            copied[firm_id] = array.copy()
        if not copied:
            raise ValueError("Quota policy must assign m^(j) to every firm.")
        rules = tuple(ClearingRule(rule) for rule in self.unregulated_rules)
        object.__setattr__(self, "firm_quotas", MappingProxyType(copied))
        object.__setattr__(self, "unregulated_rules", rules)

    @property
    def n_goods(self) -> int:
        """Return the full commodity dimension represented by ``Z(m)``."""

        return self.regulated_count + len(self.unregulated_rules)

    @property
    def total_m(self) -> FloatArray:
        """Return ``m=sum_j m^(j)`` without changing signs."""

        return np.sum(np.vstack(tuple(self.firm_quotas.values())), axis=0)

    def quota_prices(self, prices: Sequence[float] | FloatArray) -> FloatArray:
        """Return paper quota prices ``q=-proj_k(p)``."""

        price_array = self._validated_prices(prices)
        return -price_array[: self.regulated_count]

    def quota_profit_term(
        self, firm_id: str, prices: Sequence[float] | FloatArray
    ) -> float:
        """Return ``proj_k(p) dot m^(j)`` for one firm."""

        if firm_id not in self.firm_quotas:
            raise KeyError(f"No quota assignment for firm {firm_id!r}.")
        price_array = self._validated_prices(prices)
        return float(
            np.dot(
                price_array[: self.regulated_count],
                np.asarray(self.firm_quotas[firm_id]),
            )
        )

    def compliance_violations(
        self, resource_residual: Sequence[float] | FloatArray
    ) -> FloatArray:
        """Return coordinate violations of membership in ``Z(m)``."""

        residual = np.asarray(resource_residual, dtype=float)
        if residual.shape != (self.n_goods,) or not np.all(np.isfinite(residual)):
            raise ValueError(
                f"Resource residual must be finite with shape ({self.n_goods},)."
            )
        violations = np.zeros(self.n_goods, dtype=float)
        violations[: self.regulated_count] = np.abs(
            residual[: self.regulated_count] - self.total_m
        )
        for offset, rule in enumerate(self.unregulated_rules):
            index = self.regulated_count + offset
            if rule is ClearingRule.EXACT:
                violations[index] = abs(float(residual[index]))
            else:
                violations[index] = max(0.0, float(residual[index]))
        return violations

    def target_vector(self) -> FloatArray:
        """Return the equality target, with zeros on unregulated coordinates."""

        return np.concatenate(
            [self.total_m, np.zeros(len(self.unregulated_rules), dtype=float)]
        )

    def _validated_prices(
        self, prices: Sequence[float] | FloatArray
    ) -> FloatArray:
        array = np.asarray(prices, dtype=float)
        if array.shape != (self.n_goods,) or not np.all(np.isfinite(array)):
            raise ValueError(f"Prices must be finite with shape ({self.n_goods},).")
        return array

    def to_dict(self) -> dict[str, Any]:
        """Return the signed quota assignments and compliance specification."""

        return {
            "regulated_count": self.regulated_count,
            "government_firm_id": self.government_firm_id,
            "firm_m_vectors": {
                firm_id: np.asarray(quota).tolist()
                for firm_id, quota in self.firm_quotas.items()
            },
            "total_m": self.total_m.tolist(),
            "quota_is_negative_total_m": (-self.total_m).tolist(),
            "unregulated_rules": [rule.value for rule in self.unregulated_rules],
            "introduces_permit_commodity": False,
        }


@dataclass(frozen=True, slots=True)
class QuotaEconomy:
    """Production economy plus one authoritative quota-accounting layer."""

    production_economy: ProductionEconomy
    policy: QuotaPolicy

    def __post_init__(self) -> None:
        economy = self.production_economy
        policy = self.policy
        if policy.n_goods != economy.n_goods:
            raise ValueError("Quota policy dimension does not match the economy.")
        firm_ids = {firm.id for firm in economy.firms}
        if set(policy.firm_quotas) != firm_ids:
            missing = sorted(firm_ids - set(policy.firm_quotas))
            extra = sorted(set(policy.firm_quotas) - firm_ids)
            raise ValueError(
                f"Quota assignments must exactly match firms; missing={missing}, extra={extra}."
            )
        government = next(
            (firm for firm in economy.firms if firm.id == policy.government_firm_id),
            None,
        )
        if government is None:
            raise ValueError("Quota economy is missing its government firm.")
        if not isinstance(government.technology, ZeroTechnology):
            raise ValueError("The government firm must have singleton technology Y_0={0}.")
        for offset, rule in enumerate(policy.unregulated_rules):
            index = policy.regulated_count + offset
            if economy.commodities[index].clearing_rule is not rule:
                raise ValueError(
                    "Commodity clearing metadata conflicts with quota compliance rules."
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

    def optimal_firm_plans(self, prices: Sequence[float] | FloatArray) -> FloatArray:
        """Return one production optimum per firm; quota terms are plan-constant."""

        return self.production_economy.optimal_firm_plans(prices)

    def firm_profit_breakdowns(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> dict[str, QuotaFirmProfitBreakdown]:
        """Compute all paper firm profits from one accounting source."""

        operating = self.production_economy.firm_profits(prices, firm_plans)
        return {
            firm.id: QuotaFirmProfitBreakdown(
                firm_id=firm.id,
                operating_profit=float(operating[index]),
                quota_profit=self.policy.quota_profit_term(firm.id, prices),
            )
            for index, firm in enumerate(self.firms)
        }

    def income_breakdowns(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> dict[str, IncomeBreakdown]:
        """Compute budgets using the same profit decomposition as diagnostics."""

        profit_parts = self.firm_profit_breakdowns(prices, firm_plans)
        breakdowns: dict[str, IncomeBreakdown] = {}
        for consumer in self.consumers:
            operating_dividends = sum(
                firm.ownership.share_of(consumer.id)
                * profit_parts[firm.id].operating_profit
                for firm in self.firms
            )
            quota_dividends = sum(
                firm.ownership.share_of(consumer.id)
                * profit_parts[firm.id].quota_profit
                for firm in self.firms
            )
            breakdowns[consumer.id] = IncomeBreakdown(
                endowment_income=consumer.wealth(prices),
                firm_dividend_income=float(operating_dividends),
                policy_income=float(quota_dividends),
            )
        return breakdowns

    def individual_demands(
        self,
        prices: Sequence[float] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> FloatArray:
        """Optimize consumers at quota-accounted incomes."""

        incomes = self.income_breakdowns(prices, firm_plans)
        return np.vstack(
            [
                consumer.demand_at_income(prices, incomes[consumer.id].total_income)
                for consumer in self.consumers
            ]
        )

    def candidate_resource_residual(
        self,
        allocations: Sequence[Sequence[float]] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> FloatArray:
        """Return candidate ``sum x-sum e-sum y`` before the ``Z(m)`` check."""

        return self.production_economy.candidate_resource_residual(
            allocations, firm_plans
        )

    def quota_adjusted_walras_residual(
        self,
        prices: Sequence[float] | FloatArray,
        allocations: Sequence[Sequence[float]] | FloatArray,
        firm_plans: Sequence[Sequence[float]] | FloatArray,
    ) -> float:
        """Return ``p dot resource_residual - proj_k(p) dot m``."""

        price_array = self.policy._validated_prices(prices)
        residual = self.candidate_resource_residual(allocations, firm_plans)
        quota_value = float(
            np.dot(price_array[: self.policy.regulated_count], self.policy.total_m)
        )
        return float(np.dot(price_array, residual) - quota_value)

    def aggregate_endowment(self) -> FloatArray:
        return self.production_economy.aggregate_endowment()

    def aggregate_allocations(
        self, allocations: Sequence[Sequence[float]] | FloatArray
    ) -> FloatArray:
        return self.production_economy.aggregate_allocations(allocations)

    def ownership_adding_up_error(self, firm) -> float:
        return self.production_economy.ownership_adding_up_error(firm)

