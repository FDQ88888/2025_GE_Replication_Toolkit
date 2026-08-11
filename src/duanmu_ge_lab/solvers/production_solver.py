"""Scalar equilibrium solver for the analytical two-good production benchmark."""

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import root_scalar

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.production_economy import ProductionEconomy
from duanmu_ge_lab.equilibrium.candidate import ProductionEquilibriumCandidate
from duanmu_ge_lab.equilibrium.normalization import FixedNumeraire
from duanmu_ge_lab.solvers.exchange_solver import SolverConfiguration


@dataclass(frozen=True, slots=True)
class ProductionEquilibriumSolver:
    """Solve one independent market in a two-good production economy.

    This narrow solver is an analytical-benchmark tool. It independently optimizes
    firms, computes ownership income, optimizes consumers, and solves one exact
    market equation under a fixed numeraire. Other markets and all candidate
    coordinates are checked afterward by production diagnostics.
    """

    configuration: SolverConfiguration = SolverConfiguration(bracket=(0.1, 0.8))

    def solve(
        self, economy: ProductionEconomy, normalization: FixedNumeraire
    ) -> ProductionEquilibriumCandidate:
        """Return an unverified production-equilibrium candidate."""

        if economy.n_goods != 2:
            raise NotImplementedError(
                "ProductionEquilibriumSolver currently supports exactly two goods."
            )
        if any(
            commodity.clearing_rule is not ClearingRule.EXACT
            for commodity in economy.commodities
        ):
            raise NotImplementedError(
                "The Milestone 2 solver supports exact clearing only."
            )
        if normalization.index >= economy.n_goods:
            raise ValueError("Numeraire index is outside the economy dimension.")
        independent_indexes = [
            index for index in range(economy.n_goods) if index != normalization.index
        ]
        solved_market_index = independent_indexes[0]

        def residual(independent_price: float) -> float:
            prices = normalization.decode(
                np.array([independent_price], dtype=float), economy.n_goods
            )
            return float(economy.excess_demand(prices)[solved_market_index])

        lower, upper = self.configuration.bracket
        f_lower = residual(lower)
        f_upper = residual(upper)
        if not np.isfinite(f_lower) or not np.isfinite(f_upper):
            raise ValueError("Bracket endpoint residuals must be finite.")
        metadata = {
            "model_role": "ANALYTICAL_PRODUCTION_BENCHMARK",
            "numeraire": {
                "index": normalization.index,
                "value": normalization.value,
            },
            "initial_bracket": [lower, upper],
            "solved_market_index": solved_market_index,
            "unused_market_indexes": [normalization.index],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if f_lower * f_upper > 0.0:
            probe = (lower + upper) / 2.0
            prices = normalization.decode(np.array([probe]), economy.n_goods)
            return self._build_candidate(
                economy,
                prices,
                success=False,
                message=(
                    "No sign change in the configured bracket: "
                    f"f({lower})={f_lower:.16g}, f({upper})={f_upper:.16g}."
                ),
                iterations=0,
                function_calls=2,
                metadata=metadata,
            )

        result = root_scalar(
            residual,
            bracket=self.configuration.bracket,
            method=self.configuration.method,
            xtol=self.configuration.xtol,
            rtol=self.configuration.rtol,
            maxiter=self.configuration.maxiter,
        )
        prices = normalization.decode(np.array([float(result.root)]), economy.n_goods)
        return self._build_candidate(
            economy,
            prices,
            success=bool(result.converged),
            message=str(result.flag),
            iterations=int(result.iterations),
            function_calls=int(result.function_calls),
            metadata=metadata,
        )

    def _build_candidate(
        self,
        economy: ProductionEconomy,
        prices: np.ndarray,
        success: bool,
        message: str,
        iterations: int,
        function_calls: int,
        metadata: dict[str, object],
    ) -> ProductionEquilibriumCandidate:
        firm_plans = economy.optimal_firm_plans(prices)
        allocations = economy.individual_demands(prices, firm_plans)
        firm_profits = economy.firm_profits(prices, firm_plans)
        incomes = economy.income_breakdowns(prices, firm_plans)
        aggregate_demand = economy.aggregate_allocations(allocations)
        aggregate_endowment = economy.aggregate_endowment()
        aggregate_production = np.sum(firm_plans, axis=0)
        resource_residual = economy.candidate_resource_residual(
            allocations, firm_plans
        )
        return ProductionEquilibriumCandidate(
            prices=prices,
            allocations=allocations,
            firm_plans=firm_plans,
            aggregate_demand=aggregate_demand,
            aggregate_endowment=aggregate_endowment,
            aggregate_production=aggregate_production,
            resource_residual=resource_residual,
            firm_profits=firm_profits,
            income_breakdowns={
                consumer_id: breakdown.to_dict()
                for consumer_id, breakdown in incomes.items()
            },
            solver_success=success,
            solver_message=message,
            solver_method=self.configuration.method,
            iterations=iterations,
            function_calls=function_calls,
            metadata=metadata,
        )
