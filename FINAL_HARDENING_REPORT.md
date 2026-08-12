# Final Research-Grade Hardening Report

## 1. Executive Summary

This pass hardens the existing `duanmu_ge_lab` without adding economic models. It fixes two critical issues that could distort the research semantics: floating-point misclassification of theoretical zero profit in `LinearRayTechnology`, and false success for failed experiments in the reproducibility suite. Statuses, tolerances, candidate-quantity accounting, price scales, paper parameters, dependencies, documentation, CI, and the delivery archive were also audited systematically.

Final evidence: both CPython 3.12.13 and 3.13.0 report `113 passed, 0 failed`; all 16 required suite observations exactly match their expected statuses; Examples 1-6 are 6/6 `PAPER_REPLICATION_SUCCESS`; and the strict final audit returns `FINAL_AUDIT_PASSED` in both environments.

## 2. Original Issues Found

- A tiny positive rounding error in `p dot v` could misclassify a theoretical zero-profit ray as having unbounded profit.
- The suite could previously finish calls and print statuses without enforcing equality between actual and expected status.
- Sweep success did not validate the number of discovered clusters, and the single-experiment CLI could return zero for a failure status.
- Figure generation did not first reject failed upstream results.
- Environment claims lacked cross-minor execution, upper bounds, and tested pins; CI, scope, and machine-independent delivery documentation were incomplete.
- Historical result metadata recorded machine-specific absolute paths for the interpreter and two configuration files.

## 3. LinearRayTechnology Floating-Point Bug

The root cause was an exact `margin > 0` branch on `margin = p dot v`. The fix uses the L2 scale

```text
scale = ||p||_2 ||v||_2
tol = profit_margin_abs_tol + profit_margin_rel_tol * scale
```

and explicitly classifies the margin as shutdown, numerical zero, or positive-unbounded. The default is `1e-14 + 1e-12*scale`, exposed through the unified tolerance infrastructure. At zero margin, every feasible ray activity is validated as a nonunique profit-maximizing solution rather than compared with an arbitrary returned plan.

Regression tests cover exact zero, `+/-5e-17`, clearly signed `+/-1e-3`, scale changes, and nonunique activity levels. After rerunning Examples 1-6 and the mappings, the maximum change in shared paper-numerical fields relative to the pre-fix snapshot is zero. See `HARDENING_FIX_01_LINEAR_RAY.md` for margins and classifications.

## 4. Reproducibility Suite False-Success Bug

Statuses are now mapped by a central registry to SUCCESS/FAILURE/BLOCKED/PARTIAL/SKIPPED/UNKNOWN. Every YAML runner declares `expected_status` and `required` explicitly. The suite stores expected/actual/outcome; any required mismatch, blocked or unknown status, or exception produces `REPRODUCIBILITY_SUITE_FAILED` and a nonzero exit code. An optional skip can only become an explicit warning.

A sweep returns `SWEEP_SUCCESS` only when the actual branch count equals the configured target. The single-experiment CLI returns zero only for registered success statuses, and figures accept only three precisely successful upstream results. Tests cover full success, required failure, required blocked, an optional-skipped warning, failure exit codes, unknown single-experiment status, and failed figure sources. See `HARDENING_FIX_02_STATUS_SEMANTICS.md`.

## 5. Cross-Version Testing

CPython 3.12.13 and 3.13.0 were actually verified on Windows; both completed 113 tests, compileall, and the full suite, while 3.13 also ran the key CI smoke commands. An Ubuntu CPython 3.11/3.12/3.13 GitHub Actions matrix is configured but has not run remotely, so it is not labeled verified. See `TESTED_ENVIRONMENTS.md` for the exact matrix.

## 6. Dependency Strategy

`pyproject.toml` uses `>=3.11,<3.14` and sets currently audited major-version upper bounds for NumPy, SciPy, PyYAML, Matplotlib, and pytest. `requirements-tested.txt` records an actual CPython 3.12 reference environment and does not claim to be a cross-platform lockfile. No unused pandas dependency or new toolchain was introduced.

