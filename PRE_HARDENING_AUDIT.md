# Pre-Hardening Audit

## Purpose

This file records the project state immediately before the final research-grade hardening pass on 2026-08-10. The commands were executed in the existing project virtual environment; the values below are not copied from an earlier report.

## Environment

| Component | Observed version |
|---|---:|
| Operating system | Windows |
| Python | 3.12.13 |
| NumPy | 2.5.2 |
| SciPy | 1.18.0 |
| pytest | 9.1.1 |
| Matplotlib | 3.11.1 |
| PyYAML | 6.0.3 |

The project directory was **not** a Git work tree, so no Git status or commit hash was available. The pre-hardening source archive was retained unchanged, and its hash is stored in `hardening/pre_hardening/pre_hardening_archive_hash.txt`.

## Executed Baseline

```text
python -m pytest -q
100 passed in 4.62s
exit code: 0

python scripts/run_final_audit.py
FINAL_AUDIT_PASSED
exit code: 0

python scripts/run_reproducibility_suite.py
REPRODUCIBILITY_SUITE_SUCCESS
exit code: 0

python scripts/run_final_audit.py  # after suite regeneration
FINAL_AUDIT_PASSED
exit code: 0
```

## Failures

- Failed tests: none.
- Failed test count: 0.
- Traceback summaries: none were emitted.

The absence of a currently failing test does not resolve the two independently identified latent defects. In particular, the pre-hardening reproducibility suite printed success without checking every experiment against an expected-success contract, and `LinearRayTechnology` used a strict `margin > 0.0` comparison that could misclassify a theoretical zero-profit ray under floating-point perturbation.

## Preserved Evidence

- `hardening/pre_hardening/pytest.log`
- `hardening/pre_hardening/reproducibility_suite.log`
- `hardening/pre_hardening/final_audit_before_suite.log`
- `hardening/pre_hardening/final_audit_after_suite.log`
- `hardening/pre_hardening/results_snapshot/`
- `hardening/pre_hardening/figure_manifest.json`
- `duanmu_ge_lab_source.zip` (the pre-hardening clean source archive)
