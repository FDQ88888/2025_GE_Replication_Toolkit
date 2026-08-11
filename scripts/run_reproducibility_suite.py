"""Rebuild required experiments and enforce their exact status contracts."""

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from duanmu_ge_lab.experiment_io import load_yaml_mapping, write_json
from duanmu_ge_lab.experiment_status import ExperimentOutcome, experiment_outcome
from scripts.generate_figures import run as generate_figures
from scripts.run_baseline import main as run_baseline
from scripts.run_experiment import run_config
from scripts.run_production_baseline import main as run_production_baseline
from scripts.run_signed_bad_baseline import main as run_signed_bad_baseline
from scripts.run_weighted_invariance import main as run_weighted_invariance


@dataclass(frozen=True, slots=True)
class ExperimentRequirement:
    name: str
    expected_status: str
    required: bool
    result_path: str


@dataclass(frozen=True, slots=True)
class ExperimentObservation:
    requirement: ExperimentRequirement
    actual_status: str | None
    detail: str = ""


@dataclass(frozen=True, slots=True)
class SuiteSummary:
    passed: bool
    failures: tuple[dict[str, object], ...]
    warnings: tuple[dict[str, object], ...]
    observations: tuple[dict[str, object], ...]


BASELINE_SPECS: tuple[tuple[ExperimentRequirement, Callable[[], int]], ...] = (
    (
        ExperimentRequirement(
            "analytical exchange baseline",
            "VERIFIED_CANDIDATE",
            True,
            "results/milestone1_baseline.json",
        ),
        run_baseline,
    ),
    (
        ExperimentRequirement(
            "analytical production baseline",
            "VERIFIED_CANDIDATE",
            True,
            "results/milestone2_production_baseline.json",
        ),
        run_production_baseline,
    ),
    (
        ExperimentRequirement(
            "split-agent invariance baseline",
            "SPLIT_AGENT_INVARIANCE_SUCCESS",
            True,
            "results/milestone3_split_agent_invariance.json",
        ),
        run_weighted_invariance,
    ),
    (
        ExperimentRequirement(
            "signed-price bad-absorption baseline",
            "SIGNED_BAD_ABSORPTION_SUCCESS",
            True,
            "results/milestone4_signed_bad_absorption.json",
        ),
        run_signed_bad_baseline,
    ),
)

CONFIGS = (
    "configs/paper/example_1.yaml",
    "configs/paper/example_2.yaml",
    "configs/paper/theorem_3_4_mapping.yaml",
    "configs/paper/example_3.yaml",
    "configs/paper/example_4.yaml",
    "configs/paper/example_5.yaml",
    "configs/paper/example_6.yaml",
    "configs/experiments/example3_multistart.yaml",
    "configs/experiments/tax_quota_sweeps.yaml",
    "configs/experiments/quota_ownership_welfare.yaml",
    "configs/experiments/finite_weighted_bad_absorption.yaml",
)


def evaluate_suite(
    observations: tuple[ExperimentObservation, ...],
) -> SuiteSummary:
    """Evaluate exact expected statuses with explicit optional-skip semantics."""

    failures: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    for observation in observations:
        requirement = observation.requirement
        outcome = experiment_outcome(observation.actual_status)
        exact_match = observation.actual_status == requirement.expected_status
        record = {
            **asdict(requirement),
            "actual_status": observation.actual_status,
            "actual_outcome": outcome.value,
            "exact_match": exact_match,
            "detail": observation.detail,
        }
        records.append(record)
        if exact_match and outcome is ExperimentOutcome.SUCCESS:
            continue
        optional_unavailable = not requirement.required and outcome in {
            ExperimentOutcome.SKIPPED,
            ExperimentOutcome.BLOCKED,
        }
        if optional_unavailable:
            warnings.append(record)
        else:
            failures.append(record)
    return SuiteSummary(
        passed=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
        observations=tuple(records),
    )


def _read_status(relative_path: str) -> str | None:
    path = ROOT / relative_path
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("status")


def _config_requirement(relative_path: str) -> ExperimentRequirement:
    config = load_yaml_mapping(ROOT / relative_path)
    runner = config.get("runner")
    if not isinstance(runner, Mapping):
        raise ValueError(f"{relative_path} has no runner status contract.")
    expected = runner.get("expected_status")
    required = runner.get("required")
    if not isinstance(expected, str) or not isinstance(required, bool):
        raise ValueError(
            f"{relative_path} must declare runner.expected_status and runner.required."
        )
    return ExperimentRequirement(
        name=relative_path,
        expected_status=expected,
        required=required,
        result_path="results/ (runner-specific JSON)",
    )


def run_suite() -> SuiteSummary:
    observations: list[ExperimentObservation] = []
    for requirement, runner in BASELINE_SPECS:
        try:
            exit_code = runner()
            actual = (
                _read_status(requirement.result_path)
                if exit_code == 0
                else "PROCESS_FAILURE"
            )
            detail = f"process exit code {exit_code}"
        except Exception as exc:  # Preserve the remaining experiment audit.
            actual = "EXPERIMENT_EXCEPTION"
            detail = f"{type(exc).__name__}: {exc}"
        observations.append(ExperimentObservation(requirement, actual, detail))

    for relative_path in CONFIGS:
        requirement = _config_requirement(relative_path)
        try:
            result = run_config(ROOT / relative_path)
            actual = result.get("status")
            detail = "runner returned a result mapping"
        except Exception as exc:  # Preserve all failures in one suite summary.
            actual = "EXPERIMENT_EXCEPTION"
            detail = f"{type(exc).__name__}: {exc}"
        observations.append(ExperimentObservation(requirement, actual, detail))

    figure_requirement = ExperimentRequirement(
        "research figure generation",
        "FIGURE_GENERATION_SUCCESS",
        True,
        "figures/figure_manifest.json",
    )
    try:
        figure_result = generate_figures()
        figure_status = figure_result.get("status")
        figure_detail = "figure runner returned a result mapping"
    except Exception as exc:
        figure_status = "EXPERIMENT_EXCEPTION"
        figure_detail = f"{type(exc).__name__}: {exc}"
    observations.append(
        ExperimentObservation(figure_requirement, figure_status, figure_detail)
    )
    return evaluate_suite(tuple(observations))


def suite_exit_code(summary: SuiteSummary) -> int:
    """Map the contract result to the command-line process exit code."""

    return 0 if summary.passed else 1


def main() -> int:
    summary = run_suite()
    status = (
        "REPRODUCIBILITY_SUITE_SUCCESS"
        if summary.passed
        else "REPRODUCIBILITY_SUITE_FAILED"
    )
    output = {
        "status": status,
        "config_snapshot": {
            "baseline_requirements": [asdict(spec) for spec, _ in BASELINE_SPECS],
            "config_paths": list(CONFIGS),
        },
        "passed": summary.passed,
        "failures": list(summary.failures),
        "warnings": list(summary.warnings),
        "observations": list(summary.observations),
    }
    write_json(ROOT / "results" / "reproducibility_suite.json", output)
    for failure in summary.failures:
        print(
            "FAILED:",
            failure["name"],
            f"expected={failure['expected_status']}",
            f"actual={failure['actual_status']}",
            f"result={failure['result_path']}",
        )
    for warning in summary.warnings:
        print(
            "WARNING:",
            warning["name"],
            f"actual={warning['actual_status']}",
        )
    print(status)
    return suite_exit_code(summary)


if __name__ == "__main__":
    raise SystemExit(main())
