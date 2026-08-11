"""Generic multistart orchestration and verified-candidate clustering."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Sequence

import numpy as np

from duanmu_ge_lab.equilibrium.candidate import CandidateClassification
from duanmu_ge_lab.equilibrium.normalization import normalize_signed_l1


class StartKind(str, Enum):
    """Auditable origin of one numerical initial point."""

    DETERMINISTIC = "deterministic_theoretical"
    RANDOM = "random"
    CONTINUATION = "continuation"


@dataclass(slots=True)
class MultistartRun:
    """One retained solver attempt, successful or not."""

    run_id: int
    start_kind: StartKind
    initial_point: np.ndarray
    random_seed: int | None
    candidate: Any | None
    diagnostics: Any | None
    failure_reason: str | None

    @property
    def classification(self) -> str:
        if self.diagnostics is None:
            return CandidateClassification.FAILED_RUN.value
        value = self.diagnostics.classification
        return value.value if hasattr(value, "value") else str(value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "start_kind": self.start_kind.value,
            "initial_point": self.initial_point.tolist(),
            "random_seed": self.random_seed,
            "solver_method": (
                self.candidate.solver_method if self.candidate is not None else None
            ),
            "solver_convergence": (
                bool(self.candidate.solver_success)
                if self.candidate is not None
                else False
            ),
            "classification": self.classification,
            "failure_reason": self.failure_reason,
            "candidate": (
                self.candidate.to_dict() if self.candidate is not None else None
            ),
            "diagnostics": (
                self.diagnostics.to_dict() if self.diagnostics is not None else None
            ),
        }


def solve_multistart(
    solve_from_start: Callable[[np.ndarray], Any],
    diagnose: Callable[[Any], Any],
    *,
    deterministic_starts: Sequence[Sequence[float]] = (),
    random_bounds: tuple[Sequence[float], Sequence[float]] | None = None,
    random_count: int = 0,
    continuation_starts: Sequence[Sequence[float]] = (),
    random_seed: int = 0,
) -> list[MultistartRun]:
    """Run deterministic, seeded random, and continuation initial points."""

    if random_count < 0:
        raise ValueError("random_count must be nonnegative.")
    starts: list[tuple[StartKind, np.ndarray, int | None]] = []
    for values in deterministic_starts:
        starts.append((StartKind.DETERMINISTIC, _validated_start(values), None))
    if random_count:
        if random_bounds is None:
            raise ValueError("Random starts require lower and upper bounds.")
        lower = _validated_start(random_bounds[0])
        upper = _validated_start(random_bounds[1])
        if lower.shape != upper.shape or np.any(lower >= upper):
            raise ValueError("Random bounds must have matching shape and lower<upper.")
        rng = np.random.default_rng(random_seed)
        for _ in range(random_count):
            starts.append(
                (
                    StartKind.RANDOM,
                    rng.uniform(lower, upper),
                    random_seed,
                )
            )
    for values in continuation_starts:
        starts.append((StartKind.CONTINUATION, _validated_start(values), None))

    runs: list[MultistartRun] = []
    for run_id, (kind, initial, seed) in enumerate(starts):
        candidate = None
        diagnostics = None
        failure_reason = None
        try:
            candidate = solve_from_start(initial.copy())
            diagnostics = diagnose(candidate)
            if not candidate.solver_success:
                failure_reason = candidate.solver_message
            elif diagnostics.classification is not CandidateClassification.VERIFIED_CANDIDATE:
                failure_reason = (
                    "Candidate did not pass independent diagnostics: "
                    f"{diagnostics.classification.value}."
                )
        except Exception as exc:  # retained as a failed run by design
            failure_reason = f"{type(exc).__name__}: {exc}"
        runs.append(
            MultistartRun(
                run_id=run_id,
                start_kind=kind,
                initial_point=initial,
                random_seed=seed,
                candidate=candidate,
                diagnostics=diagnostics,
                failure_reason=failure_reason,
            )
        )
    return runs


@dataclass(frozen=True, slots=True)
class CandidateFeatureBlocks:
    """Economic blocks used jointly in equilibrium-candidate distance."""

    signed_l1_prices: np.ndarray
    allocations: np.ndarray
    firm_plans: np.ndarray
    policy_quantities: np.ndarray

    def __post_init__(self) -> None:
        for name in (
            "signed_l1_prices",
            "allocations",
            "firm_plans",
            "policy_quantities",
        ):
            array = np.asarray(getattr(self, name), dtype=float).reshape(-1)
            if not np.all(np.isfinite(array)):
                raise ValueError("Candidate clustering features must be finite.")
            object.__setattr__(self, name, array.copy())

    @classmethod
    def from_candidate(
        cls, candidate: Any, policy_quantities: Sequence[float]
    ) -> "CandidateFeatureBlocks":
        """Normalize prices and retain all physical/policy candidate coordinates."""

        return cls(
            signed_l1_prices=normalize_signed_l1(candidate.prices),
            allocations=np.asarray(candidate.allocations, dtype=float),
            firm_plans=np.asarray(candidate.firm_plans, dtype=float),
            policy_quantities=np.asarray(policy_quantities, dtype=float),
        )


def candidate_block_distance(
    left: CandidateFeatureBlocks, right: CandidateFeatureBlocks
) -> float:
    """Return root-mean-square relative block distance."""

    distances = []
    for name in (
        "signed_l1_prices",
        "allocations",
        "firm_plans",
        "policy_quantities",
    ):
        a = getattr(left, name)
        b = getattr(right, name)
        if a.shape != b.shape:
            return float("inf")
        scale = max(1.0, float(np.linalg.norm(a)), float(np.linalg.norm(b)))
        distances.append(float(np.linalg.norm(a - b)) / scale)
    return float(np.sqrt(np.mean(np.square(distances))))


@dataclass(frozen=True, slots=True)
class VerifiedCandidateCluster:
    """One discovered cluster of independently verified candidates."""

    cluster_id: int
    representative_run_id: int
    member_run_ids: tuple[int, ...]
    max_distance_to_representative: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "representative_run_id": self.representative_run_id,
            "member_run_ids": list(self.member_run_ids),
            "max_distance_to_representative": self.max_distance_to_representative,
        }


def cluster_verified_candidates(
    runs: Sequence[MultistartRun],
    feature_extractor: Callable[[Any], CandidateFeatureBlocks],
    *,
    distance_threshold: float,
) -> list[VerifiedCandidateCluster]:
    """Greedily cluster only candidates classified `VERIFIED_CANDIDATE`."""

    if not np.isfinite(distance_threshold) or distance_threshold <= 0.0:
        raise ValueError("Cluster distance threshold must be finite and positive.")
    verified = [
        run
        for run in runs
        if run.candidate is not None
        and run.classification == CandidateClassification.VERIFIED_CANDIDATE.value
    ]
    working: list[dict[str, Any]] = []
    for run in verified:
        features = feature_extractor(run.candidate)
        assigned = False
        for cluster in working:
            distance = candidate_block_distance(features, cluster["features"])
            if distance <= distance_threshold:
                cluster["members"].append(run.run_id)
                cluster["max_distance"] = max(cluster["max_distance"], distance)
                assigned = True
                break
        if not assigned:
            working.append(
                {
                    "representative": run.run_id,
                    "features": features,
                    "members": [run.run_id],
                    "max_distance": 0.0,
                }
            )
    return [
        VerifiedCandidateCluster(
            cluster_id=index,
            representative_run_id=cluster["representative"],
            member_run_ids=tuple(cluster["members"]),
            max_distance_to_representative=float(cluster["max_distance"]),
        )
        for index, cluster in enumerate(working)
    ]


def _validated_start(values: Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("Every multistart point must be a non-empty finite vector.")
    return array.copy()