## 7. Documentation Fixes

The README provides PowerShell, POSIX, and no-activation commands, removes personal paths, and states the non-general scope immediately. CITATIONS clarifies that locally consulted paper PDFs are excluded from the clean package. Documentation was added for scope, parameter sources, research wording, environments, and collaborators; the professor demo is a concise finite-model research presentation without marketing claims.

## 8. Tolerance Audit

`TOLERANCE_AUDIT.md` records values, scales, and uses for market clearing, budgets, consumer and firm optimality, zero profit, normalization, clustering, paper comparison, and policy accounting. Paper results were not repaired by rounding, clipping, or indiscriminately loosening tolerances; solver acceptance remains separate from tolerances for rounded paper tables.

## 9. Candidate-vs-Reoptimized Audit

Resource accounting, market clearing, policy compliance, tax/quota revenue, income, and Walras accounting all use the candidate's own allocations and plans. Reoptimized quantities are used only for utility and profit optimality gaps. A new policy-level regression test supplies an internally consistent but economically incorrect cache and confirms that diagnostics still identify violations from candidate quantities.

## 10. Paper Replication Revalidation

Examples 1-6 were all rerun and return `PAPER_REPLICATION_SUCCESS`; the Theorems 3-4 mappings return `NUMERICAL_MAPPING_CHECK_SUCCESS`. Paper parameters are traceable to article or Supplement pages, mathematical ledgers, and YAML files. Search intervals, starting points, scan points, and tolerances are explicitly labeled computational choices. See `PAPER_PARAMETER_AUDIT.md`.

## 11. Current Test Result

Final result: `113 passed, 0 failed`, an increase of 13 over the 100 pre-hardening tests. New coverage includes LinearRay margins, nonunique optima, the status contract, sweep validation, candidate policy accounting, price scales, CLI exit codes, and upstream gates for figures.

## 12. Reproducibility Suite Result

Both CPython 3.12 and 3.13 return `REPRODUCIBILITY_SUITE_SUCCESS`. The final manifest contains 16 required observations, zero failures, and zero warnings, with exact equality between every expected and actual status.

## 13. Final Audit Result

Windows CPython 3.12.13 and 3.13.0 both actually return `FINAL_AUDIT_PASSED`. The audit reruns pytest and compileall and requires critical results, the suite, figures, documentation, paths, metadata, and classifications to satisfy mandatory conditions; failure returns a nonzero exit code.

## 14. Known Remaining Limitations

- Nonlinear multistart and continuation do not certify root completeness; discovered clusters are not necessarily all equilibria.
- Nonexistence in Example 4 comes from the paper's theory, not solver failure.
- Paper-specific builders are not arbitrary YAML model compilers.
- General incomplete preferences, comprehensive externalities, and infinite-dimensional or measure-economy solution are unsupported.
- The finite weighted experiment is construction-specific and does not prove continuum convergence, uniform integrability, or results from nonstandard analysis.
- CI has not run remotely; Python 3.11 is configured but unverified.

## 15. Safe Claims to Professor Duanmu

It is accurate to describe the project as a finite-model paper-replication, equilibrium-search, and independent numerical-diagnostics framework built around the Anderson-Duanmu quota and emission-tax examples. Under the current configurations and tolerances, Examples 1-6 successfully match their specified targets; multibranch results are stable numerical discoveries of diagnosed candidates; and results reproduce in two local Python minor-version environments.

After excluding permitted bad-disposal slack and ratios used only for scale assessment from standard diagnostic error/residual fields, the largest critical error is `2.148654587585952e-10`, the `max_compliance_violation` of one verified candidate in the tax sweep.

## 16. Claims That Must Not Be Made

The following claims must not be made: numerical computation proves general existence or uniqueness; failure to find a root proves nonexistence; discovering three clusters proves there are exactly three equilibria; finite-grid stability proves a continuum limit; the project implements measure-theoretic or nonstandard analysis; the project is a universal GE solver; or unexecuted CI/Python 3.11 has been verified.
