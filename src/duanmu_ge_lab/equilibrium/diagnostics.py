"""Independent verification of finite exchange-equilibrium candidates."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.consumer import ConsumerOptimalityResult
from duanmu_ge_lab.core.economy import ExchangeEconomy
from duanmu_ge_lab.core.numerics import (
    PROFIT_MARGIN_ABS_TOL,
    PROFIT_MARGIN_REL_TOL,
)
from duanmu_ge_lab.equilibrium.candidate import (
    CandidateClassification,
    EquilibriumCandidate,
)
from duanmu_ge_lab.equilibrium.normalization import (
    FixedNumeraire,
    normalize_signed_l1,
)
from duanmu_ge_lab.equilibrium.prices import PriceSignRestrictions


@dataclass(frozen=True, slots=True)
class NumericalTolerances:
    """Centralized strict and approximate numerical tolerances.

    ``optimality_tol`` applies to utility gaps, not bundle distances. A separate
    unique-demand bundle gap is reported only as a benchmark debugging statistic.
    """

    market_abs_tol: float = 1e-10
    market_rel_tol: float = 1e-10
    budget_tol: float = 1e-10
    feasibility_tol: float = 1e-12
    optimality_tol: float = 1e-10
    normalization_tol: float = 1e-12
    walras_tol: float = 1e-10
    production_feasibility_tol: float = 1e-10
    profit_tol: float = 1e-10
    profit_margin_abs_tol: float = PROFIT_MARGIN_ABS_TOL
    profit_margin_rel_tol: float = PROFIT_MARGIN_REL_TOL
    ownership_tol: float = 1e-12
    accounting_tol: float = 1e-10
    price_sign_tol: float = 1e-12
    approximate_factor: float = 100.0

    def __post_init__(self) -> None:
        values = (
            self.market_abs_tol,
            self.market_rel_tol,
            self.budget_tol,
            self.feasibility_tol,
            self.optimality_tol,
            self.normalization_tol,
            self.walras_tol,
            self.production_feasibility_tol,
            self.profit_tol,
            self.profit_margin_abs_tol,
            self.profit_margin_rel_tol,
            self.ownership_tol,
            self.accounting_tol,
            self.price_sign_tol,
        )
        if not all(np.isfinite(value) and value > 0.0 for value in values):
            raise ValueError("All numerical tolerances must be finite and positive.")
        if not np.isfinite(self.approximate_factor) or self.approximate_factor <= 1.0:
            raise ValueError("approximate_factor must be finite and greater than one.")

    def to_dict(self) -> dict[str, float]:
        """Return JSON-serializable tolerance values."""

        return {
            "market_abs_tol": self.market_abs_tol,
            "market_rel_tol": self.market_rel_tol,
            "budget_tol": self.budget_tol,
            "feasibility_tol": self.feasibility_tol,
            "optimality_tol": self.optimality_tol,
            "normalization_tol": self.normalization_tol,
            "walras_tol": self.walras_tol,
            "production_feasibility_tol": self.production_feasibility_tol,
            "profit_tol": self.profit_tol,
            "profit_margin_abs_tol": self.profit_margin_abs_tol,
            "profit_margin_rel_tol": self.profit_margin_rel_tol,
            "ownership_tol": self.ownership_tol,
            "accounting_tol": self.accounting_tol,
            "price_sign_tol": self.price_sign_tol,
            "approximate_factor": self.approximate_factor,
        }


@dataclass(frozen=True, slots=True)
class EquilibriumDiagnosticsReport:
    """Detailed verification result with candidate and counterfactual data separated."""

    classification: CandidateClassification
    passed: bool
    checks: dict[str, bool]
    errors: dict[str, float]
    signed_l1_prices: list[float]
    candidate_aggregate_allocation: list[float]
    candidate_resource_residual: list[float]
    market_limits: list[float]
    candidate_walras_residual: float
    reoptimized_allocations: list[list[float]]
    reoptimized_resource_residual: list[float]
    reoptimized_walras_residual: float
    budget_residuals: dict[str, float]
    budget_exhaustion_gaps: dict[str, float]
    consumer_feasibility_violations: dict[str, float]
    utility_gaps: dict[str, float | None]
    unique_demand_bundle_gaps: dict[str, float | None]
    consumer_optimality_results: dict[str, ConsumerOptimalityResult]
    notes: tuple[str, ...]

    @property
    def market_residuals(self) -> list[float]:
        """Compatibility alias for the candidate resource residual."""

        return self.candidate_resource_residual

    @property
    def walras_residual(self) -> float:
        """Compatibility alias for the formal candidate Walras residual."""

        return self.candidate_walras_residual

    @property
    def recomputed_allocations(self) -> list[list[float]]:
        """Compatibility alias for independently reoptimized allocations."""

        return self.reoptimized_allocations

    @property
    def optimality_gaps(self) -> dict[str, float | None]:
        """Compatibility alias for utility gaps."""

        return self.utility_gaps

    def to_dict(self) -> dict[str, Any]:
        """Return the complete report using only semantically explicit field names."""

        return {
            "classification": self.classification.value,
            "passed": self.passed,
            "checks": dict(self.checks),
            "errors": dict(self.errors),
            "signed_l1_prices": list(self.signed_l1_prices),
            "candidate_aggregate_allocation": list(
                self.candidate_aggregate_allocation
            ),
            "candidate_resource_residual": list(self.candidate_resource_residual),
            "market_limits": list(self.market_limits),
            "candidate_walras_residual": self.candidate_walras_residual,
            "reoptimized_allocations": [
                list(row) for row in self.reoptimized_allocations
            ],
            "reoptimized_resource_residual": list(
                self.reoptimized_resource_residual
            ),
            "reoptimized_walras_residual": self.reoptimized_walras_residual,
            "budget_residuals": dict(self.budget_residuals),
            "budget_exhaustion_gaps": dict(self.budget_exhaustion_gaps),
            "consumer_feasibility_violations": dict(
                self.consumer_feasibility_violations
            ),
            "utility_gaps": dict(self.utility_gaps),
            "unique_demand_bundle_gaps": dict(self.unique_demand_bundle_gaps),
            "consumer_optimality_results": {
                consumer_id: result.to_dict()
                for consumer_id, result in self.consumer_optimality_results.items()
            },
            "notes": list(self.notes),
        }


@dataclass(frozen=True, slots=True)
class EquilibriumDiagnostics:
    """Verify a candidate independently of solver claims and cached aggregates.

    Candidate market feasibility is defined from the candidate allocation:
    ``r(x) = sum_i x_i - sum_i omega_i``. The formal Walras diagnostic is
    ``p dot r(x)``. Independently reoptimized demand is used for consumer
    optimality and is reported separately; it never replaces the candidate in the
    market-clearing test.
    """

    economy: ExchangeEconomy
    normalization: FixedNumeraire
    tolerances: NumericalTolerances = NumericalTolerances()
    price_sign_restrictions: PriceSignRestrictions | None = None

    def evaluate(
        self, candidate: EquilibriumCandidate
    ) -> EquilibriumDiagnosticsReport:
        """Evaluate all hard diagnostics and classify an unverified candidate."""

        notes: list[str] = []
        prices = np.asarray(candidate.prices, dtype=float)
        allocations = np.asarray(candidate.allocations, dtype=float)
        expected_price_shape = (self.economy.n_goods,)
        expected_allocation_shape = (
            self.economy.n_consumers,
            self.economy.n_goods,
        )

        aggregate_demand_cache = np.asarray(candidate.aggregate_demand)
        aggregate_endowment_cache = np.asarray(candidate.aggregate_endowment)
        excess_demand_cache = np.asarray(candidate.excess_demand)
        candidate_core_valid = bool(
            prices.shape == expected_price_shape
            and allocations.shape == expected_allocation_shape
            and np.all(np.isfinite(prices))
            and np.all(np.isfinite(allocations))
        )
        cache_values_valid = bool(
            aggregate_demand_cache.shape == expected_price_shape
            and aggregate_endowment_cache.shape == expected_price_shape
            and excess_demand_cache.shape == expected_price_shape
            and np.all(np.isfinite(aggregate_demand_cache))
            and np.all(np.isfinite(aggregate_endowment_cache))
            and np.all(np.isfinite(excess_demand_cache))
        )
        finite_values = candidate_core_valid and cache_values_valid

        normalization_error = float("inf")
        signed_l1_prices: list[float] = []
        if prices.shape == expected_price_shape and np.all(np.isfinite(prices)):
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
        if prices.shape == expected_price_shape and np.all(np.isfinite(prices)):
            if self.price_sign_restrictions is None:
                price_sign_violation = 0.0
            elif self.price_sign_restrictions.n_goods != self.economy.n_goods:
                notes.append("Price-sign restriction dimension does not match economy.")
            else:
                price_sign_violation = self.price_sign_restrictions.max_violation(
                    prices, self.tolerances.price_sign_tol
                )

        aggregate_endowment = self.economy.aggregate_endowment()
        candidate_aggregate = np.full(self.economy.n_goods, np.nan, dtype=float)
        candidate_residual = np.full(self.economy.n_goods, np.inf, dtype=float)
        market_limits = np.full(self.economy.n_goods, np.nan, dtype=float)
        candidate_resource_available = False
        if candidate_core_valid:
            candidate_aggregate = self.economy.aggregate_allocations(allocations)
            candidate_residual = candidate_aggregate - aggregate_endowment
            scales = np.maximum.reduce(
                [
                    np.abs(candidate_aggregate),
                    np.abs(aggregate_endowment),
                    np.ones(self.economy.n_goods),
                ]
            )
            market_limits = (
                self.tolerances.market_abs_tol
                + self.tolerances.market_rel_tol * scales
            )
            candidate_resource_available = True

        reoptimized_allocations = np.empty(expected_allocation_shape, dtype=float)
        reoptimized_residual = np.full(self.economy.n_goods, np.inf, dtype=float)
        demand_recomputed = False
        try:
            reoptimized_allocations = self.economy.individual_demands(prices)
            reoptimized_residual = (
                self.economy.aggregate_allocations(reoptimized_allocations)
                - aggregate_endowment
            )
            demand_recomputed = bool(np.all(np.isfinite(reoptimized_allocations)))
        except (ValueError, ArithmeticError) as exc:
            notes.append(f"Independent demand recomputation failed: {exc}")

        budget_residuals: dict[str, float] = {}
        budget_exhaustion_gaps: dict[str, float] = {}
        feasibility_violations: dict[str, float] = {}
        utility_gaps: dict[str, float | None] = {}
        unique_bundle_gaps: dict[str, float | None] = {}
        optimality_results: dict[str, ConsumerOptimalityResult] = {}
        budget_violations: list[float] = []
        exhaustion_values: list[float] = []
        feasibility_values: list[float] = []
        optimality_values: list[float] = []
        optimality_oracle_available = candidate_core_valid

        if candidate_core_valid:
            for row, consumer in enumerate(self.economy.consumers):
                bundle = allocations[row]
                residual = consumer.budget_residual(prices, bundle)
                budget_residuals[consumer.id] = residual
                exhaustion_gap = abs(residual)
                budget_exhaustion_gaps[consumer.id] = exhaustion_gap
                budget_violations.append(max(0.0, -residual))
                exhaustion_values.append(exhaustion_gap)

                feasibility_violation = consumer.consumption_feasibility_violation(
                    bundle
                )
                feasibility_violations[consumer.id] = feasibility_violation
                feasibility_values.append(feasibility_violation)
                try:
                    result = consumer.evaluate_optimality(prices, bundle)
                except (ValueError, ArithmeticError) as exc:
                    optimality_oracle_available = False
                    notes.append(
                        f"Consumer {consumer.id} optimality is UNSUPPORTED: {exc}"
                    )
                    result = ConsumerOptimalityResult(
                        feasible=feasibility_violation == 0.0,
                        candidate_utility=None,
                        optimal_utility=None,
                        utility_gap=None,
                        budget_violation=max(0.0, -residual),
                        method=(
                            "UNSUPPORTED_UTILITY_OPTIMALITY_ORACLE:"
                            f"{type(consumer.preference).__name__}"
                        ),
                        feasibility_violation=feasibility_violation,
                        unique_demand_bundle_gap=None,
                    )
                optimality_results[consumer.id] = result
                utility_gaps[consumer.id] = result.utility_gap
                unique_bundle_gaps[consumer.id] = (
                    result.unique_demand_bundle_gap
                )
                if result.utility_gap is None:
                    optimality_values.append(float("inf"))
                else:
                    optimality_values.append(abs(result.utility_gap))
        else:
            optimality_oracle_available = False

        max_budget_violation = max(budget_violations, default=float("inf"))
        max_budget_exhaustion = max(exhaustion_values, default=float("inf"))
        max_feasibility_violation = max(
            feasibility_values, default=float("inf")
        )
        max_optimality_gap = max(optimality_values, default=float("inf"))

        market_violations = np.full(self.economy.n_goods, np.inf, dtype=float)
        if candidate_resource_available:
            for index, commodity in enumerate(self.economy.commodities):
                residual = float(candidate_residual[index])
                if commodity.clearing_rule is ClearingRule.EXACT:
                    market_violations[index] = abs(residual)
                else:
                    market_violations[index] = max(residual, 0.0)

        candidate_walras_residual = float("inf")
        if candidate_resource_available:
            candidate_walras_residual = float(np.dot(prices, candidate_residual))

        reoptimized_walras_residual = float("inf")
        if demand_recomputed and prices.shape == expected_price_shape:
            reoptimized_walras_residual = float(
                np.dot(prices, reoptimized_residual)
            )

        strict_market = bool(
            candidate_resource_available
            and np.all(market_violations <= market_limits)
        )
        factor = self.tolerances.approximate_factor
        approximate_market = bool(
            candidate_resource_available
            and np.all(market_violations <= factor * market_limits)
        )

        checks = {
            "solver_success": bool(candidate.solver_success),
            "finite_values": finite_values,
            "price_normalization": (
                normalization_error <= self.tolerances.normalization_tol
            ),
            "price_sign_restrictions": price_sign_violation == 0.0,
            "consumer_feasibility": (
                max_feasibility_violation <= self.tolerances.feasibility_tol
            ),
            "budget_feasibility": (
                max_budget_violation <= self.tolerances.budget_tol
            ),
            "budget_exhaustion": (
                max_budget_exhaustion <= self.tolerances.budget_tol
            ),
            "optimality_oracle_available": optimality_oracle_available,
            "consumer_optimality": (
                optimality_oracle_available
                and max_optimality_gap <= self.tolerances.optimality_tol
            ),
            "market_clearing": strict_market,
            "walras_law": (
                abs(candidate_walras_residual) <= self.tolerances.walras_tol
            ),
        }
        hard_names = (
            "solver_success",
            "finite_values",
            "price_normalization",
            "price_sign_restrictions",
            "consumer_feasibility",
            "budget_feasibility",
            "optimality_oracle_available",
            "consumer_optimality",
            "market_clearing",
            "walras_law",
        )
        strict_pass = all(checks[name] for name in hard_names)

        approximate_pass = bool(
            candidate.solver_success
            and finite_values
            and candidate_resource_available
            and optimality_oracle_available
            and normalization_error <= factor * self.tolerances.normalization_tol
            and price_sign_violation <= factor * self.tolerances.price_sign_tol
            and max_feasibility_violation
            <= factor * self.tolerances.feasibility_tol
            and max_budget_violation <= factor * self.tolerances.budget_tol
            and max_optimality_gap <= factor * self.tolerances.optimality_tol
            and approximate_market
            and abs(candidate_walras_residual)
            <= factor * self.tolerances.walras_tol
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
            "max_consumer_feasibility_violation": max_feasibility_violation,
            "max_budget_violation": max_budget_violation,
            "max_budget_exhaustion_gap": max_budget_exhaustion,
            "max_abs_utility_gap": max_optimality_gap,
            "max_market_violation": float(np.max(market_violations)),
            "abs_candidate_walras_residual": abs(candidate_walras_residual),
            "abs_reoptimized_walras_residual": abs(
                reoptimized_walras_residual
            ),
        }
        return EquilibriumDiagnosticsReport(
            classification=classification,
            passed=strict_pass,
            checks=checks,
            errors=errors,
            signed_l1_prices=signed_l1_prices,
            candidate_aggregate_allocation=candidate_aggregate.tolist(),
            candidate_resource_residual=candidate_residual.tolist(),
            market_limits=market_limits.tolist(),
            candidate_walras_residual=candidate_walras_residual,
            reoptimized_allocations=(
                reoptimized_allocations.tolist() if demand_recomputed else []
            ),
            reoptimized_resource_residual=reoptimized_residual.tolist(),
            reoptimized_walras_residual=reoptimized_walras_residual,
            budget_residuals=budget_residuals,
            budget_exhaustion_gaps=budget_exhaustion_gaps,
            consumer_feasibility_violations=feasibility_violations,
            utility_gaps=utility_gaps,
            unique_demand_bundle_gaps=unique_bundle_gaps,
            consumer_optimality_results=optimality_results,
            notes=tuple(notes),
        )
