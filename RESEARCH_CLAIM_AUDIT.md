# Research Claim Audit

## Status Semantics

Run-level statuses are centrally registered in `src/duanmu_ge_lab/experiment_status.py`. The CLI, reproducibility suite, and final audit accept only explicitly registered success statuses that exactly match each configuration's expectation. Unknown, failed, blocked, partial, or skipped required experiments cannot produce a successful exit code.

`VERIFIED_CANDIDATE` means only that a given finite candidate passes the implemented feasibility, budget, optimality, clearing, price, and policy-accounting diagnostics at the recorded numerical tolerances. It is not a proof of existence, uniqueness, or search completeness.

## Claim-by-Claim Review

| Term or label | Permitted meaning in this project | Inference explicitly not permitted |
|---|---|---|
| `PAPER_REPLICATION_SUCCESS` | The configured paper targets, numerical comparisons, and required diagnostics all pass | All general theorems in the paper have been proved by software |
| `NUMERICAL_MAPPING_CHECK_SUCCESS` | A specified finite instance of Theorems 3-4 is numerically consistent in both coordinate systems | The program proves the theorems themselves |
| `DISCOVERED_N_VERIFIED_CANDIDATE_CLUSTERS` | The specified search region, starts, and clustering rule found `N` diagnosed clusters | Exactly `N` equilibria exist, or no other roots exist |
| `NO_VERIFIED_CANDIDATE...` | Search or an analytical precheck produced no verifiable candidate | The general model has no equilibrium |
| `NO_EQUILIBRIUM` | Used only for the theoretical conclusion cited from the paper in Example 4 | Nonexistence follows from solver failure |
| Solver `success` or `converged` | The numerical algorithm met its own stopping criterion | The candidate is automatically an equilibrium |
| Finite-grid stability | Numerical stability within the present construction | Measure-economy convergence, uniform integrability, or a nonstandard-analysis result |

## Repository-Wide Findings

- No run-level success condition rewrites solver convergence as equilibrium existence; each candidate still undergoes independent diagnostics.
- No zero-discovery or failed start is presented as a general nonexistence proof.
- Multibranch outputs and figures consistently use `discovered`, `candidate`, and search-protocol qualifiers.
- Example 4 stores the theoretical nonexistence label separately from the numerical precheck.
- Figure generation now requires exact expected success statuses from all three upstream results; failed results cannot receive `FIGURE_GENERATION_SUCCESS`.
- The finite weighted experiment is explicitly a construction-specific numerical experiment and makes no continuum-limit claim.

The accurate description for a professor is therefore a **finite-model paper-replication, candidate-search, and independent numerical-diagnostics framework**. It should not be described as a universal GE solver, proof assistant, measure-theoretic solver, nonstandard-analysis implementation, or exhaustive equilibrium enumerator.
