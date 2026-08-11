import importlib
import json
from pathlib import Path

from duanmu_ge_lab.experiment_io import load_yaml_mapping
from scripts.run_final_audit import EXPECTED_STATUSES, ROOT
from scripts.run_reproducibility_suite import (
    CONFIGS,
    ExperimentObservation,
    ExperimentRequirement,
    evaluate_suite,
    suite_exit_code,
)


def test_every_yaml_config_declares_an_importable_runner() -> None:
    for relative_path in CONFIGS:
        config = load_yaml_mapping(ROOT / relative_path)
        runner = config["runner"]
        module = importlib.import_module(runner["module"])
        assert callable(getattr(module, runner["callable"]))
        assert isinstance(runner["expected_status"], str)
        assert isinstance(runner["required"], bool)


def _observation(
    *, expected: str, actual: str, required: bool = True
) -> ExperimentObservation:
    return ExperimentObservation(
        ExperimentRequirement("test", expected, required, "results/test.json"),
        actual,
    )


def test_suite_passes_when_all_required_statuses_match() -> None:
    summary = evaluate_suite(
        (_observation(expected="PAPER_REPLICATION_SUCCESS", actual="PAPER_REPLICATION_SUCCESS"),)
    )

    assert summary.passed
    assert suite_exit_code(summary) == 0


def test_suite_fails_on_required_failure() -> None:
    summary = evaluate_suite(
        (_observation(expected="PAPER_REPLICATION_SUCCESS", actual="PAPER_REPLICATION_FAILURE"),)
    )

    assert not summary.passed
    assert len(summary.failures) == 1
    assert suite_exit_code(summary) != 0


def test_suite_fails_on_required_blocked_experiment() -> None:
    summary = evaluate_suite(
        (_observation(expected="PAPER_REPLICATION_SUCCESS", actual="BLOCKED"),)
    )

    assert not summary.passed
    assert summary.failures[0]["actual_outcome"] == "BLOCKED"


def test_suite_allows_optional_skipped_experiment_with_warning() -> None:
    summary = evaluate_suite(
        (
            _observation(
                expected="PAPER_REPLICATION_SUCCESS",
                actual="SKIPPED",
                required=False,
            ),
        )
    )

    assert summary.passed
    assert not summary.failures
    assert len(summary.warnings) == 1


def test_all_persisted_results_have_reproducibility_metadata() -> None:
    for filename in EXPECTED_STATUSES:
        data = json.loads((ROOT / "results" / filename).read_text(encoding="utf-8"))
        metadata = data["reproducibility"]
        assert data["config_snapshot"]
        assert metadata["generated_at_utc"]
        assert metadata["python"]["version"]
        assert metadata["dependency_versions"]["numpy"]
        assert "git_commit" in metadata
        assert metadata["candidate_and_run_status_counts"]


def test_final_audit_result_contract_names_every_critical_result() -> None:
    assert len(EXPECTED_STATUSES) == 15
    assert EXPECTED_STATUSES["milestone5_paper_example_1.json"] == (
        "PAPER_REPLICATION_SUCCESS"
    )
    assert EXPECTED_STATUSES["milestone7_paper_example_6.json"] == (
        "PAPER_REPLICATION_SUCCESS"
    )
    assert Path(ROOT / "scripts" / "run_final_audit.py").is_file()
