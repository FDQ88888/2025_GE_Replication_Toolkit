import numpy as np
import pytest

from duanmu_ge_lab import (
    ClearingRule,
    LinearRayTechnology,
    ProfitMarginRegime,
    QuotaPolicy,
    UnboundedProfitError,
    ZeroTechnology,
)


def test_quota_policy_preserves_paper_signs_and_price_identity() -> None:
    policy = QuotaPolicy(
        regulated_count=1,
        firm_quotas={"firm_0": [-0.3], "firm_1": [-0.2]},
        unregulated_rules=(ClearingRule.EXACT, ClearingRule.FREE_DISPOSAL),
    )

    assert policy.n_goods == 3
    np.testing.assert_allclose(policy.total_m, [-0.5])
    np.testing.assert_allclose(policy.quota_prices([-0.25, 0.25, 0.5]), [0.25])
    assert policy.quota_profit_term("firm_0", [-0.25, 0.25, 0.5]) == pytest.approx(
        0.075
    )
    assert policy.to_dict()["introduces_permit_commodity"] is False


def test_quota_policy_rejects_positive_m_assignment() -> None:
    with pytest.raises(ValueError, match="nonpositive"):
        QuotaPolicy(
            regulated_count=1,
            firm_quotas={"firm_0": [0.1]},
            unregulated_rules=(),
        )


def test_quota_compliance_distinguishes_exact_and_free_disposal() -> None:
    policy = QuotaPolicy(
        regulated_count=1,
        firm_quotas={"firm_0": [-0.5]},
        unregulated_rules=(ClearingRule.EXACT, ClearingRule.FREE_DISPOSAL),
    )

    np.testing.assert_allclose(policy.compliance_violations([-0.5, 0.0, -0.2]), 0.0)
    np.testing.assert_allclose(
        policy.compliance_violations([-0.4, 0.1, 0.1]), [0.1, 0.1, 0.1]
    )


def test_linear_ray_detects_unbounded_positive_profit() -> None:
    technology = LinearRayTechnology([1.0, -1.0, 1.0])

    with pytest.raises(UnboundedProfitError, match="unbounded"):
        technology.optimal_plan([1.0, 0.0, 0.0])


def test_linear_ray_accepts_any_feasible_zero_margin_plan_as_optimal() -> None:
    technology = LinearRayTechnology([1.0, -1.0, 1.0])
    result = technology.evaluate_optimality(
        [-0.25, 0.25, 0.5], [2.0, -2.0, 2.0]
    )

    assert result.feasible
    assert result.profit_gap == pytest.approx(0.0)
    assert result.optimal_plan == pytest.approx([2.0, -2.0, 2.0])
    assert result.profit_margin_assessment is not None
    assert (
        result.profit_margin_assessment.regime
        is ProfitMarginRegime.NUMERICAL_ZERO
    )


@pytest.mark.parametrize("perturbation", [5e-17, -5e-17])
def test_linear_ray_treats_roundoff_sized_margin_as_numerical_zero(
    perturbation: float,
) -> None:
    technology = LinearRayTechnology([1.0, -1.0, perturbation])
    prices = np.ones(3)

    assessment = technology.assess_unit_margin(prices)
    result = technology.evaluate_optimality(prices, [3.0, -3.0, 3.0 * perturbation])

    assert assessment.margin == pytest.approx(perturbation, rel=0.0, abs=1e-30)
    assert assessment.regime is ProfitMarginRegime.NUMERICAL_ZERO
    assert result.profit_gap == 0.0


def test_linear_ray_distinguishes_clear_positive_and_negative_margins() -> None:
    positive = LinearRayTechnology([1.0, -1.0, 1e-3])
    negative = LinearRayTechnology([1.0, -1.0, -1e-3])
    prices = np.ones(3)

    with pytest.raises(UnboundedProfitError, match="scale-aware tolerance"):
        positive.optimal_plan(prices)
    np.testing.assert_array_equal(negative.optimal_plan(prices), np.zeros(3))
    assert (
        negative.assess_unit_margin(prices).regime
        is ProfitMarginRegime.NEGATIVE_SHUTDOWN
    )


def test_linear_ray_margin_regime_is_stable_under_positive_rescaling() -> None:
    technology = LinearRayTechnology([1.0, -1.0, 5e-17])
    base = technology.assess_unit_margin(np.ones(3))
    scaled_prices = technology.assess_unit_margin(10.0 * np.ones(3))
    scaled_technology = LinearRayTechnology(0.1 * np.array([1.0, -1.0, 5e-17]))
    inverse_scaled_vector = scaled_technology.assess_unit_margin(10.0 * np.ones(3))

    assert base.regime is ProfitMarginRegime.NUMERICAL_ZERO
    assert scaled_prices.regime is ProfitMarginRegime.NUMERICAL_ZERO
    assert inverse_scaled_vector.regime is ProfitMarginRegime.NUMERICAL_ZERO


def test_zero_technology_rejects_government_production() -> None:
    technology = ZeroTechnology(3)

    assert technology.feasibility_violation([0.0, 0.0, 0.0]) == 0.0
    assert technology.feasibility_violation([0.0, 1e-3, 0.0]) == pytest.approx(1e-3)
