from dataclasses import dataclass

import numpy as np

from duanmu_ge_lab import (
    CandidateClassification,
    CandidateFeatureBlocks,
    MultistartRun,
    StartKind,
    cluster_verified_candidates,
    solve_multistart,
)


@dataclass
class DummyCandidate:
    prices: np.ndarray
    allocations: np.ndarray
    firm_plans: np.ndarray
    solver_success: bool = True
    solver_message: str = "ok"
    solver_method: str = "dummy"

    def to_dict(self):
        return {"prices": self.prices.tolist(), "allocations": self.allocations.tolist()}


@dataclass
class DummyReport:
    classification: CandidateClassification

    def to_dict(self):
        return {"classification": self.classification.value}


def _dummy_candidate(value: float) -> DummyCandidate:
    return DummyCandidate(
        prices=np.array([-0.25, 0.25, 0.5]),
        allocations=np.array([[0.0, value, 1.0]]),
        firm_plans=np.empty((0, 3)),
    )


def test_multistart_random_seed_is_reproducible() -> None:
    solve = lambda start: _dummy_candidate(float(start[0]))
    diagnose = lambda candidate: DummyReport(
        CandidateClassification.VERIFIED_CANDIDATE
    )
    kwargs = dict(
        solve_from_start=solve,
        diagnose=diagnose,
        random_bounds=([0.0], [1.0]),
        random_count=5,
        random_seed=1234,
    )

    first = solve_multistart(**kwargs)
    second = solve_multistart(**kwargs)

    np.testing.assert_allclose(
        [run.initial_point for run in first],
        [run.initial_point for run in second],
    )
    assert all(run.start_kind is StartKind.RANDOM for run in first)


def test_multistart_retains_failures_and_all_start_kinds() -> None:
    def solve(start):
        if start[0] < 0.0:
            raise ValueError("negative start rejected")
        return _dummy_candidate(float(start[0]))

    runs = solve_multistart(
        solve,
        lambda candidate: DummyReport(CandidateClassification.VERIFIED_CANDIDATE),
        deterministic_starts=([-1.0], [0.5]),
        continuation_starts=([0.75],),
    )

    assert len(runs) == 3
    assert runs[0].candidate is None
    assert "negative start rejected" in runs[0].failure_reason
    assert runs[1].start_kind is StartKind.DETERMINISTIC
    assert runs[2].start_kind is StartKind.CONTINUATION


def test_clustering_uses_allocations_not_prices_alone() -> None:
    verified = DummyReport(CandidateClassification.VERIFIED_CANDIDATE)
    runs = [
        MultistartRun(0, StartKind.DETERMINISTIC, np.array([0.0]), None, _dummy_candidate(1.0), verified, None),
        MultistartRun(1, StartKind.RANDOM, np.array([0.1]), 1, _dummy_candidate(1.0 + 1e-9), verified, None),
        MultistartRun(2, StartKind.CONTINUATION, np.array([0.2]), None, _dummy_candidate(2.0), verified, None),
    ]

    clusters = cluster_verified_candidates(
        runs,
        lambda candidate: CandidateFeatureBlocks.from_candidate(
            candidate, policy_quantities=[0.5]
        ),
        distance_threshold=1e-6,
    )

    assert len(clusters) == 2
    assert clusters[0].member_run_ids == (0, 1)
    assert clusters[1].member_run_ids == (2,)


def test_clustering_excludes_unverified_solver_points() -> None:
    runs = [
        MultistartRun(
            0,
            StartKind.DETERMINISTIC,
            np.array([0.0]),
            None,
            _dummy_candidate(1.0),
            DummyReport(CandidateClassification.SOLVER_POINT),
            "not verified",
        )
    ]

    clusters = cluster_verified_candidates(
        runs,
        lambda candidate: CandidateFeatureBlocks.from_candidate(
            candidate, policy_quantities=[0.5]
        ),
        distance_threshold=1e-6,
    )

    assert clusters == []
