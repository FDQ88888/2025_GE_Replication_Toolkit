import numpy as np
import pytest

from scripts.run_finite_weighted_lab import run


def test_finite_weighted_bad_absorption_experiment() -> None:
    result = run()

    assert result["status"] == "FINITE_WEIGHTED_EXPERIMENT_SUCCESS"
    assert "not a paper replication" in result["claim_scope"]
    assert "hyperfinite implementation" in result["claim_scope"]
    assert [item["N"] for item in result["finite_results"]] == [
        10,
        20,
        50,
        100,
        200,
    ]

    for item in result["finite_results"]:
        assert item["classification"] == "VERIFIED_CANDIDATE"
        np.testing.assert_allclose(item["prices"], [-1.0, 1.0], atol=0.0)
        np.testing.assert_allclose(
            item["aggregate_consumption"], [1.0, 2.0], atol=1e-13
        )
        np.testing.assert_allclose(item["resource_residual"], [0.0, 0.0], atol=1e-13)
        assert item["emissions_unabsorbed_bad"] == pytest.approx(0.0, abs=1e-13)
        assert item["population_weights"]["sum"] == pytest.approx(1.0, abs=1e-13)
        assert item["tail_diagnostics"]["largest_population_atom"] == pytest.approx(
            1.0 / item["N"]
        )
        assert item["tail_diagnostics"]["interpretation"].endswith(
            "not a uniform-integrability proof."
        )


def test_finite_weighted_midpoints_have_expected_tail_limit() -> None:
    result = run()
    finite_results = result["finite_results"]

    assert finite_results[-1]["tail_diagnostics"][
        "max_individual_bad_absorption"
    ] == pytest.approx(1.4975)
    assert finite_results[-1]["tail_diagnostics"][
        "weighted_truncated_mean"
    ] < finite_results[-1]["tail_diagnostics"][
        "max_individual_bad_absorption"
    ]
    assert finite_results[-1]["target_aggregate_error_linf"] <= 1e-13
