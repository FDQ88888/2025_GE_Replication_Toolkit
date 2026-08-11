import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    ClearingRule,
    EmissionTaxEconomy,
    EmissionTaxEquilibriumDiagnostics,
    EmissionTaxPolicy,
    FixedNumeraire,
    PaperExample1QuotaSolver,
    PaperTaxConvention,
    PriceSign,
    PriceSignRestrictions,
    QuotaEquilibriumDiagnostics,
    build_emission_tax_candidate,
    build_paper_example_1,
    build_quota_candidate,
    map_emission_tax_to_global_quota,
    map_quota_to_emission_tax,
)


PRICE_SIGNS = PriceSignRestrictions(
    (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
)


def _mapped_example_1_tax():
    quota_economy, _ = build_paper_example_1(0.5)
    quota_candidate = PaperExample1QuotaSolver().solve(quota_economy)
    tax_economy = map_quota_to_emission_tax(
        quota_economy, quota_candidate.prices
    )
    tax_candidate = build_emission_tax_candidate(
        tax_economy,
        np.asarray(quota_candidate.prices),
        np.asarray(quota_candidate.allocations),
        np.asarray(quota_candidate.firm_plans)[1:],
        solver_success=True,
        solver_message="test mapping",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )
    return quota_economy, quota_candidate, tax_economy, tax_candidate


def test_emission_tax_policy_computes_C_revenue_and_V() -> None:
    policy = EmissionTaxPolicy(
        regulated_count=1,
        tax_rates=[0.25],
        rebate_shares={"a": 0.4, "b": 0.6},
        unregulated_rules=(ClearingRule.EXACT, ClearingRule.FREE_DISPOSAL),
    )

    np.testing.assert_allclose(policy.total_net_emissions([-0.5, 0.0, -0.2]), [0.5])
    assert policy.tax_revenue([-0.5, 0.0, -0.2]) == pytest.approx(0.125)
    np.testing.assert_allclose(policy.compliance_violations([-0.5, 0.0, -0.2]), 0.0)
    np.testing.assert_allclose(
        policy.compliance_violations([0.1, 0.2, 0.3]), [0.1, 0.2, 0.3]
    )


def test_tax_coordinate_conversion_roundtrip_scales_p_and_t_together() -> None:
    paper_prices = np.array([-0.25, 0.25, 0.5])
    paper_tax = np.array([0.25])
    internal = PaperTaxConvention.to_fixed_numeraire(
        paper_prices, paper_tax, FixedNumeraire(index=2, value=1.0)
    )
    roundtrip = PaperTaxConvention.to_paper_l1(
        internal.prices, internal.tax_rates
    )

    assert internal.scale == pytest.approx(2.0)
    np.testing.assert_allclose(internal.prices, [-0.5, 0.5, 1.0])
    np.testing.assert_allclose(internal.tax_rates, [0.5])
    np.testing.assert_allclose(roundtrip.prices, paper_prices)
    np.testing.assert_allclose(roundtrip.tax_rates, paper_tax)


def test_tax_coordinate_conversion_rejects_price_only_rescaling() -> None:
    with pytest.raises(ValueError, match="proj_k"):
        PaperTaxConvention.to_paper_l1([-0.5, 0.5, 1.0], [0.25])


def test_theorem_3_mapping_preserves_example_1_candidate_and_income() -> None:
    _, quota_candidate, tax_economy, tax_candidate = _mapped_example_1_tax()
    report = EmissionTaxEquilibriumDiagnostics(
        tax_economy, price_sign_restrictions=PRICE_SIGNS
    ).evaluate(tax_candidate)

    assert report.passed
    assert report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert dict(tax_economy.policy.rebate_shares) == {
        "omega_1": pytest.approx(0.0),
        "omega_2": pytest.approx(1.0),
    }
    np.testing.assert_allclose(tax_candidate.allocations, quota_candidate.allocations)
    assert tax_candidate.tax_revenue == pytest.approx(0.125)
    assert tax_candidate.income_breakdowns == quota_candidate.income_breakdowns


def test_theorem_4_reverse_mapping_is_verified_global_quota() -> None:
    _, _, tax_economy, tax_candidate = _mapped_example_1_tax()
    quota_economy = map_emission_tax_to_global_quota(
        tax_economy, tax_candidate.allocations, tax_candidate.firm_plans
    )
    plans = np.vstack([np.zeros(3), tax_candidate.firm_plans])
    candidate = build_quota_candidate(
        quota_economy,
        np.asarray(tax_candidate.prices),
        np.asarray(tax_candidate.allocations),
        plans,
        solver_success=True,
        solver_message="test reverse mapping",
        solver_method="test",
        iterations=0,
        function_calls=0,
        metadata={},
    )
    report = QuotaEquilibriumDiagnostics(
        quota_economy, price_sign_restrictions=PRICE_SIGNS
    ).evaluate(candidate)

    assert report.passed
    np.testing.assert_allclose(quota_economy.policy.total_m, [-0.5])


def test_tax_budget_and_demand_are_invariant_to_positive_coordinate_scale() -> None:
    _, _, paper_economy, candidate = _mapped_example_1_tax()
    conversion = PaperTaxConvention.to_fixed_numeraire(
        candidate.prices,
        paper_economy.policy.tax_rates,
        FixedNumeraire(index=2, value=1.0),
    )
    scaled_economy = EmissionTaxEconomy(
        paper_economy.production_economy,
        EmissionTaxPolicy(
            regulated_count=1,
            tax_rates=conversion.tax_rates,
            rebate_shares=paper_economy.policy.rebate_shares,
            unregulated_rules=paper_economy.policy.unregulated_rules,
        ),
    )
    paper_demand = paper_economy.individual_demands(
        candidate.prices, candidate.allocations, candidate.firm_plans
    )
    scaled_demand = scaled_economy.individual_demands(
        conversion.prices, candidate.allocations, candidate.firm_plans
    )
    paper_income = paper_economy.income_breakdowns(
        candidate.prices, candidate.allocations, candidate.firm_plans
    )
    scaled_income = scaled_economy.income_breakdowns(
        conversion.prices, candidate.allocations, candidate.firm_plans
    )

    np.testing.assert_allclose(paper_demand, scaled_demand)
    for consumer_id in paper_income:
        assert scaled_income[consumer_id].total_income == pytest.approx(
            conversion.scale * paper_income[consumer_id].total_income
        )


def test_tax_diagnostics_rejects_tampered_emissions_cache() -> None:
    _, _, tax_economy, candidate = _mapped_example_1_tax()
    candidate.total_net_emissions[0] += 0.1

    report = EmissionTaxEquilibriumDiagnostics(tax_economy).evaluate(candidate)

    assert not report.passed
    assert not report.checks["candidate_cache_consistency"]


def test_tax_diagnostics_rejects_wrong_policy_price() -> None:
    _, _, tax_economy, candidate = _mapped_example_1_tax()
    candidate.prices[0] = -0.2

    report = EmissionTaxEquilibriumDiagnostics(tax_economy).evaluate(candidate)

    assert not report.passed
    assert not report.checks["tax_price_constraint_proj_k_p_equals_negative_t"]
