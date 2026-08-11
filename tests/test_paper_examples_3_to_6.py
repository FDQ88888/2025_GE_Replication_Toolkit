import numpy as np
import pytest

from duanmu_ge_lab import (
    EmissionTaxEquilibriumDiagnostics,
    PaperExample3TaxSolver,
    PaperExample5TargetSolver,
    QuotaEquilibriumDiagnostics,
    build_emission_tax_candidate,
    build_paper_example_3_tax_economy,
    build_paper_example_4_tax_economy,
    build_quota_candidate,
    map_emission_tax_to_global_quota,
    paper_example_3_reduction_percent,
    paper_example_3_signed_l1_prices,
    paper_example_4_coordinates,
)


def test_example_3_is_exactly_a_zero_firm_tax_economy() -> None:
    economy = build_paper_example_3_tax_economy(0.01)

    assert economy.n_firms == 0
    assert economy.production_economy.optimal_firm_plans(
        [-0.01 / 1.01, 0.5 / 1.01, 0.5 / 1.01]
    ).shape == (0, 3)


def test_example_3_table_i_row_discovers_three_verified_branches() -> None:
    economy = build_paper_example_3_tax_economy(0.01)
    roots = PaperExample3TaxSolver().solve_tax_rate(0.01)

    assert len(roots) == 3
    np.testing.assert_allclose(
        [root.eta for root in roots],
        [2.071166093697895, 0.8556519113512379, 0.5775837140288584],
        atol=1e-12,
        rtol=0.0,
    )
    np.testing.assert_allclose(
        [root.reduction_percent for root in roots],
        [26.21316273951955, 31.747874098553943, 38.085843736432295],
        atol=1e-10,
        rtol=0.0,
    )
    assert all(
        EmissionTaxEquilibriumDiagnostics(economy).evaluate(root.candidate).passed
        for root in roots
    )


def test_example_3_goods_sum_conversion_preserves_tax_price_identity() -> None:
    tau = 0.01
    prices = paper_example_3_signed_l1_prices(tau, 2.0)

    assert np.sum(np.abs(prices)) == pytest.approx(1.0)
    assert prices[0] == pytest.approx(-tau / (1.0 + tau))


def test_example_4_below_boundary_has_unit_emissions_and_verifies() -> None:
    economy = build_paper_example_4_tax_economy(0.2)
    prices, allocations, plans = paper_example_4_coordinates(0.2, 1.0)
    candidate = build_emission_tax_candidate(
        economy,
        prices,
        allocations,
        plans,
        solver_success=True,
        solver_message="test",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )
    report = EmissionTaxEquilibriumDiagnostics(economy).evaluate(candidate)

    assert report.passed
    np.testing.assert_allclose(candidate.total_net_emissions, [1.0])


@pytest.mark.parametrize("emissions", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_example_4_boundary_supports_emissions_continuum_sample(
    emissions: float,
) -> None:
    economy = build_paper_example_4_tax_economy(0.25)
    prices, allocations, plans = paper_example_4_coordinates(0.25, emissions)
    candidate = build_emission_tax_candidate(
        economy,
        prices,
        allocations,
        plans,
        solver_success=True,
        solver_message="test",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )

    assert EmissionTaxEquilibriumDiagnostics(economy).evaluate(candidate).passed
    assert candidate.total_net_emissions[0] == pytest.approx(emissions)


def test_example_4_formula_rejects_tax_above_the_paper_boundary() -> None:
    with pytest.raises(ValueError, match="1/4"):
        paper_example_4_coordinates(0.3, 1.0)


def test_example_5_target_solver_recovers_table_iii_prices() -> None:
    solver = PaperExample5TargetSolver(
        starts_eta_tau=((2.0, 0.011), (0.8, 0.0095), (0.55, 0.0075))
    )
    roots = solver.solve_target_reduction(0.30)

    assert len(roots) == 3
    np.testing.assert_allclose(
        [root.table_goods_sum_tax_rate for root in roots],
        [0.011448, 0.00951705, 0.0075832],
        atol=5e-7,
        rtol=0.0,
    )
    np.testing.assert_allclose(
        [root.reduction_percent for root in roots], [30.0, 30.0, 30.0], atol=1e-9
    )


def test_example_5_global_quota_mapping_fixes_emissions_at_point_28() -> None:
    root = PaperExample5TargetSolver(
        starts_eta_tau=((2.0, 0.011),)
    ).solve_target_reduction(0.30)[0]
    tax_economy = build_paper_example_3_tax_economy(
        root.table_goods_sum_tax_rate
    )
    quota_economy = map_emission_tax_to_global_quota(
        tax_economy, root.candidate.allocations, root.candidate.firm_plans
    )
    candidate = build_quota_candidate(
        quota_economy,
        np.asarray(root.candidate.prices),
        np.asarray(root.candidate.allocations),
        np.zeros((1, 3)),
        solver_success=True,
        solver_message="test",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )
    report = QuotaEquilibriumDiagnostics(quota_economy).evaluate(candidate)

    assert report.passed
    assert -report.candidate_resource_residual[0] == pytest.approx(0.28)


def test_example_6_quota_candidate_hits_target_but_tax_rate_is_not_selective() -> None:
    v = 0.5
    tax_economy = build_paper_example_4_tax_economy(0.25)
    prices, allocations, plans = paper_example_4_coordinates(0.25, v)
    quota_economy = map_emission_tax_to_global_quota(
        tax_economy, allocations, plans
    )
    candidate = build_quota_candidate(
        quota_economy,
        prices,
        allocations,
        np.vstack([np.zeros(3), plans]),
        solver_success=True,
        solver_message="test",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )
    report = QuotaEquilibriumDiagnostics(quota_economy).evaluate(candidate)

    assert report.passed
    assert -report.candidate_resource_residual[0] == pytest.approx(v)
    assert paper_example_3_reduction_percent(0.01, 2.0) != pytest.approx(30.0)
