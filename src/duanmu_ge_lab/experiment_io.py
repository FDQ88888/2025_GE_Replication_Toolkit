"""Stable configuration, numerical comparison, and JSON output helpers."""

import json
import platform
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import yaml


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config {path} must contain a YAML mapping at its root.")
    return data


def compare_numeric(
    expected: Any,
    computed: Any,
    *,
    absolute_tolerance: float,
    relative_tolerance: float,
) -> dict[str, Any]:
    if isinstance(expected, Mapping):
        if not isinstance(computed, Mapping) or set(expected) != set(computed):
            return {
                "passed": False,
                "structure_error": "Mapping keys differ.",
                "expected_keys": sorted(expected),
                "computed_keys": sorted(computed) if isinstance(computed, Mapping) else None,
            }
        children = {
            str(key): compare_numeric(
                expected[key],
                computed[key],
                absolute_tolerance=absolute_tolerance,
                relative_tolerance=relative_tolerance,
            )
            for key in expected
        }
        return {
            "passed": all(child["passed"] for child in children.values()),
            "children": children,
        }
    expected_array = np.asarray(expected, dtype=float)
    computed_array = np.asarray(computed, dtype=float)
    if expected_array.shape != computed_array.shape:
        return {
            "passed": False,
            "structure_error": "Array shapes differ.",
            "expected_shape": list(expected_array.shape),
            "computed_shape": list(computed_array.shape),
        }
    absolute = np.abs(computed_array - expected_array)
    allowed = absolute_tolerance + relative_tolerance * np.abs(expected_array)
    nonzero = expected_array != 0.0
    relative_object = np.empty(expected_array.shape, dtype=object)
    relative_object[nonzero] = (
        absolute[nonzero] / np.abs(expected_array[nonzero])
    ).tolist()
    relative_object[~nonzero] = None
    max_relative = (
        float(np.max(absolute[nonzero] / np.abs(expected_array[nonzero])))
        if np.any(nonzero)
        else None
    )
    return {
        "passed": bool(np.all(absolute <= allowed)),
        "paper_analytical": expected_array.tolist(),
        "computed": computed_array.tolist(),
        "absolute_difference": absolute.tolist(),
        "relative_difference_where_paper_value_nonzero": relative_object.tolist(),
        "max_absolute_difference": float(np.max(absolute, initial=0.0)),
        "max_relative_difference_where_paper_value_nonzero": max_relative,
        "absolute_tolerance": absolute_tolerance,
        "relative_tolerance": relative_tolerance,
    }


def _matching_values(value: Any, path: str, terms: tuple[str, ...]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if any(term in str(key).lower() for term in terms):
                matches.append({"path": child_path, "value": child})
            matches.extend(_matching_values(child, child_path, terms))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            matches.extend(_matching_values(child, f"{path}[{index}]", terms))
    return matches


def _git_commit(project_root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None
    commit = completed.stdout.strip()
    return commit if completed.returncode == 0 and commit else None


def build_reproducibility_metadata(path: Path, data: Mapping[str, Any]) -> dict[str, Any]:
    project_root = path.resolve().parent.parent
    git_commit = _git_commit(project_root)
    status_entries = _matching_values(data, "", ("status", "classification"))
    status_counts = Counter(
        str(entry["value"])
        for entry in status_entries
        if isinstance(entry["value"], (str, bool, int, float))
    )
    dependency_versions: dict[str, str | None] = {}
    for distribution in ("numpy", "scipy", "PyYAML", "pytest", "matplotlib"):
        try:
            dependency_versions[distribution] = metadata.version(distribution)
        except metadata.PackageNotFoundError:
            dependency_versions[distribution] = None
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable_name": Path(sys.executable).name,
            "platform": platform.platform(),
        },
        "dependency_versions": dependency_versions,
        "git_commit": git_commit,
        "git_note": (
            None
            if git_commit is not None
            else "Project directory is not inside a Git work tree; commit hash unavailable."
        ),
        "config_snapshot_present": "config_snapshot" in data,
        "random_seed_entries": _matching_values(data, "", ("seed",)),
        "numerical_setting_entries": _matching_values(
            data,
            "",
            ("tolerance", "solver", "start", "bracket", "scan", "iteration"),
        ),
        "candidate_and_run_status_counts": dict(sorted(status_counts.items())),
        "failure_retention_note": (
            "Run-level and candidate-level statuses are counted without dropping "
            "failed or nonexistence classifications."
        ),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    data.setdefault("reproducibility", build_reproducibility_metadata(path, data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
