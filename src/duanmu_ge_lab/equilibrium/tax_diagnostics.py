"""Independent verification of emission-tax equilibrium candidates."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from duanmu_ge_lab.core.consumer import ConsumerOptimalityResult
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import FirmOptimalityResult
from duanmu_ge_lab.equilibrium.candidate import (
    CandidateClassification,
    EmissionTaxEquilibriumCandidate,
)
from duanmu_ge_lab.equilibrium.diagnostics import NumericalTolerances
from duanmu_ge_lab.equilibrium.normalization import normalize_signed_l1
from duanmu_ge_lab.equilibrium.prices import PriceSignRestrictions
from duanmu_ge_lab.policy.tax import EmissionTaxEconomy


@dataclass(frozen=True, slots=True)
class EmissionTaxDiagnosticsReport:
    """Full Definition 4.3 and tax-accounting audit."""

    classification: CandidateClassification
    passed: bool
    checks: dict[str, bool]
    errors: dict[str, float]
    signed_l1_prices: list[float]
    tax_rates: list[float]
    total_net_emissions: list[float]
    tax_revenue: float
    candidate_resource_residual: list[float]
    compliance_violations: list[float]
    raw_walras_value: float
    rebate_adjusted_walras_residual: float
    firm_profits: dict[str, float]
    consumer_income_breakdowns: dict[str, IncomeBreakdown]
    budget_residuals: dict[str, float]
    consumer_optimality_results: dict[str, ConsumerOptimalityResult]
    firm_optimality_results: dict[str, FirmOptimalityResult]
    ownership_adding_up_errors: dict[str, float]
    cache_errors: dict[str, float]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification.value,
            "passed": self.passed,
            "checks": dict(self.checks),
            "errors": dict(self.errors),
            "signed_l1_prices": list(self.signed_l1_prices),
            "tax_rates": list(self.tax_rates),
            "total_net_emissions_C": list(self.total_net_emissions),
            "tax_revenue_t_dot_C": self.tax_revenue,
            "candidate_resource_residual": list(self.candidate_resource_residual),
            "compliance_violations": list(self.compliance_violations),
            "raw_walras_value_p_dot_r": self.raw_walras_value,
            "rebate_adjusted_walras_residual_p_dot_r_minus_t_dot_C": (
                self.rebate_adjusted_walras_residual
            ),
            "firm_profits": dict(self.firm_profits),
            "consumer_income_breakdowns": {
                consumer_id: value.to_dict()
                for consumer_id, value in self.consumer_income_breakdowns.items()
            },
            "budget_residuals": dict(self.budget_residuals),
            "consumer_optimality_results": {
                consumer_id: value.to_dict()
                for consumer_id, value in self.consumer_optimality_results.items()
            },
            "firm_optimality_results": {
                firm_id: value.to_dict()
                for firm_id, value in self.firm_optimality_results.items()
            },
            "ownership_adding_up_errors": dict(self.ownership_adding_up_errors),
            "cache_errors": dict(self.cache_errors),
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class EmissionTaxEquilibriumDiagnostics:
    """Verify tax prices, candidate budgets, production, compliance, and rebates."""

    economy: EmissionTaxEconomy
    tolerances: NumericalTolerances = NumericalTolerances()
    price_sign_restrictions: PriceSignRestrictions | None = None

    def evaluate(
        self, candidate: EmissionTaxEquilibriumCandidate
    ) -> EmissionTaxDiagnosticsReport:
        notes: list[str] = []
        prices = np.asarray(candidate.prices, dtype=float)
        allocations = np.asarray(candidate.allocations, dtype=float)
        plans = np.asarray(candidate.firm_plans, dtype=float)
        valid = bool(
            prices.shape == (self.economy.n_goods,)
            and allocations.shape
            == (self.economy.n_consumers, self.economy.n_goods)
            and plans.shape == (self.economy.n_firms, self.economy.n_goods)
            and np.all(np.isfinite(prices))
            and np.all(np.isfinite(allocations))
            and np.all(np.isfinite(plans))
        )
        if not valid:
            notes.append("Authoritative tax-candidate coordinates are malformed.")
            return self._invalid_report(candidate, notes)

        normalization_error = abs(float(np.sum(np.abs(prices))) - 1.0)
        signed_prices = normalize_signed_l1(prices).tolist()
        price_constraint = self.economy.policy.price_constraint_violations(prices)
        max_price_constraint = float(np.max(price_constraint, initial=0.0))
        price_sign_error = 0.0
        if self.price_sign_restrictions is not None:
            if self.price_sign_restrictions.n_goods != self.economy.n_goods:
                price_sign_error = float("inf")
                notes.append("Price-sign restriction dimension does not match economy.")
            else:
                price_sign_error = self.price_sign_restrictions.max_violation(
                    prices, self.tolerances.price_sign_tol
                )

        aggregate_allocation = self.economy.aggregate_allocations(allocations)
        aggregate_endowment = self.economy.aggregate_endowment()
        aggregate_production = np.sum(plans, axis=0)
        residual = self.economy.candidate_resource_residual(allocations, plans)
        emissions = self.economy.policy.total_net_emissions(residual)
        revenue = self.economy.policy.tax_revenue(residual)
        compliance = self.economy.policy.compliance_violations(residual)
        market_limits = self.tolerances.market_abs_tol + self.tolerances.market_rel_tol * np.maximum(
            np.abs(aggregate_allocation),
            np.maximum(np.abs(aggregate_endowment), np.abs(aggregate_production)),
        )
        max_compliance_ratio = float(np.max(compliance / market_limits))
        profits_array = self.economy.firm_profits(prices, plans)
        profits = {
            firm.id: float(profits_array[index])
            for index, firm in enumerate(self.economy.firms)
        }
        incomes = self.economy.income_breakdowns(prices, allocations, plans)
        raw_walras = float(np.dot(prices, residual))
        adjusted_walras = raw_walras - revenue

        ownership_errors = {
            firm.id: self.economy.ownership_adding_up_error(firm)
            for firm in self.economy.firms
        }
        weighted_rebate_total = sum(
            consumer.population_weight
            * self.economy.policy.rebate_shares[consumer.id]
            for consumer in self.economy.consumers
        )
        rebate_error = abs(float(weighted_rebate_total) - 1.0)

        firm_results: dict[str, FirmOptimalityResult] = {}
        firm_oracle = True
        for index, firm in enumerate(self.economy.firms):
            try:
                firm_results[firm.id] = firm.evaluate_optimality(prices, plans[index])
            except (ValueError, ArithmeticError) as exc:
                firm_oracle = False
                notes.append(f"Firm {firm.id} optimality oracle failed: {exc}")

        consumer_results: dict[str, ConsumerOptimalityResult] = {}
        budget_residuals: dict[str, float] = {}
        consumer_oracle = True
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
                consumer_oracle = False
                notes.append(f"Consumer {consumer.id} demand oracle failed: {exc}")

        cache_errors = self._cache_errors(
            candidate,
            aggregate_allocation,
            aggregate_endowment,
            aggregate_production,
            residual,
            emissions,
            revenue,
            profits,
            incomes,
        )
        max_ownership = max(ownership_errors.values(), default=0.0)
        max_firm_feasibility = max(
            (result.feasibility_violation for result in firm_results.values()),
            default=0.0,
        )
        max_profit_gap = max(
            (max(0.0, result.profit_gap) for result in firm_results.values()),
            default=0.0,
        )
        max_consumer_feasibility = max(
            (result.feasibility_violation for result in consumer_results.values()),
            default=float("inf"),
        )
        max_budget_violation = max(
            (max(0.0, -value) for value in budget_residuals.values()),
            default=float("inf"),
        )
        max_budget_gap = max(
            (abs(value) for value in budget_residuals.values()),
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
        max_cache = max(cache_errors.values(), default=float("inf"))

        checks = {
            "solver_success": bool(candidate.solver_success),
            "finite_authoritative_coordinates": valid,
            "signed_l1_normalization": normalization_error
            <= self.tolerances.normalization_tol,
            "tax_price_constraint_proj_k_p_equals_negative_t": max_price_constraint
            <= self.tolerances.accounting_tol,
            "price_sign_restrictions": price_sign_error == 0.0,
            "rebate_shares_add_up": rebate_error <= self.tolerances.ownership_tol,
            "ownership_share_adding_up": max_ownership
            <= self.tolerances.ownership_tol,
            "firm_optimality_oracle_available": firm_oracle,
            "firm_feasibility": max_firm_feasibility
            <= self.tolerances.production_feasibility_tol,
            "firm_profit_maximization": firm_oracle
            and max_profit_gap <= self.tolerances.profit_tol,
            "consumer_optimality_oracle_available": consumer_oracle,
            "consumer_feasibility": consumer_oracle
            and max_consumer_feasibility <= self.tolerances.feasibility_tol,
            "budget_feasibility": consumer_oracle
            and max_budget_violation <= self.tolerances.budget_tol,
            "budget_exhaustion": consumer_oracle
            and max_budget_gap <= self.tolerances.budget_tol,
            "consumer_optimality": consumer_oracle
            and max_utility_gap <= self.tolerances.optimality_tol,
            "tax_revenue_nonnegative": revenue >= -self.tolerances.accounting_tol,
            "compliance_V": bool(np.all(compliance <= market_limits)),
            "rebate_adjusted_walras_identity": abs(adjusted_walras)
            <= self.tolerances.walras_tol,
            "candidate_cache_consistency": max_cache
            <= self.tolerances.accounting_tol,
        }
        strict_pass = all(checks.values())
        factor = self.tolerances.approximate_factor
        approximate = bool(
            candidate.solver_success
            and valid
            and normalization_error <= factor * self.tolerances.normalization_tol
            and max_price_constraint <= factor * self.tolerances.accounting_tol
            and price_sign_error <= factor * self.tolerances.price_sign_tol
            and rebate_error <= factor * self.tolerances.ownership_tol
            and max_ownership <= factor * self.tolerances.ownership_tol
            and firm_oracle
            and max_firm_feasibility
            <= factor * self.tolerances.production_feasibility_tol
            and max_profit_gap <= factor * self.tolerances.profit_tol
            and consumer_oracle
            and max_consumer_feasibility <= factor * self.tolerances.feasibility_tol
            and max_budget_violation <= factor * self.tolerances.budget_tol
            and max_budget_gap <= factor * self.tolerances.budget_tol
            and max_utility_gap <= factor * self.tolerances.optimality_tol
            and max_compliance_ratio <= factor
            and abs(adjusted_walras) <= factor * self.tolerances.walras_tol
            and max_cache <= factor * self.tolerances.accounting_tol
        )
        if not candidate.solver_success:
            classification = CandidateClassification.FAILED_RUN
        elif strict_pass:
            classification = CandidateClassification.VERIFIED_CANDIDATE
        elif approximate:
            classification = CandidateClassification.APPROXIMATE_CANDIDATE
        else:
            classification = CandidateClassification.SOLVER_POINT

        errors = {
            "normalization_error": normalization_error,
            "max_tax_price_constraint_violation": max_price_constraint,
            "max_price_sign_violation": price_sign_error,
            "rebate_adding_up_error": rebate_error,
            "max_ownership_adding_up_error": max_ownership,
            "max_firm_feasibility_violation": max_firm_feasibility,
            "max_profit_gap": max_profit_gap,
            "max_consumer_feasibility_violation": max_consumer_feasibility,
            "max_budget_violation": max_budget_violation,
            "max_budget_exhaustion_gap": max_budget_gap,
            "max_utility_gap": max_utility_gap,
            "max_compliance_violation": float(np.max(compliance, initial=0.0)),
            "max_compliance_ratio": max_compliance_ratio,
            "abs_rebate_adjusted_walras_residual": abs(adjusted_walras),
            "max_candidate_cache_error": max_cache,
        }
        return EmissionTaxDiagnosticsReport(
            classification=classification,
            passed=strict_pass,
            checks=checks,
            errors=errors,
            signed_l1_prices=signed_prices,
            tax_rates=np.asarray(self.economy.policy.tax_rates).tolist(),
            total_net_emissions=emissions.tolist(),
            tax_revenue=revenue,
            candidate_resource_residual=residual.tolist(),
            compliance_violations=compliance.tolist(),
            raw_walras_value=raw_walras,
            rebate_adjusted_walras_residual=adjusted_walras,
            firm_profits=profits,
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
        candidate,
        aggregate_allocation,
        aggregate_endowment,
        aggregate_production,
        residual,
        emissions,
        revenue,
        profits,
        incomes,
    ) -> dict[str, float]:
        errors = {
            "tax_rates": self._array_error(candidate.tax_rates, self.economy.policy.tax_rates),
            "total_net_emissions": self._array_error(
                candidate.total_net_emissions, emissions
            ),
            "tax_revenue": abs(float(candidate.tax_revenue) - revenue)
            if np.isfinite(candidate.tax_revenue)
            else float("inf"),
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
                candidate.resource_residual, residual
            ),
            "firm_profits": self._mapping_error(candidate.firm_profits, profits),
        }
        income_error = 0.0
        if set(candidate.income_breakdowns) != set(incomes):
            income_error = float("inf")
        else:
            for consumer_id, expected in incomes.items():
                cached = candidate.income_breakdowns[consumer_id]
                for key, value in expected.to_dict().items():
                    actual = cached.get(key)
                    if actual is None or not np.isfinite(actual):
                        income_error = float("inf")
                        break
                    income_error = max(income_error, abs(float(actual) - value))
        errors["income_breakdowns"] = income_error
        return errors

    @staticmethod
    def _array_error(actual, expected) -> float:
        array = np.asarray(actual, dtype=float)
        expected_array = np.asarray(expected, dtype=float)
        if array.shape != expected_array.shape or not np.all(np.isfinite(array)):
            return float("inf")
        return float(np.max(np.abs(array - expected_array), initial=0.0))

    @staticmethod
    def _mapping_error(actual, expected) -> float:
        if not isinstance(actual, dict) or set(actual) != set(expected):
            return float("inf")
        errors = []
        for key, value in expected.items():
            if not np.isfinite(actual[key]):
                return float("inf")
            errors.append(abs(float(actual[key]) - value))
        return max(errors, default=0.0)

    def _invalid_report(self, candidate, notes) -> EmissionTaxDiagnosticsReport:
        return EmissionTaxDiagnosticsReport(
            classification=(
                CandidateClassification.FAILED_RUN
                if not candidate.solver_success
                else CandidateClassification.SOLVER_POINT
            ),
            passed=False,
            checks={"solver_success": bool(candidate.solver_success), "finite_authoritative_coordinates": False},
            errors={"invalid_authoritative_coordinates": float("inf")},
            signed_l1_prices=[],
            tax_rates=np.asarray(self.economy.policy.tax_rates).tolist(),
            total_net_emissions=[],
            tax_revenue=float("nan"),
            candidate_resource_residual=[],
            compliance_violations=[],
            raw_walras_value=float("nan"),
            rebate_adjusted_walras_residual=float("nan"),
            firm_profits={},
            consumer_income_breakdowns={},
            budget_residuals={},
            consumer_optimality_results={},
            firm_optimality_results={},
            ownership_adding_up_errors={},
            cache_errors={},
            notes=tuple(notes),
        )
