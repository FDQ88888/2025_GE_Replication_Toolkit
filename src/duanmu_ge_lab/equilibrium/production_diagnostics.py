"""Independent verification for finite production-equilibrium candidates."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.consumer import ConsumerOptimalityResult
from duanmu_ge_lab.core.income import IncomeBreakdown
from duanmu_ge_lab.core.production import FirmOptimalityResult
from duanmu_ge_lab.core.production_economy import ProductionEconomy
from duanmu_ge_lab.equilibrium.candidate import (
    CandidateClassification,
    ProductionEquilibriumCandidate,
)
from duanmu_ge_lab.equilibrium.diagnostics import NumericalTolerances
from duanmu_ge_lab.equilibrium.normalization import (
    FixedNumeraire,
    normalize_signed_l1,
)
from duanmu_ge_lab.equilibrium.prices import PriceSignRestrictions


@dataclass(frozen=True, slots=True)
class ProductionDiagnosticsReport:
    """Complete production-candidate audit with candidate and oracle data separated."""

    classification: CandidateClassification
    passed: bool
    checks: dict[str, bool]
    errors: dict[str, float]
    signed_l1_prices: list[float]
    candidate_aggregate_allocation: list[float]
    candidate_aggregate_production: list[float]
    candidate_resource_residual: list[float]
    market_limits: list[float]
    candidate_walras_residual: float
    candidate_income_breakdowns: dict[str, IncomeBreakdown]
    independently_reoptimized_consumer_allocations: list[list[float]]
    independently_optimal_firm_plans: list[list[float]]
    fully_reoptimized_resource_residual: list[float]
    budget_residuals: dict[str, float]
    consumer_feasibility_violations: dict[str, float]
    consumer_optimality_results: dict[str, ConsumerOptimalityResult]
    firm_optimality_results: dict[str, FirmOptimalityResult]
    ownership_adding_up_errors: dict[str, float]
    dividend_accounting_residuals: dict[str, float]
    cache_errors: dict[str, float]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable diagnostics with explicit economic names."""

        return {
            "classification": self.classification.value,
            "passed": self.passed,
            "checks": dict(self.checks),
            "errors": dict(self.errors),
            "signed_l1_prices": list(self.signed_l1_prices),
            "candidate_aggregate_allocation": list(
                self.candidate_aggregate_allocation
            ),
            "candidate_aggregate_production": list(
                self.candidate_aggregate_production
            ),
            "candidate_resource_residual": list(self.candidate_resource_residual),
            "market_limits": list(self.market_limits),
            "candidate_walras_residual": self.candidate_walras_residual,
            "candidate_income_breakdowns": {
                consumer_id: breakdown.to_dict()
                for consumer_id, breakdown in self.candidate_income_breakdowns.items()
            },
            "independently_reoptimized_consumer_allocations": [
                list(row)
                for row in self.independently_reoptimized_consumer_allocations
            ],
            "independently_optimal_firm_plans": [
                list(row) for row in self.independently_optimal_firm_plans
            ],
            "fully_reoptimized_resource_residual": list(
                self.fully_reoptimized_resource_residual
            ),
            "budget_residuals": dict(self.budget_residuals),
            "consumer_feasibility_violations": dict(
                self.consumer_feasibility_violations
            ),
            "consumer_optimality_results": {
                consumer_id: result.to_dict()
                for consumer_id, result in self.consumer_optimality_results.items()
            },
            "firm_optimality_results": {
                firm_id: result.to_dict()
                for firm_id, result in self.firm_optimality_results.items()
            },
            "ownership_adding_up_errors": dict(self.ownership_adding_up_errors),
            "dividend_accounting_residuals": dict(
                self.dividend_accounting_residuals
            ),
            "cache_errors": dict(self.cache_errors),
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class ProductionEquilibriumDiagnostics:
    """Verify production, ownership, income, consumers, and candidate resources."""

    economy: ProductionEconomy
    normalization: FixedNumeraire
    tolerances: NumericalTolerances = NumericalTolerances()
    price_sign_restrictions: PriceSignRestrictions | None = None

    def evaluate(
        self, candidate: ProductionEquilibriumCandidate
    ) -> ProductionDiagnosticsReport:
        """Classify a production candidate only after all independent checks."""

        notes: list[str] = []
        prices = np.asarray(candidate.prices, dtype=float)
        allocations = np.asarray(candidate.allocations, dtype=float)
        firm_plans = np.asarray(candidate.firm_plans, dtype=float)
        price_shape = (self.economy.n_goods,)
        allocation_shape = (self.economy.n_consumers, self.economy.n_goods)
        firm_shape = (self.economy.n_firms, self.economy.n_goods)
        vector_shape = (self.economy.n_goods,)

        core_valid = bool(
            prices.shape == price_shape
            and allocations.shape == allocation_shape
            and firm_plans.shape == firm_shape
            and np.all(np.isfinite(prices))
            and np.all(np.isfinite(allocations))
            and np.all(np.isfinite(firm_plans))
        )
        cache_arrays = (
            np.asarray(candidate.aggregate_demand),
            np.asarray(candidate.aggregate_endowment),
            np.asarray(candidate.aggregate_production),
            np.asarray(candidate.resource_residual),
        )
        cache_shapes_valid = all(array.shape == vector_shape for array in cache_arrays)
        profit_cache = np.asarray(candidate.firm_profits)
        expected_consumer_ids = {
            consumer.id for consumer in self.economy.consumers
        }
        expected_income_keys = {
            "endowment_income",
            "firm_dividend_income",
            "policy_income",
            "total_income",
        }
        income_cache_values_valid = True
        try:
            if set(candidate.income_breakdowns) != expected_consumer_ids:
                income_cache_values_valid = False
            else:
                for cached in candidate.income_breakdowns.values():
                    if set(cached) != expected_income_keys or not all(
                        np.isfinite(float(cached[key]))
                        for key in expected_income_keys
                    ):
                        income_cache_values_valid = False
                        break
        except (TypeError, ValueError, KeyError):
            income_cache_values_valid = False
        cache_values_valid = bool(
            cache_shapes_valid
            and profit_cache.shape == (self.economy.n_firms,)
            and all(np.all(np.isfinite(array)) for array in cache_arrays)
            and np.all(np.isfinite(profit_cache))
            and income_cache_values_valid
        )
        finite_values = core_valid and cache_values_valid

        normalization_error = float("inf")
        signed_l1_prices: list[float] = []
        if prices.shape == price_shape and np.all(np.isfinite(prices)):
            if self.normalization.index < prices.size:
                normalization_error = abs(
                    float(prices[self.normalization.index])
                    - self.normalization.value
                )
            try:
                signed_l1_prices = normalize_signed_l1(prices).tolist()
            except ValueError as exc:
                notes.append(f"Signed L1 normalization failed: {exc}")

        price_sign_violation = float("inf")
        if prices.shape == price_shape and np.all(np.isfinite(prices)):
            if self.price_sign_restrictions is None:
                price_sign_violation = 0.0
            elif self.price_sign_restrictions.n_goods != self.economy.n_goods:
                notes.append("Price-sign restriction dimension does not match economy.")
            else:
                price_sign_violation = self.price_sign_restrictions.max_violation(
                    prices, self.tolerances.price_sign_tol
                )

        aggregate_endowment = self.economy.aggregate_endowment()
        aggregate_allocation = np.full(self.economy.n_goods, np.nan)
        aggregate_production = np.full(self.economy.n_goods, np.nan)
        candidate_residual = np.full(self.economy.n_goods, np.inf)
        market_limits = np.full(self.economy.n_goods, np.nan)
        candidate_walras = float("inf")
        if core_valid:
            aggregate_allocation = self.economy.aggregate_allocations(allocations)
            aggregate_production = np.sum(firm_plans, axis=0)
            candidate_residual = self.economy.candidate_resource_residual(
                allocations, firm_plans
            )
            available_resources = aggregate_endowment + aggregate_production
            scales = np.maximum.reduce(
                [
                    np.abs(aggregate_allocation),
                    np.abs(available_resources),
                    np.ones(self.economy.n_goods),
                ]
            )
            market_limits = (
                self.tolerances.market_abs_tol
                + self.tolerances.market_rel_tol * scales
            )
            candidate_walras = float(np.dot(prices, candidate_residual))

        firm_results: dict[str, FirmOptimalityResult] = {}
        ownership_errors = {
            firm.id: self.economy.ownership_adding_up_error(firm)
            for firm in self.economy.firms
        }
        dividend_residuals: dict[str, float] = {}
        firm_feasibility_values: list[float] = []
        profit_gap_values: list[float] = []
        independent_plans = np.empty(firm_shape, dtype=float)
        actual_profits = np.full(self.economy.n_firms, np.nan)
        firm_oracle_available = core_valid
        if core_valid:
            for index, firm in enumerate(self.economy.firms):
                try:
                    result = firm.evaluate_optimality(prices, firm_plans[index])
                    firm_results[firm.id] = result
                    independent_plans[index] = np.asarray(result.optimal_plan)
                    actual_profits[index] = result.candidate_profit
                    firm_feasibility_values.append(result.feasibility_violation)
                    profit_gap_values.append(abs(result.profit_gap))
                    distributed = sum(
                        consumer.population_weight
                        * firm.ownership.share_of(consumer.id)
                        * result.candidate_profit
                        for consumer in self.economy.consumers
                    )
                    dividend_residuals[firm.id] = (
                        distributed - result.candidate_profit
                    )
                except (ValueError, ArithmeticError) as exc:
                    firm_oracle_available = False
                    notes.append(f"Firm {firm.id} optimality failed: {exc}")
        else:
            firm_oracle_available = False

        max_firm_feasibility = max(
            firm_feasibility_values, default=float("inf")
        )
        max_profit_gap = max(profit_gap_values, default=float("inf"))
        max_ownership_error = max(ownership_errors.values(), default=float("inf"))
        max_dividend_error = max(
            (abs(value) for value in dividend_residuals.values()),
            default=float("inf"),
        )

        income_breakdowns: dict[str, IncomeBreakdown] = {}
        budget_residuals: dict[str, float] = {}
        consumer_feasibility: dict[str, float] = {}
        consumer_results: dict[str, ConsumerOptimalityResult] = {}
        budget_violations: list[float] = []
        budget_exhaustion: list[float] = []
        consumer_feasibility_values: list[float] = []
        utility_gap_values: list[float] = []
        reoptimized_consumers = np.empty(allocation_shape, dtype=float)
        consumer_oracle_available = core_valid
        if core_valid:
            try:
                income_breakdowns = self.economy.income_breakdowns(
                    prices, firm_plans
                )
                reoptimized_consumers = self.economy.individual_demands(
                    prices, firm_plans
                )
                for row, consumer in enumerate(self.economy.consumers):
                    income = income_breakdowns[consumer.id].total_income
                    budget_residual = consumer.budget_residual_at_income(
                        prices, allocations[row], income
                    )
                    budget_residuals[consumer.id] = budget_residual
                    budget_violations.append(max(0.0, -budget_residual))
                    budget_exhaustion.append(abs(budget_residual))
                    violation = consumer.consumption_feasibility_violation(
                        allocations[row]
                    )
                    consumer_feasibility[consumer.id] = violation
                    consumer_feasibility_values.append(violation)
                    result = consumer.evaluate_optimality_at_income(
                        prices, allocations[row], income
                    )
                    consumer_results[consumer.id] = result
                    utility_gap_values.append(
                        float("inf")
                        if result.utility_gap is None
                        else abs(result.utility_gap)
                    )
            except (ValueError, ArithmeticError) as exc:
                consumer_oracle_available = False
                notes.append(f"Consumer income/optimality recomputation failed: {exc}")
        else:
            consumer_oracle_available = False

        max_budget_violation = max(budget_violations, default=float("inf"))
        max_budget_exhaustion = max(budget_exhaustion, default=float("inf"))
        max_consumer_feasibility = max(
            consumer_feasibility_values, default=float("inf")
        )
        max_utility_gap = max(utility_gap_values, default=float("inf"))

        fully_reoptimized_residual = np.full(self.economy.n_goods, np.inf)
        try:
            fully_reoptimized_residual = self.economy.excess_demand(prices)
        except (ValueError, ArithmeticError) as exc:
            notes.append(f"Fully reoptimized economy failed: {exc}")

        market_violations = np.full(self.economy.n_goods, np.inf)
        if core_valid:
            for index, commodity in enumerate(self.economy.commodities):
                residual = float(candidate_residual[index])
                if commodity.clearing_rule is ClearingRule.EXACT:
                    market_violations[index] = abs(residual)
                else:
                    market_violations[index] = max(0.0, residual)

        cache_errors = {
            "aggregate_demand": float("inf"),
            "aggregate_endowment": float("inf"),
            "aggregate_production": float("inf"),
            "resource_residual": float("inf"),
            "firm_profits": float("inf"),
            "income_breakdowns": float("inf"),
        }
        if core_valid and cache_values_valid:
            cache_errors.update(
                {
                    "aggregate_demand": float(
                        np.max(
                            np.abs(
                                np.asarray(candidate.aggregate_demand)
                                - aggregate_allocation
                            )
                        )
                    ),
                    "aggregate_endowment": float(
                        np.max(
                            np.abs(
                                np.asarray(candidate.aggregate_endowment)
                                - aggregate_endowment
                            )
                        )
                    ),
                    "aggregate_production": float(
                        np.max(
                            np.abs(
                                np.asarray(candidate.aggregate_production)
                                - aggregate_production
                            )
                        )
                    ),
                    "resource_residual": float(
                        np.max(
                            np.abs(
                                np.asarray(candidate.resource_residual)
                                - candidate_residual
                            )
                        )
                    ),
                    "firm_profits": float(
                        np.max(np.abs(profit_cache - actual_profits))
                    ),
                }
            )
            income_error = 0.0
            if set(candidate.income_breakdowns) != expected_consumer_ids:
                income_error = float("inf")
            else:
                for consumer_id, actual in income_breakdowns.items():
                    cached = candidate.income_breakdowns[consumer_id]
                    expected = actual.to_dict()
                    if set(cached) != set(expected):
                        income_error = float("inf")
                        break
                    income_error = max(
                        income_error,
                        max(
                            abs(float(cached[key]) - value)
                            for key, value in expected.items()
                        ),
                    )
            cache_errors["income_breakdowns"] = income_error

        max_cache_error = max(cache_errors.values())
        factor = self.tolerances.approximate_factor
        strict_market = bool(
            core_valid and np.all(market_violations <= market_limits)
        )
        approximate_market = bool(
            core_valid and np.all(market_violations <= factor * market_limits)
        )
        checks = {
            "solver_success": bool(candidate.solver_success),
            "finite_values": finite_values,
            "price_normalization": (
                normalization_error <= self.tolerances.normalization_tol
            ),
            "price_sign_restrictions": price_sign_violation == 0.0,
            "ownership_share_adding_up": (
                max_ownership_error <= self.tolerances.ownership_tol
            ),
            "firm_feasibility": (
                max_firm_feasibility
                <= self.tolerances.production_feasibility_tol
            ),
            "firm_optimality_oracle_available": firm_oracle_available,
            "firm_optimality": (
                firm_oracle_available
                and max_profit_gap <= self.tolerances.profit_tol
            ),
            "dividend_accounting": (
                max_dividend_error <= self.tolerances.accounting_tol
            ),
            "consumer_feasibility": (
                max_consumer_feasibility <= self.tolerances.feasibility_tol
            ),
            "budget_feasibility": (
                max_budget_violation <= self.tolerances.budget_tol
            ),
            "budget_exhaustion": (
                max_budget_exhaustion <= self.tolerances.budget_tol
            ),
            "consumer_optimality_oracle_available": consumer_oracle_available,
            "consumer_optimality": (
                consumer_oracle_available
                and max_utility_gap <= self.tolerances.optimality_tol
            ),
            "candidate_cache_consistency": (
                max_cache_error <= self.tolerances.accounting_tol
            ),
            "market_clearing": strict_market,
            "walras_law": (
                abs(candidate_walras) <= self.tolerances.walras_tol
            ),
        }
        hard_names = tuple(name for name in checks if name != "budget_exhaustion")
        strict_pass = all(checks[name] for name in hard_names)
        approximate_pass = bool(
            candidate.solver_success
            and finite_values
            and firm_oracle_available
            and consumer_oracle_available
            and normalization_error <= factor * self.tolerances.normalization_tol
            and price_sign_violation <= factor * self.tolerances.price_sign_tol
            and max_ownership_error <= factor * self.tolerances.ownership_tol
            and max_firm_feasibility
            <= factor * self.tolerances.production_feasibility_tol
            and max_profit_gap <= factor * self.tolerances.profit_tol
            and max_dividend_error <= factor * self.tolerances.accounting_tol
            and max_consumer_feasibility
            <= factor * self.tolerances.feasibility_tol
            and max_budget_violation <= factor * self.tolerances.budget_tol
            and max_utility_gap <= factor * self.tolerances.optimality_tol
            and max_cache_error <= factor * self.tolerances.accounting_tol
            and approximate_market
            and abs(candidate_walras) <= factor * self.tolerances.walras_tol
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
            "max_ownership_adding_up_error": max_ownership_error,
            "max_firm_feasibility_violation": max_firm_feasibility,
            "max_abs_profit_gap": max_profit_gap,
            "max_dividend_accounting_error": max_dividend_error,
            "max_consumer_feasibility_violation": max_consumer_feasibility,
            "max_budget_violation": max_budget_violation,
            "max_budget_exhaustion_gap": max_budget_exhaustion,
            "max_abs_utility_gap": max_utility_gap,
            "max_candidate_cache_error": max_cache_error,
            "max_market_violation": float(np.max(market_violations)),
            "abs_candidate_walras_residual": abs(candidate_walras),
        }
        return ProductionDiagnosticsReport(
            classification=classification,
            passed=strict_pass,
            checks=checks,
            errors=errors,
            signed_l1_prices=signed_l1_prices,
            candidate_aggregate_allocation=aggregate_allocation.tolist(),
            candidate_aggregate_production=aggregate_production.tolist(),
            candidate_resource_residual=candidate_residual.tolist(),
            market_limits=market_limits.tolist(),
            candidate_walras_residual=candidate_walras,
            candidate_income_breakdowns=income_breakdowns,
            independently_reoptimized_consumer_allocations=(
                reoptimized_consumers.tolist()
                if consumer_oracle_available
                else []
            ),
            independently_optimal_firm_plans=(
                independent_plans.tolist() if firm_oracle_available else []
            ),
            fully_reoptimized_resource_residual=(
                fully_reoptimized_residual.tolist()
            ),
            budget_residuals=budget_residuals,
            consumer_feasibility_violations=consumer_feasibility,
            consumer_optimality_results=consumer_results,
            firm_optimality_results=firm_results,
            ownership_adding_up_errors=ownership_errors,
            dividend_accounting_residuals=dividend_residuals,
            cache_errors=cache_errors,
            notes=tuple(notes),
        )
