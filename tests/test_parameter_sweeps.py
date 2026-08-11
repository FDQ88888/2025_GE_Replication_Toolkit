import pytest

from scripts.run_tax_quota_sweeps import run, validate_cluster_counts


@pytest.fixture(scope="module")
def sweep_result():
    return run()


def test_tax_sweep_retains_all_discovered_branches(sweep_result) -> None:
    rows = sweep_result["tax_emissions_correspondence"]
    counts = [len(row["equilibria"]) for row in rows]

    assert counts == [3, 3, 3, 3, 3, 1, 1, 0]
    assert all(
        equilibrium["classification"] == "VERIFIED_CANDIDATE"
        for row in rows
        for equilibrium in row["equilibria"]
    )
    assert rows[-1]["paper_theoretical_status"] == "NO_EQUILIBRIUM"
    assert rows[-1]["numerical_search_status"] == (
        "DISCOVERED_0_VERIFIED_CANDIDATE_CLUSTERS"
    )


def test_tax_sweep_reports_sets_without_averaging(sweep_result) -> None:
    row = next(
        item
        for item in sweep_result["tax_emissions_correspondence"]
        if item["table_goods_sum_tax_rate"] == 0.01
    )
    emissions = [item["emissions"] for item in row["equilibria"]]

    assert len(emissions) == 3
    assert max(emissions) - min(emissions) > 0.04
    assert "average_emissions" not in row


def test_quota_sweep_retains_three_prices_and_fixed_emissions(sweep_result) -> None:
    for row in sweep_result["quota_price_correspondence"]:
        assert len(row["equilibria"]) == 3
        emissions = [item["emissions"] for item in row["equilibria"]]
        assert emissions == pytest.approx([row["quota_emissions"]] * 3, abs=1e-10)
        prices = {
            round(item["quota_price_goods_sum_convention"], 10)
            for item in row["equilibria"]
        }
        assert len(prices) == 3
        assert all(
            item["classification"] == "VERIFIED_CANDIDATE"
            for item in row["equilibria"]
        )


def test_sweep_status_validation_rejects_missing_required_cluster() -> None:
    assert validate_cluster_counts([3, 1], [3, 1], [3], [3])
    assert not validate_cluster_counts([3, 0], [3, 1], [3], [3])
