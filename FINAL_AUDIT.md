# FINAL AUDIT AFTER HARDENING

## Current Gate Status

**`FINAL_AUDIT_PASSED`.** The hardened code completed `113 passed, 0 failed`, compileall, the full reproducibility suite, and the strict final audit on Windows CPython 3.12.13 and 3.13.0 independently. Examples 1-6 all succeed, and 16 required suite observations match exactly.

## Environment Tiers

- Original development environment: pre-hardening CPython 3.12.13, 100 tests, with the old audit and suite passing; evidence is preserved in `hardening/pre_hardening/`.
- Current verified environments: Windows CPython 3.12.13 and 3.13.0; see `TESTED_ENVIRONMENTS.md` for exact dependencies and execution scope.
- CI environments: an Ubuntu CPython 3.11, 3.12, and 3.13 matrix is configured. Its current status is **CI CONFIGURED**, not CI verified.

## Mandatory Checks Added by Hardening

The final audit now executes pytest and compileall and requires exact success for the baseline, all critical paper results, the suite manifest, and six research figures. It also checks configuration and reproducibility metadata, anomalous candidate classifications, personal absolute paths, local Markdown links, required documentation, package metadata, and stale hard-coded test counts in the README. Any required failure returns a nonzero exit code.

---

# Historical Final Audit Before Hardening

The following section preserves the previous audit history in full. Its `100 passed` describes only the pre-hardening state and is not the current README claim.

## Audit Conclusion

**FINAL_AUDIT_PASSED.** The automated artifact audit covers 15 milestone result files and six research figures, reading 130 `VERIFIED_CANDIDATE` classifications in total and finding no other candidate classification. The final test gate reports `100 passed`, and `python -m compileall -q src scripts paper_replications` passes.

This conclusion means that the current finite models, persisted results, figures, and reproduction information are internally consistent under the specified tests and tolerances. It does not mean that general-equilibrium existence, uniqueness, branch completeness, or convergence of finite economies to a measure economy has been proved.

## 1. Paper Fidelity

**Passed, with limited scope.**

- The article and Supplement both come from official Econometric Society sources; page and example mappings are recorded in `CITATIONS.md`.
- Quota models use the emission-commodity coordinate and the paper's property-right accounting without adding a permit commodity.
- Tax models preserve `proj_k(p)=-t`, rescaling prices and the tax rate together when changing normalization.
- Examples 1-6 each have a mathematical ledger, source location, and configuration before code.
- Theorems 3-4 are described only as numerical checks; the `NO_EQUILIBRIUM` status of Example 4 is attributed only to the paper's theory.

Remaining boundary: the code does not cover the paper's most general preference relations, infinite-dimensional economies, or all existence assumptions.

## 2. Mathematical Correctness

**Passed the analytical and regression gates for the currently implemented objects.**

- Candidate clearing uses candidate allocations and production; reoptimized demand verifies only optimality.
- The Walras residual uses the candidate resource residual.
- Consumers and firms have explicit feasibility, budget/profit, and optimality-gap checks.
- The sign of `consumption - endowment - net production` is consistent across layers.
- Normalization, sign restrictions, clearing rules, and commodity semantics are separate.
- Population weights are not treated as welfare weights.
- Quota/tax budgets and diagnostics call the same policy-accounting layer.

Analytical exchange, production, the negative-price bad, Examples 1-2, and paper tables provide mutually independent validation points.

## 3. Numerical Robustness

**Passed under the specified search protocol, without a completeness claim.**

- Scalar analytical structures prefer Brent; target equations use SciPy root or least squares.
- Multistart includes deterministic, random, and continuation starts and stores an explicit seed.
- Only candidates that pass complete diagnostics enter clustering.
- Clustering distances compare allocations, production, and policy quantities as well as prices.
- Tax-rate sweeps use both continuation and fresh multistart and retain failure counts.
- Theoretical nonexistence from the paper is separated from numerical search status.

Residual risk: nonlinear systems may still miss roots; clustering thresholds and finite grids cannot replace interval certification or analytical proof.

## 4. Software Reproducibility

**Passed.**

- Every YAML file declares an importable runner; the unified entry point is `scripts/run_experiment.py`.
- `scripts/run_reproducibility_suite.py` rebuilds all results and figures in dependency order.
- Every milestone JSON contains `config_snapshot` and `reproducibility`.
- Metadata includes UTC time, Python and dependency versions, Git commit (explicitly null when unavailable), seed and numerical-setting locations, and candidate-status summaries.
- The six PNG files have axes, legends, titles, captions, source JSON files, and a SHA-256 manifest.
- `.gitignore` excludes `.venv`, caches, egg-info, build artifacts, and coverage output.

The current directory is not a Git work tree, so results truthfully record `git_commit: null`; no version identifier is fabricated.

## 5. Research Integrity

**Passed.**

- Paper replications, numerical mapping checks, software benchmarks, and paper-inspired experiments use distinct labels.
- Solver success is not treated as equilibrium, and solver failure is not treated as a nonexistence proof.
- Discovery of three candidate clusters is not described as "exactly three equilibria."
- No cardinal social welfare is fabricated for Example 2.
- Tail statistics are not described as a proof of uniform integrability, and the project does not claim to implement Loeb measure or a hyperfinite economy.
- Failed runs and non-verified counts are retained in parameter-sweep results.

## 6. Final Evidence

```text
pytest:                     100 passed
compileall:                 passed
persisted milestone files: 15
research PNG figures:       6
recorded verified classes:  130
artifact audit:             FINAL_AUDIT_PASSED
```

Machine-readable evidence is in `results/final_audit.json`; the figure manifest is in `figures/figure_manifest.json`.

## 7. Remaining Risks

1. Computational representations of Examples 3-6 are faithful to the verified finite examples but do not fully implement the paper's general theory.
2. Branch discovery depends on search intervals, starting points, and tolerances; no complete root certification is available.
3. YAML can modify exposed parameters, but arbitrary preferences or technologies cannot be added through configuration alone.
4. Current welfare conclusions are limited to agent-by-agent comparisons at fixed emissions.
5. The finite weighted experiment has not been connected to a proved convergence theorem for measure economies.

These limitations are recorded consistently in the README, REPORT, and OPEN_QUESTIONS. They do not prevent the current finite research toolkit from serving as a reliable baseline for the next stage.
