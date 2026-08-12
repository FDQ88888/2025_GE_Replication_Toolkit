"""Run the strict post-hardening artifact, documentation, and runtime audit."""

import json
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from duanmu_ge_lab.experiment_io import write_json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

EXPECTED_STATUSES = {
    "milestone1_baseline.json": "VERIFIED_CANDIDATE",
    "milestone2_production_baseline.json": "VERIFIED_CANDIDATE",
    "milestone3_split_agent_invariance.json": "SPLIT_AGENT_INVARIANCE_SUCCESS",
    "milestone4_signed_bad_absorption.json": "SIGNED_BAD_ABSORPTION_SUCCESS",
    "milestone5_paper_example_1.json": "PAPER_REPLICATION_SUCCESS",
    "milestone5_paper_example_2.json": "PAPER_REPLICATION_SUCCESS",
    "milestone6_theorem_3_4_mapping.json": "NUMERICAL_MAPPING_CHECK_SUCCESS",
    "milestone7_paper_example_3.json": "PAPER_REPLICATION_SUCCESS",
    "milestone7_paper_example_4.json": "PAPER_REPLICATION_SUCCESS",
    "milestone7_paper_example_5.json": "PAPER_REPLICATION_SUCCESS",
    "milestone7_paper_example_6.json": "PAPER_REPLICATION_SUCCESS",
    "milestone8_example3_multistart.json": "MULTISTART_CLUSTERING_SUCCESS",
    "milestone9_tax_quota_sweeps.json": "SWEEP_SUCCESS",
    "milestone10_welfare_distribution.json": "WELFARE_DISTRIBUTION_SUCCESS",
    "milestone11_finite_weighted_lab.json": "FINITE_WEIGHTED_EXPERIMENT_SUCCESS",
}

EXPECTED_FIGURES = (
    "tax_emission_correspondence.png",
    "quota_price_correspondence.png",
    "quota_ownership_welfare.png",
    "finite_approximation_prices.png",
    "finite_approximation_emissions.png",
    "equilibrium_branch_diagram.png",
)

REQUIRED_DOCUMENTS = (
    "README.md",
    "REPORT.md",
    "FINAL_AUDIT.md",
    "PROFESSOR_DEMO.md",
    "CITATIONS.md",
    "OPEN_QUESTIONS.md",
    "TOLERANCE_AUDIT.md",
    "TESTED_ENVIRONMENTS.md",
    "docs/SCOPE_AND_LIMITATIONS.md",
)

PERSONAL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    re.compile("\u8d39\u4ee3\u5f3a"),
    re.compile("One" + "Drive", re.IGNORECASE),
    re.compile("\u684c\u9762"),
)


def _collect_classifications(value: Any) -> list[str]:
    classifications: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "classification" and isinstance(child, str):
                classifications.append(child)
            classifications.extend(_collect_classifications(child))
    elif isinstance(value, list):
        for child in value:
            classifications.extend(_collect_classifications(child))
    return classifications


def _run_command(arguments: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        arguments,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    recorded_arguments = list(arguments)
    if recorded_arguments and Path(recorded_arguments[0]).is_absolute():
        recorded_arguments[0] = Path(recorded_arguments[0]).name
    return {
        "command": recorded_arguments,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "output_tail": "\n".join(combined.splitlines()[-20:]),
    }


def _audited_source_files() -> Iterable[Path]:
    for directory in (
        "src",
        "tests",
        "scripts",
        "configs",
        "docs",
        "paper_replications",
        ".github",
    ):
        root = ROOT / directory
        if root.exists():
            yield from (
                path
                for path in root.rglob("*")
                if path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix.lower() in {".py", ".md", ".yaml", ".yml", ".toml"}
            )
    yield from ROOT.glob("*.md")
    yield ROOT / "pyproject.toml"
    yield ROOT / ".gitignore"


def _personal_path_findings() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in _audited_source_files():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in PERSONAL_PATH_PATTERNS):
                findings.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "line": line_number,
                        "text": line.strip(),
                    }
                )
    return findings


def _markdown_link_findings() -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for document in ROOT.rglob("*.md"):
        if any(part in {".venv", ".pytest_cache", "hardening"} for part in document.parts):
            continue
        text = document.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target, re.IGNORECASE):
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                missing.append(
                    {
                        "document": str(document.relative_to(ROOT)),
                        "target": raw_target,
                    }
                )
    return missing


def _package_metadata_check() -> dict[str, Any]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    description = project.get("description", "")
    dependencies = project.get("dependencies", [])
    stale_description = "minimal finite exchange-economy" in description.lower()
    required_dependency_names = {"numpy", "scipy", "pyyaml", "matplotlib"}
    declared_names = {
        re.split(r"[<>=!~\[]", dependency, maxsplit=1)[0].lower()
        for dependency in dependencies
    }
    return {
        "passed": bool(
            project.get("requires-python") == ">=3.11,<3.14"
            and not stale_description
            and required_dependency_names <= declared_names
        ),
        "description": description,
        "requires_python": project.get("requires-python"),
        "declared_dependencies": dependencies,
        "missing_required_dependencies": sorted(required_dependency_names - declared_names),
        "stale_description": stale_description,
    }


