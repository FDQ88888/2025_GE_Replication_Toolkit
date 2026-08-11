"""Narrow nonlinear solvers for paper quota Examples 1 and 2."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

import numpy as np
from scipy.optimize import least_squares

from duanmu_ge_lab.core.production import LinearRayTechnology
from duanmu_ge_lab.equilibrium.candidate import QuotaEquilibriumCandidate
from duanmu_ge_lab.policy.quota import QuotaEconomy


def build_quota_candidate(
    economy: QuotaEconomy,
    prices: np.ndarray,
    allocations: np.ndarray,
    firm_plans: np.ndarray,
    *,
    solver_success: bool,
    solver_message: str,
    solver_method: str,
    iterations: int | None,
    function_calls: int | None,
    metadata: dict[str, object],
) -> QuotaEquilibriumCandidate:
    """Build solver caches from the policy layer without asserting validity."""

    aggregate_demand = economy.aggregate_allocations(allocations)
    aggregate_endowment = economy.aggregate_endowment()
    aggregate_production = np.sum(firm_plans, axis=0)
    resource_residual = economy.candidate_resource_residual(allocations, firm_plans)
    profits = economy.firm_profit_breakdowns(prices, firm_plans)
    incomes = economy.income_breakdowns(prices, firm_plans)
    return QuotaEquilibriumCandidate(
        prices=prices,
        allocations=allocations,
        firm_plans=firm_plans,
        quota_prices=economy.policy.quota_prices(prices),
        aggregate_demand=aggregate_demand,
        aggregate_endowment=aggregate_endowment,
        aggregate_production=aggregate_production,
        resource_residual=resource_residual,
        operating_profits={
            firm_id: breakdown.operating_profit
            for firm_id, breakdown in profits.items()
        },
        quota_profit_terms={
            firm_id: breakdown.quota_profit
            for firm_id, breakdown in profits.items()
        },
        total_firm_profits={
            firm_id: breakdown.total_profit
            for firm_id, breakdown in profits.items()
        },
        income_breakdowns={
            consumer_id: breakdown.to_dict()
            for consumer_id, breakdown in incomes.items()
        },
        solver_success=solver_success,
        solver_message=solver_message,
        solver_method=solver_method,
        iterations=iterations,
        function_calls=function_calls,
        metadata=metadata,
    )


@dataclass(frozen=True, slots=True)
class PaperExample1QuotaSolver:
    """Recover Example 1 from resource, budget, profit, and price equations."""

    initial_guess: Sequence[float] = (-0.2, 0.3, 0.5, 0.4, 0.4, 0.6)
    tolerance: float = 1e-13
    max_nfev: int = 2000

    def solve(self, economy: QuotaEconomy) -> QuotaEquilibriumCandidate:
        if economy.n_goods != 3 or economy.n_consumers != 2 or economy.n_firms != 2:
            raise ValueError("PaperExample1QuotaSolver requires the Example 1 dimensions.")
        if tuple(firm.id for firm in economy.firms) != ("firm_0", "firm_1"):
            raise ValueError("PaperExample1QuotaSolver requires firms 0 and 1 in order.")
        private_technology = economy.firms[1].technology
        if not isinstance(private_technology, LinearRayTechnology):
            raise ValueError("Example 1 private firm must use a linear ray.")
        vector = np.asarray(private_technology.net_output_per_unit)

        def unpack(point: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            prices = point[:3]
            activity, electricity_1, coal_2 = point[3:]
            allocations = np.array(
                [[0.0, 0.0, electricity_1], [0.0, coal_2, 0.0]]
            )
            plans = np.vstack([np.zeros(3), activity * vector])
            return prices, allocations, plans

        def equations(point: np.ndarray) -> np.ndarray:
            prices, allocations, plans = unpack(point)
            resource = economy.candidate_resource_residual(allocations, plans)
            incomes = economy.income_breakdowns(prices, plans)
            budgets = np.array(
                [
                    consumer.budget_residual_at_income(
                        prices,
                        allocations[index],
                        incomes[consumer.id].total_income,
                    )
                    for index, consumer in enumerate(economy.consumers)
                ]
            )
            return np.concatenate(
                [
                    resource - economy.policy.target_vector(),
                    np.array(
                        [
                            float(np.dot(prices, vector)),
                            float(np.sum(np.abs(prices)) - 1.0),
                        ]
                    ),
                    budgets,
                ]
            )

        result = least_squares(
            equations,
            np.asarray(self.initial_guess, dtype=float),
            bounds=(
                np.array([-np.inf, 1e-12, 1e-12, 0.0, 0.0, 0.0]),
                np.array([0.0, np.inf, np.inf, np.inf, np.inf, np.inf]),
            ),
            xtol=self.tolerance,
            ftol=self.tolerance,
            gtol=self.tolerance,
            max_nfev=self.max_nfev,
        )
        prices, allocations, plans = unpack(result.x)
        return build_quota_candidate(
            economy,
            prices,
            allocations,
            plans,
            solver_success=bool(result.success),
            solver_message=str(result.message),
            solver_method="scipy.optimize.least_squares:paper_example_1_system",
            iterations=None,
            function_calls=int(result.nfev),
            metadata={
                "model_role": "PAPER_REPLICATION_EXAMPLE_1",
                "equation_residual_inf_norm": float(
                    np.max(np.abs(result.fun), initial=0.0)
                ),
                "cost": float(result.cost),
                "optimality": float(result.optimality),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
        )


@dataclass(frozen=True, slots=True)
class PaperExample2QuotaSolver:
    """Recover Example 2 without inserting its analytical equilibrium values."""

    initial_guess: Sequence[float] = (-0.2, 0.3, 0.5, 5.0, 1.0, 1.0, 1.5, 2.0)
    tolerance: float = 1e-13
    max_nfev: int = 3000

    def solve(self, economy: QuotaEconomy) -> QuotaEquilibriumCandidate:
        if economy.n_goods != 3 or economy.n_consumers != 3 or economy.n_firms != 3:
            raise ValueError("PaperExample2QuotaSolver requires the Example 2 dimensions.")
        if tuple(firm.id for firm in economy.firms) != (
            "firm_0",
            "firm_1",
            "firm_2",
        ):
            raise ValueError("PaperExample2QuotaSolver requires firms 0, 1, and 2 in order.")
        technologies = [economy.firms[index].technology for index in (1, 2)]
        if not all(isinstance(technology, LinearRayTechnology) for technology in technologies):
            raise ValueError("Example 2 private firms must use linear rays.")
        vectors = [
            np.asarray(technology.net_output_per_unit) for technology in technologies
        ]

        def unpack(point: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            prices = point[:3]
            activity_1, activity_2 = point[3:5]
            electricity = point[5:]
            allocations = np.column_stack(
                [np.zeros(3), np.zeros(3), electricity]
            )
            plans = np.vstack(
                [np.zeros(3), activity_1 * vectors[0], activity_2 * vectors[1]]
            )
            return prices, allocations, plans

        def equations(point: np.ndarray) -> np.ndarray:
            prices, allocations, plans = unpack(point)
            resource = economy.candidate_resource_residual(allocations, plans)
            incomes = economy.income_breakdowns(prices, plans)
            budgets = np.array(
                [
                    consumer.budget_residual_at_income(
                        prices,
                        allocations[index],
                        incomes[consumer.id].total_income,
                    )
                    for index, consumer in enumerate(economy.consumers)
                ]
            )
            return np.concatenate(
                [
                    resource - economy.policy.target_vector(),
                    np.array(
                        [
                            float(np.dot(prices, vectors[0])),
                            float(np.dot(prices, vectors[1])),
                            float(np.sum(np.abs(prices)) - 1.0),
                        ]
                    ),
                    budgets,
                ]
            )

        result = least_squares(
            equations,
            np.asarray(self.initial_guess, dtype=float),
            bounds=(
                np.array(
                    [-np.inf, 1e-12, 1e-12, 0.0, 0.0, 0.0, 0.0, 0.0]
                ),
                np.array([0.0, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]),
            ),
            xtol=self.tolerance,
            ftol=self.tolerance,
            gtol=self.tolerance,
            max_nfev=self.max_nfev,
        )
        refined_point = result.x.copy()
        price_system = np.vstack(
            [vectors[0], vectors[1], np.array([-1.0, 1.0, 1.0])]
        )
        refined_point[:3] = np.linalg.solve(
            price_system, np.array([0.0, 0.0, 1.0])
        )
        prices, allocations, plans = unpack(refined_point)
        refined_residual = equations(refined_point)
        return build_quota_candidate(
            economy,
            prices,
            allocations,
            plans,
            solver_success=bool(result.success),
            solver_message=str(result.message),
            solver_method="scipy.optimize.least_squares:paper_example_2_system",
            iterations=None,
            function_calls=int(result.nfev),
            metadata={
                "model_role": "PAPER_REPLICATION_EXAMPLE_2",
                "equation_residual_inf_norm": float(
                    np.max(np.abs(refined_residual), initial=0.0)
                ),
                "price_refinement": (
                    "Solved the two zero-unit-margin equations and the signed-L1 "
                    "equation as a linear system; no analytical target was inserted."
                ),
                "cost": float(result.cost),
                "optimality": float(result.optimality),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
