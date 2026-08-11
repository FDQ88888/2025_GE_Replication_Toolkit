import numpy as np
import pytest

from duanmu_ge_lab import (
    CandidateClassification,
    ClearingRule,
    CobbDouglasUtility,
    Commodity,
    CommodityKind,
    Consumer,
    EquilibriumCandidate,
    EquilibriumDiagnostics,
    ExchangeEconomy,
    FixedNumeraire,
    PriceSign,
    PriceSignRestrictions,
    build_signed_bad_absorption_benchmark,
    normalize_signed_l1,
    rescale_to_fixed_numeraire,
)


def _candidate(
    economy: ExchangeEconomy, prices: np.ndarray, allocations: np.ndarray
) -> EquilibriumCandidate:
    aggregate = economy.aggregate_allocations(allocations)
    endowment = economy.aggregate_endowment()
    return EquilibriumCandidate(
        prices=prices,
        allocations=allocations,
        aggregate_demand=aggregate,
        aggregate_endowment=endowment,
        excess_demand=aggregate - endowment,
        solver_success=True,
        solver_message="manual analytical candidate",
        solver_method="manual",
    )


def test_signed_l1_and_fixed_numeraire_round_trip_preserves_signs() -> None:
    prices = np.array([-2.0, 1.0])
    signed_l1 = normalize_signed_l1(prices)
    recovered = rescale_to_fixed_numeraire(
        signed_l1, FixedNumeraire(index=1, value=1.0)
    )

    np.testing.assert_allclose(signed_l1, [-2.0 / 3.0, 1.0 / 3.0], atol=1e-14)
    np.testing.assert_allclose(recovered, prices, atol=1e-14)


def test_rescaling_rejects_sign_reversing_numeraire() -> None:
    with pytest.raises(ValueError, match="positive scale"):
        rescale_to_fixed_numeraire(
            np.array([-0.5, 0.5]), FixedNumeraire(index=1, value=-1.0)
        )


def test_bad_kind_does_not_create_an_automatic_price_sign_rule() -> None:
    bad = Commodity(
        name="semantic bad",
        index=0,
        clearing_rule=ClearingRule.EXACT,
        kind=CommodityKind.BAD,
    )
    unrestricted = PriceSignRestrictions((PriceSign.ANY,))

    assert bad.kind is CommodityKind.BAD
    assert unrestricted.max_violation(np.array([2.0])) == 0.0


def test_signed_bad_absorption_candidate_is_verified() -> None:
    economy, normalization, restrictions, analytical = (
        build_signed_bad_absorption_benchmark()
    )
    candidate = _candidate(economy, analytical.prices, analytical.allocations)

    report = EquilibriumDiagnostics(
        economy,
        normalization,
        price_sign_restrictions=restrictions,
    ).evaluate(candidate)

    assert report.classification is CandidateClassification.VERIFIED_CANDIDATE
    assert report.passed
    assert report.checks["price_sign_restrictions"]
    assert report.checks["consumer_feasibility"]
    assert report.checks["consumer_optimality"]
    assert report.checks["market_clearing"]
    np.testing.assert_allclose(report.signed_l1_prices, [-0.5, 0.5], atol=1e-14)
    np.testing.assert_allclose(report.candidate_resource_residual, [0.0, 0.0])


def test_bad_absorption_bound_is_a_consumer_set_constraint() -> None:
    economy, _, _, _ = build_signed_bad_absorption_benchmark()
    consumer = economy.consumers[0]

    assert consumer.consumption_feasibility_violation([1.1, 2.0]) == pytest.approx(
        0.1
    )
    assert consumer.consumption_feasibility_violation([0.5, 2.0]) == 0.0


def test_free_disposal_and_exact_clearing_have_distinct_candidate_semantics() -> None:
    consumer = Consumer(
        id="Consumer",
        preference=CobbDouglasUtility([0.5, 0.5]),
        endowment=[1.0, 1.0],
    )
    free_economy = ExchangeEconomy(
        commodities=(
            Commodity(
                "Disposable good",
                0,
                ClearingRule.FREE_DISPOSAL,
                CommodityKind.GOOD,
            ),
            Commodity("Exact good", 1, ClearingRule.EXACT, CommodityKind.GOOD),
        ),
        consumers=(consumer,),
    )
    exact_economy = ExchangeEconomy(
        commodities=(
            Commodity("Exact good 1", 0, ClearingRule.EXACT, CommodityKind.GOOD),
            Commodity("Exact good 2", 1, ClearingRule.EXACT, CommodityKind.GOOD),
        ),
        consumers=(consumer,),
    )
    allocations = np.array([[0.5, 1.0]])
    prices = np.array([1.0, 1.0])

    free_report = EquilibriumDiagnostics(
        free_economy, FixedNumeraire(1, 1.0)
    ).evaluate(_candidate(free_economy, prices, allocations))
    exact_report = EquilibriumDiagnostics(
        exact_economy, FixedNumeraire(1, 1.0)
    ).evaluate(_candidate(exact_economy, prices, allocations))

    np.testing.assert_allclose(free_report.candidate_resource_residual, [-0.5, 0.0])
    assert free_report.checks["market_clearing"]
    assert not exact_report.checks["market_clearing"]
