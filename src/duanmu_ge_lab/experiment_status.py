"""Exact run-status semantics shared by experiment orchestration and audits."""

from enum import Enum


class ExperimentOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    BLOCKED = "BLOCKED"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    UNKNOWN = "UNKNOWN"


_STATUS_OUTCOMES = {
    "VERIFIED_CANDIDATE": ExperimentOutcome.SUCCESS,
    "SPLIT_AGENT_INVARIANCE_SUCCESS": ExperimentOutcome.SUCCESS,
    "SIGNED_BAD_ABSORPTION_SUCCESS": ExperimentOutcome.SUCCESS,
    "PAPER_REPLICATION_SUCCESS": ExperimentOutcome.SUCCESS,
    "NUMERICAL_MAPPING_CHECK_SUCCESS": ExperimentOutcome.SUCCESS,
    "MULTISTART_CLUSTERING_SUCCESS": ExperimentOutcome.SUCCESS,
    "SWEEP_SUCCESS": ExperimentOutcome.SUCCESS,
    "WELFARE_DISTRIBUTION_SUCCESS": ExperimentOutcome.SUCCESS,
    "FINITE_WEIGHTED_EXPERIMENT_SUCCESS": ExperimentOutcome.SUCCESS,
    "FIGURE_GENERATION_SUCCESS": ExperimentOutcome.SUCCESS,
    "REPRODUCIBILITY_SUITE_SUCCESS": ExperimentOutcome.SUCCESS,
    "FINAL_AUDIT_PASSED": ExperimentOutcome.SUCCESS,
    "SPLIT_AGENT_INVARIANCE_FAILURE": ExperimentOutcome.FAILURE,
    "SIGNED_BAD_ABSORPTION_FAILURE": ExperimentOutcome.FAILURE,
    "PAPER_REPLICATION_FAILURE": ExperimentOutcome.FAILURE,
    "NUMERICAL_MAPPING_CHECK_FAILURE": ExperimentOutcome.FAILURE,
    "MULTISTART_CLUSTERING_FAILURE": ExperimentOutcome.FAILURE,
    "SWEEP_FAILURE": ExperimentOutcome.FAILURE,
    "WELFARE_DISTRIBUTION_FAILURE": ExperimentOutcome.FAILURE,
    "FINITE_WEIGHTED_EXPERIMENT_FAILURE": ExperimentOutcome.FAILURE,
    "FIGURE_GENERATION_FAILURE": ExperimentOutcome.FAILURE,
    "PROCESS_FAILURE": ExperimentOutcome.FAILURE,
    "EXPERIMENT_EXCEPTION": ExperimentOutcome.FAILURE,
    "REPRODUCIBILITY_SUITE_FAILED": ExperimentOutcome.FAILURE,
    "FINAL_AUDIT_FAILED": ExperimentOutcome.FAILURE,
    "BLOCKED": ExperimentOutcome.BLOCKED,
    "BLOCKED_BY_PRIMARY_SOURCE": ExperimentOutcome.BLOCKED,
    "PARTIAL": ExperimentOutcome.PARTIAL,
    "REPLICATION_PARTIAL": ExperimentOutcome.PARTIAL,
    "SKIPPED": ExperimentOutcome.SKIPPED,
}


def experiment_outcome(status: str | None) -> ExperimentOutcome:
    """Return the registered coarse outcome; unknown strings never pass."""

    if not isinstance(status, str):
        return ExperimentOutcome.UNKNOWN
    return _STATUS_OUTCOMES.get(status, ExperimentOutcome.UNKNOWN)


def is_registered_success(status: str | None) -> bool:
    """Return true only for an explicitly registered success status."""

    return experiment_outcome(status) is ExperimentOutcome.SUCCESS
