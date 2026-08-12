# Duanmu GE Lab - Milestone 1.1 Audit Report

> Completion date: 2026-08-09  
> Scope: Milestone 1 diagnostic-architecture repair and regression gates  
> Final status: **PASS; ready for the next independent milestone**

## 1. Audit Conclusion

This pass fixed a substantive defect that changed the object being evaluated as an equilibrium. The old diagnostics checked market clearing with demand reoptimized at the given prices, while checking budgets and optimality with `candidate.allocations`. A single report therefore referred to two different allocations and could describe a resource-infeasible candidate as market-clearing.

The current implementation strictly separates:

```text
candidate resource residual   r(x) = sum_i x_i(candidate) - sum_i omega_i
formal Walras residual             = p dot r(x)
reoptimized demand residual   z(p) = sum_i x_i^opt(p) - sum_i omega_i
```

`r(x)` determines candidate market clearing, and `p dot r(x)` is the formal candidate Walras diagnostic. `z(p)` is retained only as reoptimization audit information and a reference for consumer optimality.

## 2. A1-A7 Repair Matrix

| ID | Issue | Repair | Final result |
|---|---|---|---|
| A1 | Market clearing incorrectly used reoptimized demand | Use `candidate_resource_residual` aggregated from `candidate.allocations` | PASS |
| A2 | Ambiguous object in the Walras residual | Make `candidate_walras_residual = p dot candidate_resource_residual` the formal field and report `reoptimized_walras_residual` separately | PASS |
| A3 | Missing consumption-set feasibility | Add finite-value, dimension, and nonnegativity checks plus a hard `consumer_feasibility` gate | PASS |
| A4 | Bundle distance treated as general optimality | Add `ConsumerOptimalityResult`; use utility gap as the formal criterion and label bundle gap only `UNIQUE_DEMAND_BENCHMARK_CHECK` | PASS |
| A5 | Exact floating-point equality for the numeraire | Use configurable absolute tolerance and `np.isclose` in `FixedNumeraire.encode` without modifying the input | PASS |
| A6 | Missing version-control exclusions | Add `.gitignore` entries for local environments, caches, builds, and coverage artifacts | PASS |
| A7 | Missing gates for these defects | Add six audit-related tests, increasing the full suite from 26 to 32 | PASS |

## 3. Mathematical Impact and Behavioral Change

### 3.1 Candidate Resource Feasibility

Old behavior: demand was reoptimized at `candidate.prices`, and its aggregate was used to judge markets, so feasibility of the candidate allocations was never actually checked.

New behavior: market residuals use only candidate allocations and the economy's actual aggregate endowment. Cached aggregate demand, aggregate endowment, and excess demand in the candidate do not enter the decision.

The key regression case uses:

```text
p = (1,1)
x_1(candidate) = x_2(candidate) = (0.8,0.2)
x_1^opt(p) = x_2^opt(p) = (0.5,0.5)
```

This gives:

```text
candidate_resource_residual = (0.6,-0.6)
reoptimized_resource_residual = (0,0)
candidate_walras_residual = 1.11e-16, approximately 0
market_clearing = false
consumer_optimality = false
```

This shows both that clearing by reoptimized demand cannot replace candidate resource feasibility and that a zero Walras residual cannot replace market-by-market checks.

### 3.2 Consumption Set

The Milestone 1 consumption set is `R_+^L`. The regression candidate

```text
x_1=(-0.1,1.1), x_2=(1.1,-0.1)
```

equals aggregate endowment in total and exactly exhausts each budget, but every consumer has a nonnegativity violation of `0.1`. The new diagnostics therefore report:

```text
market_clearing = true
budget_feasibility = true
consumer_feasibility = false
consumer_optimality = false
passed = false
```

### 3.3 Optimality Architecture

The new `ConsumerOptimalityResult` reports at least:

- `feasible`；
- `candidate_utility`；
- `optimal_utility`；
- `utility_gap`；
- `budget_violation`；
- `method`。

