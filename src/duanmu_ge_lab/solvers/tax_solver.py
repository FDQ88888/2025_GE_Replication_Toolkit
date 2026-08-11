"""Candidate construction helpers for emission-tax equilibria."""

import numpy as np

from duanmu_ge_lab.equilibrium.candidate import EmissionTaxEquilibriumCandidate
from duanmu_ge_lab.policy.tax import EmissionTaxEconomy


def build_emission_tax_candidate(
    economy: EmissionTaxEconomy,
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
) -> EmissionTaxEquilibriumCandidate:
    """Build non-authoritative caches from authoritative candidate coordinates."""

    residual = economy.candidate_resource_residual(allocations, firm_plans)
    emissions = economy.policy.total_net_emissions(residual)
    revenue = economy.policy.tax_revenue(residual)
    profits = economy.firm_profits(prices, firm_plans)
    incomes = economy.income_breakdowns(prices, allocations, firm_plans)
    return EmissionTaxEquilibriumCandidate(
        prices=prices,
        allocations=allocations,
        firm_plans=firm_plans,
        tax_rates=economy.policy.tax_rates,
        total_net_emissions=emissions,
        tax_revenue=revenue,
        aggregate_demand=economy.aggregate_allocations(allocations),
        aggregate_endowment=economy.aggregate_endowment(),
        aggregate_production=np.sum(firm_plans, axis=0),
        resource_residual=residual,
        firm_profits={
            firm.id: float(profits[index])
            for index, firm in enumerate(economy.firms)
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
