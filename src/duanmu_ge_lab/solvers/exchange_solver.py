"""One-dimensional root solver for the Milestone 1 two-good benchmark."""

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from scipy.optimize import root_scalar

from duanmu_ge_lab.core.commodity import ClearingRule
from duanmu_ge_lab.core.economy import ExchangeEconomy
from duanmu_ge_lab.equilibrium.candidate import EquilibriumCandidate
from duanmu_ge_lab.equilibrium.normalization import FixedNumeraire


@dataclass(frozen=True, slots=True)
class SolverConfiguration:
    """Configuration for a bracketed one-dimensional equilibrium root.

    Parameters
        bracket: Lower and upper values for the single independent price.
        method: SciPy bracketed method; Milestone 1 supports ``brentq`` only.
        xtol: Absolute root tolerance.
        rtol: Relative root tolerance.
        maxiter: Maximum scalar iterations.
    """

    bracket: tuple[float, float] = (0.05, 20.0)
    method: str = "brentq"
    xtol: float = 1e-13
    rtol: float = 1e-13
    maxiter: int = 100

    def __post_init__(self) -> None:
        lower, upper = self.bracket
        if not np.isfinite(lower) or not np.isfinite(upper) or lower >= upper:
            raise ValueError("Solver bracket must be finite with lower < upper.")
        if self.method != "brentq":
            raise ValueError("Milestone 1 supports only the brentq root method.")
        if self.xtol <= 0.0 or self.rtol <= 0.0:
            raise ValueError("Root tolerances must be positive.")
        if self.maxiter < 1:
            raise ValueError("maxiter must be positive.")


@dataclass(frozen=True, slots=True)
class ExchangeEquilibriumSolver:
    """Solve one non-numeraire market in a two-good exchange economy.

    Economic interpretation
        This solver is intentionally limited to the Milestone 1 benchmark. With one
        numeraire in a two-good economy, it solves only the remaining market equation.
        The unused market and Walras law are verified independently afterward.
    Mathematical definition
        If commodity ``r`` is not the numeraire, solve ``z_r(p)=0`` where
        ``z = aggregate demand - aggregate endowment``.
    Parameters
        configuration: Bracketed scalar root settings.
    Returns
        An unverified :class:`EquilibriumCandidate`.
    Raises
        NotImplementedError: For dimensions or clearing rules beyond Milestone 1.
        ValueError: For invalid normalization or bracket configuration.
    """

    configuration: SolverConfiguration = SolverConfiguration()

    def solve(
        self, economy: ExchangeEconomy, normalization: FixedNumeraire
    ) -> EquilibriumCandidate:
        """Solve the unique independent market equation and return a candidate."""

        if economy.n_goods != 2:
            raise NotImplementedError(
                "Milestone 1 ExchangeEquilibriumSolver supports exactly two goods."
            )
        if any(
            commodity.clearing_rule is not ClearingRule.EXACT
            for commodity in economy.commodities
        ):
            raise NotImplementedError(
                "Milestone 1 solver supports exact clearing for all commodities only."
            )
        if normalization.index >= economy.n_goods:
            raise ValueError("Numeraire index is outside the economy dimension.")

        independent_indexes = [
            index for index in range(economy.n_goods) if index != normalization.index
        ]
        solved_market_index = independent_indexes[0]

        def residual(independent_price: float) -> float:
            full_prices = normalization.decode(
                np.array([independent_price], dtype=float), economy.n_goods
            )
            return float(economy.excess_demand(full_prices)[solved_market_index])

        lower, upper = self.configuration.bracket
        f_lower = residual(lower)
        f_upper = residual(upper)
        if not np.isfinite(f_lower) or not np.isfinite(f_upper):
            raise ValueError("Bracket endpoint residuals must be finite.")

        metadata = {
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
                economy=economy,
                prices=prices,
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
            economy=economy,
            prices=prices,
            success=bool(result.converged),
            message=str(result.flag),
            iterations=int(result.iterations),
            function_calls=int(result.function_calls),
            metadata=metadata,
        )

    def _build_candidate(
        self,
        economy: ExchangeEconomy,
        prices: np.ndarray,
        success: bool,
        message: str,
        iterations: int,
        function_calls: int,
        metadata: dict[str, object],
    ) -> EquilibriumCandidate:
        allocations = economy.individual_demands(prices)
        aggregate_demand = economy.aggregate_allocations(allocations)
        aggregate_endowment = economy.aggregate_endowment()
        excess_demand = aggregate_demand - aggregate_endowment
        return EquilibriumCandidate(
            prices=prices,
            allocations=allocations,
            aggregate_demand=aggregate_demand,
            aggregate_endowment=aggregate_endowment,
            excess_demand=excess_demand,
            solver_success=success,
            solver_message=message,
            solver_method=self.configuration.method,
            iterations=iterations,
            function_calls=function_calls,
            metadata=metadata,
        )
