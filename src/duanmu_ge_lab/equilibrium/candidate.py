"""Unverified solver output containers and candidate classifications."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


class CandidateClassification(str, Enum):
    """Classification assigned only after independent diagnostics."""

    VERIFIED_CANDIDATE = "VERIFIED_CANDIDATE"
    APPROXIMATE_CANDIDATE = "APPROXIMATE_CANDIDATE"
    SOLVER_POINT = "SOLVER_POINT"
    FAILED_RUN = "FAILED_RUN"


@dataclass(slots=True)
class EquilibriumCandidate:
    """Store a solver point without asserting that it is an equilibrium.

    Economic interpretation
        A root solver can converge while budgets, optimality, another market, or
        normalization fail. This object records numerical output only.
    Mathematical definition
        Cached aggregates use ``z = demand - endowment``, but diagnostics use the
        candidate allocations for resource feasibility and independently recompute
        all other mathematical quantities.
    Parameters
        prices: Full candidate price vector.
        allocations: Candidate individual demand/allocation matrix.
        aggregate_demand: Solver-cached aggregate demand.
        aggregate_endowment: Solver-cached aggregate endowment.
        excess_demand: Solver-cached excess demand.
        solver_success: Numerical solver convergence flag only.
        solver_message: Concise solver status.
        solver_method: Numerical method name.
        iterations: Solver iterations when available.
        function_calls: Residual evaluations when available.
        metadata: JSON-oriented run metadata; never diagnostic pass flags.
    """

    prices: Sequence[float] | FloatArray
    allocations: Sequence[Sequence[float]] | FloatArray
    aggregate_demand: Sequence[float] | FloatArray
    aggregate_endowment: Sequence[float] | FloatArray
    excess_demand: Sequence[float] | FloatArray
    solver_success: bool
    solver_message: str
    solver_method: str
    iterations: int | None = None
    function_calls: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.prices = np.asarray(self.prices, dtype=float).copy()
        self.allocations = np.asarray(self.allocations, dtype=float).copy()
        self.aggregate_demand = np.asarray(self.aggregate_demand, dtype=float).copy()
        self.aggregate_endowment = np.asarray(
            self.aggregate_endowment, dtype=float
        ).copy()
        self.excess_demand = np.asarray(self.excess_demand, dtype=float).copy()
        self.metadata = dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the solver output."""

        return {
            "prices": np.asarray(self.prices).tolist(),
            "allocations": np.asarray(self.allocations).tolist(),
            "aggregate_demand": np.asarray(self.aggregate_demand).tolist(),
            "aggregate_endowment": np.asarray(self.aggregate_endowment).tolist(),
            "excess_demand": np.asarray(self.excess_demand).tolist(),
            "solver_success": bool(self.solver_success),
            "solver_message": self.solver_message,
            "solver_method": self.solver_method,
            "iterations": self.iterations,
            "function_calls": self.function_calls,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class ProductionEquilibriumCandidate:
    """Unverified solver output for a finite production economy.

    The authoritative candidate coordinates are prices, consumer allocations, and
    firm net-output plans. All aggregate, profit, income, and residual fields are
    solver caches that independent diagnostics must recompute.
    """

    prices: Sequence[float] | FloatArray
    allocations: Sequence[Sequence[float]] | FloatArray
    firm_plans: Sequence[Sequence[float]] | FloatArray
    aggregate_demand: Sequence[float] | FloatArray
    aggregate_endowment: Sequence[float] | FloatArray
    aggregate_production: Sequence[float] | FloatArray
    resource_residual: Sequence[float] | FloatArray
    firm_profits: Sequence[float] | FloatArray
    income_breakdowns: Mapping[str, Mapping[str, float]]
    solver_success: bool
    solver_message: str
    solver_method: str
    iterations: int | None = None
    function_calls: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.prices = np.asarray(self.prices, dtype=float).copy()
        self.allocations = np.asarray(self.allocations, dtype=float).copy()
        self.firm_plans = np.asarray(self.firm_plans, dtype=float).copy()
        self.aggregate_demand = np.asarray(self.aggregate_demand, dtype=float).copy()
        self.aggregate_endowment = np.asarray(
            self.aggregate_endowment, dtype=float
        ).copy()
        self.aggregate_production = np.asarray(
            self.aggregate_production, dtype=float
        ).copy()
        self.resource_residual = np.asarray(
            self.resource_residual, dtype=float
        ).copy()
        self.firm_profits = np.asarray(self.firm_profits, dtype=float).copy()
        self.income_breakdowns = {
            consumer_id: dict(breakdown)
            for consumer_id, breakdown in self.income_breakdowns.items()
        }
        self.metadata = dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable solver record without verification claims."""

        return {
            "prices": np.asarray(self.prices).tolist(),
            "allocations": np.asarray(self.allocations).tolist(),
            "firm_plans": np.asarray(self.firm_plans).tolist(),
            "aggregate_demand": np.asarray(self.aggregate_demand).tolist(),
            "aggregate_endowment": np.asarray(self.aggregate_endowment).tolist(),
            "aggregate_production": np.asarray(
                self.aggregate_production
            ).tolist(),
            "resource_residual": np.asarray(self.resource_residual).tolist(),
            "firm_profits": np.asarray(self.firm_profits).tolist(),
            "income_breakdowns": {
                consumer_id: dict(breakdown)
                for consumer_id, breakdown in self.income_breakdowns.items()
            },
            "solver_success": bool(self.solver_success),
            "solver_message": self.solver_message,
            "solver_method": self.solver_method,
            "iterations": self.iterations,
            "function_calls": self.function_calls,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class QuotaEquilibriumCandidate:
    """Unverified quota-equilibrium output with explicit accounting caches."""

    prices: Sequence[float] | FloatArray
    allocations: Sequence[Sequence[float]] | FloatArray
    firm_plans: Sequence[Sequence[float]] | FloatArray
    quota_prices: Sequence[float] | FloatArray
    aggregate_demand: Sequence[float] | FloatArray
    aggregate_endowment: Sequence[float] | FloatArray
    aggregate_production: Sequence[float] | FloatArray
    resource_residual: Sequence[float] | FloatArray
    operating_profits: Mapping[str, float]
    quota_profit_terms: Mapping[str, float]
    total_firm_profits: Mapping[str, float]
    income_breakdowns: Mapping[str, Mapping[str, float]]
    solver_success: bool
    solver_message: str
    solver_method: str
    iterations: int | None = None
    function_calls: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "prices",
            "allocations",
            "firm_plans",
            "quota_prices",
            "aggregate_demand",
            "aggregate_endowment",
            "aggregate_production",
            "resource_residual",
        ):
            setattr(self, name, np.asarray(getattr(self, name), dtype=float).copy())
        self.operating_profits = dict(self.operating_profits)
        self.quota_profit_terms = dict(self.quota_profit_terms)
        self.total_firm_profits = dict(self.total_firm_profits)
        self.income_breakdowns = {
            consumer_id: dict(breakdown)
            for consumer_id, breakdown in self.income_breakdowns.items()
        }
        self.metadata = dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON data without making an equilibrium claim."""

        return {
            "prices": np.asarray(self.prices).tolist(),
            "allocations": np.asarray(self.allocations).tolist(),
            "firm_plans": np.asarray(self.firm_plans).tolist(),
            "quota_prices": np.asarray(self.quota_prices).tolist(),
            "aggregate_demand": np.asarray(self.aggregate_demand).tolist(),
            "aggregate_endowment": np.asarray(self.aggregate_endowment).tolist(),
            "aggregate_production": np.asarray(self.aggregate_production).tolist(),
            "resource_residual": np.asarray(self.resource_residual).tolist(),
            "operating_profits": dict(self.operating_profits),
            "quota_profit_terms": dict(self.quota_profit_terms),
            "total_firm_profits": dict(self.total_firm_profits),
            "income_breakdowns": {
                consumer_id: dict(breakdown)
                for consumer_id, breakdown in self.income_breakdowns.items()
            },
            "solver_success": bool(self.solver_success),
            "solver_message": self.solver_message,
            "solver_method": self.solver_method,
            "iterations": self.iterations,
            "function_calls": self.function_calls,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class EmissionTaxEquilibriumCandidate:
    """Unverified tax-equilibrium output with candidate-dependent tax caches."""

    prices: Sequence[float] | FloatArray
    allocations: Sequence[Sequence[float]] | FloatArray
    firm_plans: Sequence[Sequence[float]] | FloatArray
    tax_rates: Sequence[float] | FloatArray
    total_net_emissions: Sequence[float] | FloatArray
    tax_revenue: float
    aggregate_demand: Sequence[float] | FloatArray
    aggregate_endowment: Sequence[float] | FloatArray
    aggregate_production: Sequence[float] | FloatArray
    resource_residual: Sequence[float] | FloatArray
    firm_profits: Mapping[str, float]
    income_breakdowns: Mapping[str, Mapping[str, float]]
    solver_success: bool
    solver_message: str
    solver_method: str
    iterations: int | None = None
    function_calls: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "prices",
            "allocations",
            "firm_plans",
            "tax_rates",
            "total_net_emissions",
            "aggregate_demand",
            "aggregate_endowment",
            "aggregate_production",
            "resource_residual",
        ):
            setattr(self, name, np.asarray(getattr(self, name), dtype=float).copy())
        self.tax_revenue = float(self.tax_revenue)
        self.firm_profits = dict(self.firm_profits)
        self.income_breakdowns = {
            consumer_id: dict(breakdown)
            for consumer_id, breakdown in self.income_breakdowns.items()
        }
        self.metadata = dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prices": np.asarray(self.prices).tolist(),
            "allocations": np.asarray(self.allocations).tolist(),
            "firm_plans": np.asarray(self.firm_plans).tolist(),
            "tax_rates": np.asarray(self.tax_rates).tolist(),
            "total_net_emissions": np.asarray(self.total_net_emissions).tolist(),
            "tax_revenue": self.tax_revenue,
            "aggregate_demand": np.asarray(self.aggregate_demand).tolist(),
            "aggregate_endowment": np.asarray(self.aggregate_endowment).tolist(),
            "aggregate_production": np.asarray(self.aggregate_production).tolist(),
            "resource_residual": np.asarray(self.resource_residual).tolist(),
            "firm_profits": dict(self.firm_profits),
            "income_breakdowns": {
                consumer_id: dict(breakdown)
                for consumer_id, breakdown in self.income_breakdowns.items()
            },
            "solver_success": bool(self.solver_success),
            "solver_message": self.solver_message,
            "solver_method": self.solver_method,
            "iterations": self.iterations,
            "function_calls": self.function_calls,
            "metadata": dict(self.metadata),
        }
