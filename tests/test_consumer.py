import numpy as np
import pytest

from duanmu_ge_lab.core import CobbDouglasUtility, Consumer


def test_consumer_wealth_is_endowment_value() -> None:
    consumer = Consumer(
        id="Consumer 1",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([1.0, 0.0]),
    )

    assert consumer.wealth(np.array([2.0, 1.0])) == pytest.approx(2.0)


def test_consumer_demand_uses_endowment_wealth() -> None:
    consumer = Consumer(
        id="Consumer 1",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([1.0, 0.0]),
    )

    demand = consumer.demand(np.array([2.0, 1.0]))

    np.testing.assert_allclose(demand, np.array([0.5, 1.0]), atol=1e-14)


def test_consumer_rejects_endowment_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="dimension"):
        Consumer(
            id="bad-dimension",
            preference=CobbDouglasUtility(np.array([0.5, 0.5])),
            endowment=np.array([1.0]),
        )


def test_budget_residual_uses_wealth_minus_expenditure() -> None:
    consumer = Consumer(
        id="Consumer 1",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([1.0, 0.0]),
    )

    residual = consumer.budget_residual(
        prices=np.array([2.0, 1.0]), bundle=np.array([0.5, 1.0])
    )

    assert residual == pytest.approx(0.0, abs=1e-14)


def test_consumer_optimality_uses_utility_gap_and_labels_unique_check() -> None:
    consumer = Consumer(
        id="Consumer 1",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([1.0, 0.0]),
    )

    result = consumer.evaluate_optimality(
        prices=np.array([1.0, 1.0]), bundle=np.array([0.8, 0.2])
    )

    assert result.feasible
    assert result.candidate_utility == pytest.approx(0.4)
    assert result.optimal_utility == pytest.approx(0.5)
    assert result.utility_gap == pytest.approx(0.1)
    assert result.budget_violation == 0.0
    assert result.unique_demand_bundle_gap == pytest.approx(0.3)
    assert "UNIQUE_DEMAND_BENCHMARK_CHECK" in result.method


def test_consumer_feasibility_rejects_negative_quantity() -> None:
    consumer = Consumer(
        id="Consumer 1",
        preference=CobbDouglasUtility(np.array([0.5, 0.5])),
        endowment=np.array([1.0, 0.0]),
    )

    assert consumer.consumption_feasibility_violation([-0.25, 1.25]) == 0.25
    assert not consumer.is_consumption_feasible([-0.25, 1.25])
