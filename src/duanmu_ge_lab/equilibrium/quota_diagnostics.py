"""Independent diagnostics for Anderson-Duanmu quota equilibria."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from duanmu_ge_lab.core.consumer import ConsumerOptimalityResult
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import FirmOptimalityResult
from duanmu_ge_lab.equilibrium.candidate import (
    CandidateClassification,
    QuotaEquilibriumCandidate,
)
from duanmu_ge_lab.equilibrium.diagnostics import NumericalTolerances
from duanmu_ge_lab.equilibrium.normalization import normalize_signed_l1
from duanmu_ge_lab.equilibrium.prices import PriceSignRestrictions
from duanmu_ge_lab.policy.quota import (
    QuotaEconomy,
    QuotaFirmProfitBreakdown,
)


@dataclass(frozen=True, slots=True)
class QuotaDiagnosticsReport:
    """Complete quota-candidate audit with solver caches kept non-authoritative."""

    classification: CandidateClassification
    passed: bool
    checks: dict[str, bool]
    errors: dict[str, float]
    signed_l1_prices: list[float]
    quota_prices: list[float]
    total_m: list[float]
    candidate_aggregate_allocation: list[float]
    candidate_aggregate_production: list[float]
    candidate_resource_residual: list[float]
    compliance_violations: list[float]
    raw_walras_value: float
    quota_value: float
    quota_adjusted_walras_residual: float
    firm_profit_breakdowns: dict[str, QuotaFirmProfitBreakdown]
    consumer_income_breakdowns: dict[str, IncomeBreakdown]
    budget_residuals: dict[str, float]
    consumer_optimality_results: dict[str, ConsumerOptimalityResult]
    firm_optimality_results: dict[str, FirmOptimalityResult]
    ownership_adding_up_errors: dict[str, float]
    cache_errors: dict[str, float]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable diagnostics."""

        return {
            "classification": self.classification.value,
            "passed": self.passed,
            "checks": dict(self.checks),
            "errors": dict(self.errors),
            "signed_l1_prices": list(self.signed_l1_prices),
            "quota_prices_q_equals_negative_projected_p": list(self.quota_prices),
            "total_m_equals_sum_firm_m": list(self.total_m),
            "candidate_aggregate_allocation": list(
                self.candidate_aggregate_allocation
            ),
            "candidate_aggregate_production": list(
                self.candidate_aggregate_production
            ),
            "candidate_resource_residual": list(self.candidate_resource_residual),
            "compliance_violations": list(self.compliance_violations),
            "raw_walras_value_p_dot_resource_residual": self.raw_walras_value,
            "quota_value_projected_p_dot_m": self.quota_value,
            "quota_adjusted_walras_residual": self.quota_adjusted_walras_residual,
            "firm_profit_breakdowns": {
                firm_id: breakdown.to_dict()
                for firm_id, breakdown in self.firm_profit_breakdowns.items()
            },
            "consumer_income_breakdowns": {
                consumer_id: breakdown.to_dict()
                for consumer_id, breakdown in self.consumer_income_breakdowns.items()
            },
            "budget_residuals": dict(self.budget_residuals),
            "consumer_optimality_results": {
                consumer_id: result.to_dict()
                for consumer_id, result in self.consumer_optimality_results.items()
            },
            "firm_optimality_results": {
                firm_id: result.to_dict()
                for firm_id, result in self.firm_optimality_results.items()
            },
            "ownership_adding_up_errors": dict(
                self.ownership_adding_up_errors
            ),
            "cache_errors": dict(self.cache_errors),
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class QuotaEquilibriumDiagnostics:
    """Verify Definition 3.5 and all associated quota-income accounting."""

    economy: QuotaEconomy
    tolerances: NumericalTolerances = NumericalTolerances()
    price_sign_restrictions: PriceSignRestrictions | None = None

    def evaluate(
        self, candidate: QuotaEquilibriumCandidate
    ) -> QuotaDiagnosticsReport:
        """Classify a candidate only after independent recomputation."""

        notes: list[str] = []
        prices = np.asarray(candidate.prices, dtype=float)
        allocations = np.asarray(candidate.allocations, dtype=float)
        plans = np.asarray(candidate.firm_plans, dtype=float)
        expected_shapes = (
            prices.shape == (self.economy.n_goods,)
            and allocations.shape
            == (self.economy.n_consumers, self.economy.n_goods)
            and plans.shape == (self.economy.n_firms, self.economy.n_goods)
        )
        authoritative_finite = bool(
            expected_shapes
            and np.all(np.isfinite(prices))
            and np.all(np.isfinite(allocations))
            and np.all(np.isfinite(plans))
        )
        if not authoritative_finite:
            notes.append(
                "Authoritative candidate coordinates have invalid shapes or nonfinite values."
            )
            return self._invalid_report(candidate, notes)

        normalization_error = abs(float(np.sum(np.abs(prices))) - 1.0)
        signed_l1_prices = normalize_signed_l1(prices).tolist()
        price_sign_violation = 0.0
        if self.price_sign_restrictions is not None:
            if self.price_sign_restrictions.n_goods != self.economy.n_goods:
                price_sign_violation = float("inf")
                notes.append("Price-sign restriction dimension does not match economy.")
            else:
                price_sign_violation = self.price_sign_restrictions.max_violation(
                    prices, self.tolerances.price_sign_tol
                )

        aggregate_allocation = self.economy.aggregate_allocations(allocations)
        aggregate_endowment = self.economy.aggregate_endowment()
        aggregate_production = np.sum(plans, axis=0)
        resource_residual = self.economy.candidate_resource_residual(
            allocations, plans
        )
        compliance = self.economy.policy.compliance_violations(resource_residual)
        market_limits = self.tolerances.market_abs_tol + (
            self.tolerances.market_rel_tol
            * np.maximum(
                np.abs(self.economy.policy.target_vector()),
                np.maximum(np.abs(aggregate_allocation), np.abs(aggregate_production)),
            )
        )
        max_compliance_ratio = float(np.max(compliance / market_limits))

        quota_prices = self.economy.policy.quota_prices(prices)
        profit_parts = self.economy.firm_profit_breakdowns(prices, plans)
        incomes = self.economy.income_breakdowns(prices, plans)
        raw_walras = float(np.dot(prices, resource_residual))
        quota_value = float(
            np.dot(
                prices[: self.economy.policy.regulated_count],
                self.economy.policy.total_m,
            )
        )
        adjusted_walras = raw_walras - quota_value

        ownership_errors = {
            firm.id: self.economy.ownership_adding_up_error(firm)
            for firm in self.economy.firms
        }
        firm_results: dict[str, FirmOptimalityResult] = {}
        firm_oracle_available = True
        for index, firm in enumerate(self.economy.firms):
            try:
                firm_results[firm.id] = firm.evaluate_optimality(prices, plans[index])
            except (ValueError, ArithmeticError) as exc:
                firm_oracle_available = False
                notes.append(f"Firm {firm.id} optimality oracle failed: {exc}")

        budget_residuals: dict[str, float] = {}
        consumer_results: dict[str, ConsumerOptimalityResult] = {}
        consumer_oracle_available = True
        for index, consumer in enumerate(self.economy.consumers):
            income = incomes[consumer.id].total_income
            try:
                budget_residuals[consumer.id] = consumer.budget_residual_at_income(
                    prices, allocations[index], income
                )
                consumer_results[consumer.id] = consumer.evaluate_optimality_at_income(
                    prices, allocations[index], income
                )
            except (ValueError, ArithmeticError) as exc:
                consumer_oracle_available = False
                notes.append(f"Consumer {consumer.id} demand oracle failed: {exc}")

        cache_errors = self._cache_errors(
            candidate=candidate,
            aggregate_allocation=aggregate_allocation,
            aggregate_endowment=aggregate_endowment,
            aggregate_production=aggregate_production,
            resource_residual=resource_residual,
            quota_prices=quota_prices,
            profit_parts=profit_parts,
            incomes=incomes,
        )

        max_ownership = max(ownership_errors.values(), default=float("inf"))
        max_firm_feasibility = max(
            (result.feasibility_violation for result in firm_results.values()),
            default=float("inf"),
        )
        max_profit_gap = max(
            (max(0.0, result.profit_gap) for result in firm_results.values()),
            default=float("inf"),
        )
        government_index = next(
            index
            for index, firm in enumerate(self.economy.firms)
            if firm.id == self.economy.policy.government_firm_id
        )
        government_plan_error = float(np.max(np.abs(plans[government_index])))
        max_budget_violation = max(
            (max(0.0, -value) for value in budget_residuals.values()),
            default=float("inf"),
        )
        max_budget_gap = max(
            (abs(value) for value in budget_residuals.values()),
            default=float("inf"),
        )
        max_consumer_feasibility = max(
            (
                result.feasibility_violation
                for result in consumer_results.values()
            ),
            default=float("inf"),
        )
        max_utility_gap = max(
            (
                max(0.0, result.utility_gap)
                for result in consumer_results.values()
                if result.utility_gap is not None
            ),
            default=float("inf"),
        )
        max_cache_error = max(cache_errors.values(), default=float("inf"))

        checks = {
            "solver_success": bool(candidate.solver_success),
            "finite_authoritative_coordinates": authoritative_finite,
            "signed_l1_normalization": (
                normalization_error <= self.tolerances.normalization_tol
            ),
            "price_sign_restrictions": price_sign_violation == 0.0,
            "quota_price_identity": (
                cache_errors["quota_prices"] <= self.tolerances.accounting_tol
            ),
            "ownership_share_adding_up": (
                max_ownership <= self.tolerances.ownership_tol
            ),
            "government_firm_zero_production": (
                government_plan_error
                <= self.tolerances.production_feasibility_tol
            ),
            "firm_feasibility": (
                max_firm_feasibility
                <= self.tolerances.production_feasibility_tol
            ),
            "firm_optimality_oracle_available": firm_oracle_available,
            "firm_profit_maximization": (
                firm_oracle_available
                and max_profit_gap <= self.tolerances.profit_tol
            ),
            "consumer_optimality_oracle_available": consumer_oracle_available,
            "consumer_feasibility": (
                consumer_oracle_available
                and max_consumer_feasibility <= self.tolerances.feasibility_tol
            ),
            "budget_feasibility": (
                consumer_oracle_available
                and max_budget_violation <= self.tolerances.budget_tol
            ),
            "budget_exhaustion": (
                consumer_oracle_available
                and max_budget_gap <= self.tolerances.budget_tol
            ),
            "consumer_optimality": (
                consumer_oracle_available
                and max_utility_gap <= self.tolerances.optimality_tol
            ),
            "quota_compliance_Z_m": bool(np.all(compliance <= market_limits)),
            "quota_adjusted_walras_identity": (
                abs(adjusted_walras) <= self.tolerances.walras_tol
            ),
            "candidate_cache_consistency": (
                max_cache_error <= self.tolerances.accounting_tol
            ),
        }
        strict_pass = all(checks.values())
        factor = self.tolerances.approximate_factor
        approximate_pass = bool(
            candidate.solver_success
            and authoritative_finite
            and normalization_error <= factor * self.tolerances.normalization_tol
            and price_sign_violation <= factor * self.tolerances.price_sign_tol
            and max_ownership <= factor * self.tolerances.ownership_tol
            and government_plan_error
            <= factor * self.tolerances.production_feasibility_tol
            and firm_oracle_available
            and max_firm_feasibility
            <= factor * self.tolerances.production_feasibility_tol
            and max_profit_gap <= factor * self.tolerances.profit_tol
            and consumer_oracle_available
            and max_consumer_feasibility <= factor * self.tolerances.feasibility_tol
            and max_budget_violation <= factor * self.tolerances.budget_tol
            and max_budget_gap <= factor * self.tolerances.budget_tol
            and max_utility_gap <= factor * self.tolerances.optimality_tol
            and max_compliance_ratio <= factor
            and abs(adjusted_walras) <= factor * self.tolerances.walras_tol
            and max_cache_error <= factor * self.tolerances.accounting_tol
        )
        if not candidate.solver_success:
            classification = CandidateClassification.FAILED_RUN
        elif strict_pass:
            classification = CandidateClassification.VERIFIED_CANDIDATE
        elif approximate_pass:
            classification = CandidateClassification.APPROXIMATE_CANDIDATE
        else:
            classification = CandidateClassification.SOLVER_POINT

        errors = {
            "normalization_error": normalization_error,
            "max_price_sign_violation": price_sign_violation,
            "max_ownership_adding_up_error": max_ownership,
            "government_plan_error": government_plan_error,
            "max_firm_feasibility_violation": max_firm_feasibility,
            "max_profit_gap": max_profit_gap,
            "max_consumer_feasibility_violation": max_consumer_feasibility,
            "max_budget_violation": max_budget_violation,
            "max_budget_exhaustion_gap": max_budget_gap,
            "max_utility_gap": max_utility_gap,
            "max_quota_compliance_violation": float(np.max(compliance)),
            "max_quota_compliance_ratio": max_compliance_ratio,
            "abs_quota_adjusted_walras_residual": abs(adjusted_walras),
            "max_candidate_cache_error": max_cache_error,
        }
        return QuotaDiagnosticsReport(
            classification=classification,
            passed=strict_pass,
            checks=checks,
            errors=errors,
            signed_l1_prices=signed_l1_prices,
            quota_prices=quota_prices.tolist(),
            total_m=self.economy.policy.total_m.tolist(),
            candidate_aggregate_allocation=aggregate_allocation.tolist(),
            candidate_aggregate_production=aggregate_production.tolist(),
            candidate_resource_residual=resource_residual.tolist(),
            compliance_violations=compliance.tolist(),
            raw_walras_value=raw_walras,
            quota_value=quota_value,
            quota_adjusted_walras_residual=adjusted_walras,
            firm_profit_breakdowns=profit_parts,
            consumer_income_breakdowns=incomes,
            budget_residuals=budget_residuals,
            consumer_optimality_results=consumer_results,
            firm_optimality_results=firm_results,
            ownership_adding_up_errors=ownership_errors,
            cache_errors=cache_errors,
            notes=tuple(notes),
        )

    def _cache_errors(
        self,
        candidate: QuotaEquilibriumCandidate,
        aggregate_allocation: np.ndarray,
        aggregate_endowment: np.ndarray,
        aggregate_production: np.ndarray,
        resource_residual: np.ndarray,
        quota_prices: np.ndarray,
        profit_parts: dict[str, QuotaFirmProfitBreakdown],
        incomes: dict[str, IncomeBreakdown],
    ) -> dict[str, float]:
        """Compare every non-authoritative solver cache to recomputed values."""

        errors = {
            "aggregate_demand": self._array_error(
                candidate.aggregate_demand, aggregate_allocation
            ),
            "aggregate_endowment": self._array_error(
                candidate.aggregate_endowment, aggregate_endowment
            ),
            "aggregate_production": self._array_error(
                candidate.aggregate_production, aggregate_production
            ),
            "resource_residual": self._array_error(
                candidate.resource_residual, resource_residual
            ),
            "quota_prices": self._array_error(candidate.quota_prices, quota_prices),
            "operating_profits": self._mapping_error(
                candidate.operating_profits,
                {key: value.operating_profit for key, value in profit_parts.items()},
            ),
            "quota_profit_terms": self._mapping_error(
                candidate.quota_profit_terms,
                {key: value.quota_profit for key, value in profit_parts.items()},
            ),
            "total_firm_profits": self._mapping_error(
                candidate.total_firm_profits,
                {key: value.total_profit for key, value in profit_parts.items()},
            ),
        }
        income_error = 0.0
        expected_ids = set(incomes)
        if set(candidate.income_breakdowns) != expected_ids:
            income_error = float("inf")
        else:
            for consumer_id, expected in incomes.items():
                cached = candidate.income_breakdowns[consumer_id]
                for key, value in expected.to_dict().items():
                    cached_value = cached.get(key)
                    if cached_value is None or not np.isfinite(cached_value):
                        income_error = float("inf")
                        break
                    income_error = max(income_error, abs(float(cached_value) - value))
        errors["income_breakdowns"] = income_error
        return errors

    @staticmethod
    def _array_error(actual: Any, expected: np.ndarray) -> float:
        array = np.asarray(actual, dtype=float)
        if array.shape != expected.shape or not np.all(np.isfinite(array)):
            return float("inf")
        return float(np.max(np.abs(array - expected), initial=0.0))

    @staticmethod
    def _mapping_error(actual: Any, expected: dict[str, float]) -> float:
        if not isinstance(actual, dict) or set(actual) != set(expected):
            return float("inf")
        values = []
        for key, expected_value in expected.items():
            actual_value = actual[key]
            if not np.isfinite(actual_value):
                return float("inf")
            values.append(abs(float(actual_value) - expected_value))
        return max(values, default=0.0)

    def _invalid_report(
        self, candidate: QuotaEquilibriumCandidate, notes: list[str]
    ) -> QuotaDiagnosticsReport:
        """Return a structured failure without evaluating malformed coordinates."""

        checks = {
            "solver_success": bool(candidate.solver_success),
            "finite_authoritative_coordinates": False,
        }
        return QuotaDiagnosticsReport(
            classification=(
                CandidateClassification.FAILED_RUN
                if not candidate.solver_success
                else CandidateClassification.SOLVER_POINT
            ),
            passed=False,
            checks=checks,
            errors={"invalid_authoritative_coordinates": float("inf")},
            signed_l1_prices=[],
            quota_prices=[],
            total_m=self.economy.policy.total_m.tolist(),
            candidate_aggregate_allocation=[],
            candidate_aggregate_production=[],
            candidate_resource_residual=[],
            compliance_violations=[],
            raw_walras_value=float("nan"),
            quota_value=float("nan"),
            quota_adjusted_walras_residual=float("nan"),
            firm_profit_breakdowns={},
            consumer_income_breakdowns={},
            budget_residuals={},
            consumer_optimality_results={},
            firm_optimality_results={},
            ownership_adding_up_errors={},
            cache_errors={},
            notes=tuple(notes),
        )