It also reports consumption-set violations and a bundle gap used only for unique-demand benchmarks. Formal `consumer_optimality` compares `abs(utility_gap)` with a centralized tolerance and does not require the candidate bundle to equal one particular optimal bundle, allowing the interface to support multiple optima in the future.

The supported scope is a `PreferenceModel` with numerical utility and a verifiable Marshallian-demand oracle. Relation-only preferences from the paper that have not been converted into numerical utility/optimization problems are explicitly labeled `UNSUPPORTED_UTILITY_OPTIMALITY_ORACLE`; they are neither guessed nor passed automatically.

### 3.4 Numeraire

`FixedNumeraire(index, value, tolerance)` now accepts inputs whose absolute error does not exceed the tolerance. Otherwise it raises an error containing the expected value, tolerance, actual value, and a statement that the input is not modified. The implementation performs no rounding, clipping, or silent price replacement.

## 4. Report Fields

The current JSON uses the following unambiguous fields:

```text
candidate_aggregate_allocation
candidate_resource_residual
candidate_walras_residual
reoptimized_allocations
reoptimized_resource_residual
reoptimized_walras_residual
consumer_feasibility_violations
utility_gaps
unique_demand_bundle_gaps
consumer_optimality_results
```

The Python report temporarily retains read-only compatibility aliases `market_residuals`, `walras_residual`, `recomputed_allocations`, and `optimality_gaps`, but they no longer appear in new JSON and project code no longer uses these ambiguous names.

## 5. Regression Tests

New or expanded tests cover:

1. A candidate must be rejected when its allocations do not clear even though reoptimized demand does.
2. The formal candidate Walras residual is explicitly separated from the reoptimized Walras residual.
3. Negative consumption must be rejected even when aggregate resources and budgets are satisfied.
4. Structured utility-gap optimality results and the unique-demand label.
5. A numeraire within tolerance is accepted without modifying the input.
6. A numeraire outside tolerance raises an explicit error.

The semantics of the existing fabricated-candidate test at `p=(2,1)` were also corrected. Its candidate allocations clear in aggregate, so `candidate_resource_residual=(0,0)`, but budgets and utility optimality fail. Only the independently reoptimized demand residual is `(-0.25,0.5)`.

## 6. Final Verification Results

Actual final run:

```text
.venv\Scripts\python.exe -m pytest -q
................................ [100%]
32 passed in 0.55s
```

Baseline run:

```text
.venv\Scripts\python.exe scripts\run_baseline.py
classification = VERIFIED_CANDIDATE
candidate_resource_residual = [0.0,0.0]
candidate_walras_residual = 0.0
utility_gaps = {Consumer 1: 0.0, Consumer 2: 0.0}
exit code = 0
```

Other gates:

```text
python -m compileall -q src -> exit code 0
python -m pip check          -> No broken requirements found
```

The first run with the new regressions had one failure: a test compared a theoretical zero with `== 0.0`, while the actual floating-point result was `1.11e-16`. The test assertion was corrected to `abs=1e-14`; the economic residual was neither truncated nor modified. The full suite then passed.

## 7. File and Environment Hygiene

`.gitignore` excludes:

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
build/
dist/
.coverage
htmlcov/
```

The local `.venv` may remain for VS Code and testing, but must not be committed or distributed. This pass deleted or moved no source code, tests, results, or research documents; all changes remained under the user-specified `codepart/duanmu_ge_lab`.

## 8. Remaining Boundaries

- The absolute tolerance for utility gaps still depends on the scale of the utility representation; scale-robust absolute/relative criteria should be designed before introducing heterogeneous utility models.
- The current oracle is closed-form Cobb-Douglas Marshallian demand. It validates this computational benchmark and does not imply support for the paper's general preference relations.
- `FREE_DISPOSAL` has commodity-level residual semantics but, at this stage, no corresponding production/bad benchmark.
- Candidate caches are still checked only for shape and finite values and are not used as a basis for mathematical decisions.

These boundaries are all recorded explicitly and do not affect the passing conclusion for the current Milestone 1.1 benchmark.