def _result_checks() -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    all_classifications: list[str] = []
    for filename, expected_status in EXPECTED_STATUSES.items():
        path = RESULTS / filename
        if not path.is_file():
            checks.append(
                {
                    "file": f"results/{filename}",
                    "expected_status": expected_status,
                    "actual_status": None,
                    "passed": False,
                    "reason": "missing result file",
                }
            )
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        classifications = _collect_classifications(data)
        all_classifications.extend(classifications)
        checks.append(
            {
                "file": f"results/{filename}",
                "expected_status": expected_status,
                "actual_status": data.get("status"),
                "passed": bool(
                    data.get("status") == expected_status
                    and "config_snapshot" in data
                    and "reproducibility" in data
                ),
                "config_snapshot_present": "config_snapshot" in data,
                "reproducibility_metadata_present": "reproducibility" in data,
                "classification_counts": dict(Counter(classifications)),
            }
        )
    return checks, all_classifications


def run(*, run_runtime_checks: bool = True) -> dict[str, Any]:
    result_checks, all_classifications = _result_checks()
    suite_path = RESULTS / "reproducibility_suite.json"
    suite_data = (
        json.loads(suite_path.read_text(encoding="utf-8"))
        if suite_path.is_file()
        else {}
    )
    suite_check = {
        "file": "results/reproducibility_suite.json",
        "actual_status": suite_data.get("status"),
        "passed": bool(
            suite_data.get("status") == "REPRODUCIBILITY_SUITE_SUCCESS"
            and suite_data.get("passed") is True
            and not suite_data.get("failures")
        ),
    }
    figure_checks = []
    for filename in EXPECTED_FIGURES:
        path = ROOT / "figures" / filename
        content = path.read_bytes() if path.is_file() else b""
        figure_checks.append(
            {
                "file": f"figures/{filename}",
                "passed": content.startswith(b"\x89PNG\r\n\x1a\n") and len(content) > 10_000,
                "size_bytes": len(content),
            }
        )

    runtime_checks = (
        [
            _run_command([sys.executable, "-m", "pytest", "-q"]),
            _run_command(
                [
                    sys.executable,
                    "-m",
                    "compileall",
                    "-q",
                    "src",
                    "scripts",
                    "paper_replications",
                ]
            ),
        ]
        if run_runtime_checks
        else []
    )
    personal_paths = _personal_path_findings()
    missing_links = _markdown_link_findings()
    package_metadata = _package_metadata_check()
    required_documents = {
        path: (ROOT / path).is_file() for path in REQUIRED_DOCUMENTS
    }
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    stale_test_count_claim = bool(re.search(r"\b\d+\s+passed\b", readme_text))
    unexpected_classifications = sorted(
        classification
        for classification in set(all_classifications)
        if classification != "VERIFIED_CANDIDATE"
    )
    checks = {
        "runtime_checks_passed": bool(
            run_runtime_checks and runtime_checks and all(item["passed"] for item in runtime_checks)
        ),
        "critical_results_passed": all(item["passed"] for item in result_checks),
        "reproducibility_suite_passed": suite_check["passed"],
        "figures_passed": all(item["passed"] for item in figure_checks),
        "no_unexpected_candidate_classifications": not unexpected_classifications,
        "no_personal_absolute_paths_in_source_or_docs": not personal_paths,
        "all_local_markdown_links_exist": not missing_links,
        "all_required_documents_exist": all(required_documents.values()),
        "package_metadata_accurate": package_metadata["passed"],
        "readme_has_no_hard_coded_test_count": not stale_test_count_claim,
    }
    audit_passed = all(checks.values())
    output = {
        "status": "FINAL_AUDIT_PASSED" if audit_passed else "FINAL_AUDIT_FAILED",
        "scope": (
            "Post-hardening runtime, required experiment, artifact, source-path, "
            "documentation-link, and package-metadata audit. This is not a proof "
            "of equilibrium existence, uniqueness, or search completeness."
        ),
        "checks": checks,
        "runtime_checks": runtime_checks,
        "result_checks": result_checks,
        "reproducibility_suite_check": suite_check,
        "figure_checks": figure_checks,
        "aggregate_classification_counts": dict(Counter(all_classifications)),
        "unexpected_classifications": unexpected_classifications,
        "personal_path_findings": personal_paths,
        "missing_markdown_links": missing_links,
        "required_documents": required_documents,
        "package_metadata": package_metadata,
        "readme_stale_test_count_claim": stale_test_count_claim,
        "config_snapshot": {
            "required_result_statuses": EXPECTED_STATUSES,
            "required_figures": EXPECTED_FIGURES,
            "required_documents": REQUIRED_DOCUMENTS,
            "runtime_checks_enabled": run_runtime_checks,
        },
    }
    write_json(RESULTS / "final_audit.json", output)
    return output


def main() -> int:
    output = run(run_runtime_checks=True)
    print(output["status"])
    if output["status"] != "FINAL_AUDIT_PASSED":
        for check, passed in output["checks"].items():
            if not passed:
                print(f"FAILED CHECK: {check}")
    return 0 if output["status"] == "FINAL_AUDIT_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
