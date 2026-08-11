import pytest

from scripts.run_welfare_distribution import run


def test_fixed_quota_property_rights_distribution_report() -> None:
    result = run()

    assert result["status"] == "WELFARE_DISTRIBUTION_SUCCESS"
    assert result["global_minus_cap_electricity"] == pytest.approx(
        [0.25, 0.0, -0.25], abs=1e-10
    )
    assert all(
        regime["total_emissions"] == pytest.approx(3.0)
        for regime in result["regimes"].values()
    )
    assert result["welfare_scope"]["weighted_welfare_reported"] is False
    assert result["welfare_scope"]["automatic_optimal_carbon_policy"] is False
    assert "aggregate_welfare" not in result
