import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    PaperExample1QuotaSolver,
    PaperExample2QuotaSolver,
    PriceSign,
    PriceSignRestrictions,
    QuotaEquilibriumDiagnostics,
    build_paper_example_1,
    build_paper_example_2,
    build_quota_candidate,
)


PAPER_PRICE_SIGNS = PriceSignRestrictions(
    (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
)


def _analytical_candidate(economy, analytical):
    return build_quota_candidate(
        economy,
        analytical.prices,
        analytical.allocations,
        analytical.firm_plans,
        solver_success=True,
        solver_message="analytical test coordinate",
        solver_method="test_fixture",
        iterations=0,
        function_calls=0,
        metadata={"model_role": "PAPER_ANALYTICAL_TEST_FIXTURE"},
    )


def test_example_1_paper_accounting_single_source_of_truth() -> None:
    economy, analytical = build_paper_example_1(0.5)
    profits = economy.firm_profit_breakdowns(
        analytical.prices, analytical.firm_plans
    )
    incomes = economy.income_breakdowns(analytical.prices, analytical.firm_plans)
    residual = economy.candidate_resource_residual(
        analytical.allocations, analytical.firm_plans
    )

    assert profits["firm_0"].operating_profit == 0.0
    assert profits["firm_0"].quota_profit == pytest.approx(0.125)
    assert profits["firm_1"].total_profit == pytest.approx(0.0)
    assert incomes["omega_1"].total_income == pytest.approx(0.25)
    assert incomes["omega_2"].total_income == pytest.approx(0.125)
    np.testing.assert_allclose(residual, [-0.5, 0.0, 0.0])
    assert economy.quota_adjusted_walras_residual(
        analytical.prices, analytical.allocations, analytical.firm_plans
    ) == pytest.approx(0.0)


def test_example_1_analytical_candidate_is_verified() -> None:
    economy, analytical = build_paper_example_1(0.5)
    report = QuotaEquilibriumDiagnostics(
        economy, price_sign_restrictions=PAPER_PRICE_SIGNS
    ).evaluate(_analytical_candidate(economy, analytical))

    assert report.passed
    assert report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert all(report.checks.values())


def test_example_1_solver_recovers_paper_values() -> None:
    economy, analytical = build_paper_example_1(0.5)
    candidate = PaperExample1QuotaSolver().solve(economy)
    report = QuotaEquilibriumDiagnostics(
        economy, price_sign_restrictions=PAPER_PRICE_SIGNS
    ).evaluate(candidate)

    assert report.passed
    np.testing.assert_allclose(candidate.prices, analytical.prices, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(
        candidate.allocations, analytical.allocations, atol=1e-12, rtol=0.0
    )
    np.testing.assert_allclose(
        candidate.firm_plans, analytical.firm_plans, atol=1e-12, rtol=0.0
    )


def test_quota_diagnostics_rejects_tampered_quota_price_cache() -> None:
    economy, analytical = build_paper_example_1(0.5)
    candidate = _analytical_candidate(economy, analytical)
    candidate.quota_prices[0] += 0.01

    report = QuotaEquilibriumDiagnostics(economy).evaluate(candidate)

    assert not report.passed
    assert not report.checks["quota_price_identity"]
    assert not report.checks["candidate_cache_consistency"]


def test_quota_diagnostics_rejects_noncompliant_candidate_coordinates() -> None:
    economy, analytical = build_paper_example_1(0.5)
    candidate = _analytical_candidate(economy, analytical)
    candidate.allocations[0, 2] += 0.01

    report = QuotaEquilibriumDiagnostics(economy).evaluate(candidate)

    assert not report.passed
    assert not report.checks["quota_compliance_Z_m"]
    assert report.errors["max_quota_compliance_violation"] == pytest.approx(0.01)


def test_quota_diagnostics_use_candidate_quantities_even_with_consistent_cache() -> None:
    economy, analytical = build_paper_example_1(0.5)
    allocations = analytical.allocations.copy()
    allocations[0, 2] += 0.01
    candidate = build_quota_candidate(
        economy,
        analytical.prices,
        allocations,
        analytical.firm_plans,
        solver_success=True,
        solver_message="internally cached but policy-infeasible candidate",
        solver_method="test_fixture",
        iterations=0,
        function_calls=0,
        metadata={},
    )

    report = QuotaEquilibriumDiagnostics(economy).evaluate(candidate)

    assert report.checks["candidate_cache_consistency"]
    assert not report.checks["quota_compliance_Z_m"]
    np.testing.assert_allclose(
        report.candidate_resource_residual, [-0.5, 0.0, 0.01], atol=1e-14
    )
    assert report.errors["max_quota_compliance_violation"] == pytest.approx(0.01)


@pytest.mark.parametrize("regime", ["global_quota", "cap_and_trade"])
def test_example_2_solver_recovers_each_paper_regime(regime: str) -> None:
    economy, analytical = build_paper_example_2(3.0, regime)
    candidate = PaperExample2QuotaSolver().solve(economy)
    report = QuotaEquilibriumDiagnostics(
        economy, price_sign_restrictions=PAPER_PRICE_SIGNS
    ).evaluate(candidate)

    assert report.passed
    np.testing.assert_allclose(candidate.prices, analytical.prices, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(
        candidate.allocations, analytical.allocations, atol=1e-12, rtol=0.0
    )
    np.testing.assert_allclose(
        candidate.firm_plans, analytical.firm_plans, atol=1e-12, rtol=0.0
    )


def test_example_2_property_rights_change_distribution_not_aggregates() -> None:
    _, global_solution = build_paper_example_2(3.0, "global_quota")
    _, cap_solution = build_paper_example_2(3.0, "cap_and_trade")
    global_electricity = global_solution.allocations[:, 2]
    cap_electricity = cap_solution.allocations[:, 2]

    np.testing.assert_allclose(global_solution.prices, cap_solution.prices)
    np.testing.assert_allclose(
        np.sum(global_solution.allocations, axis=0),
        np.sum(cap_solution.allocations, axis=0),
    )
    np.testing.assert_allclose(
        global_electricity - cap_electricity, [0.25, 0.0, -0.25]
    )
    assert global_electricity[0] > cap_electricity[0]
    assert global_electricity[1] == cap_electricity[1]
    assert global_electricity[2] < cap_electricity[2]


def test_example_2_does_not_fabricate_paper_cardinal_utility() -> None:
    _, analytical = build_paper_example_2(3.0, "global_quota")

    assert analytical.paper_utility_data["cardinal_utility_is_explicit_in_paper"] is False
    assert "own_electricity_components" in analytical.paper_utility_data
