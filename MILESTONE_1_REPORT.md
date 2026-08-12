# Duanmu GE Lab - Milestone 1 Report

> **Historical report notice (2026-08-09):** This file records the original Milestone 1 delivery. A later audit found that it conflated candidate resource residuals with reoptimized demand residuals. The current implementation and final verification semantics are defined by `MILESTONE_1_1_AUDIT_REPORT.md`; this file is no longer the normative description of current diagnostics.

> Completion date: 2026-08-09  
> Scope: Minimal General Equilibrium Engine  
> Status: Completed and stopped; Production, Quota, Emission Tax, Bads, Externalities, and Finite Approximation were not entered.

## 1. What Was Implemented

This milestone established an installable and testable finite exchange-economy core that runs on Windows with VS Code and Python 3.11+. The completed computational chain is:

```text
economic parameters
-> Consumer
-> closed-form individual demand
-> ExchangeEconomy
-> aggregate excess demand
-> FixedNumeraire
-> scalar equilibrium solver
-> EquilibriumCandidate
-> independent EquilibriumDiagnostics
-> VERIFIED_CANDIDATE
```

Implemented objects include:

- `Commodity`, `CommodityKind`, and `ClearingRule`;
- abstract `PreferenceModel` and `CobbDouglasUtility`;
- `Consumer` with endowment wealth, demand, utility, and budget residuals;
- `ExchangeEconomy` with aggregate endowment, demand, excess demand, market-by-market residuals, and a Walras residual;
- abstract `PriceNormalization`, `FixedNumeraire`, and signed-L1 reporting normalization;
- a two-good, one-independent-price `ExchangeEquilibriumSolver`;
- `EquilibriumCandidate` without a verification conclusion;
- `NumericalTolerances`, a four-level candidate classification, and independent diagnostics;
- an analytical benchmark, command-line script, JSON result, and 26 automated tests.

## 2. Mathematical Benchmark

The current benchmark is a `SOFTWARE VALIDATION BENCHMARK`, not an Anderson-Duanmu paper replication.

Consumer 1:

```text
omega_1 = (1,0)
u_1(x_11,x_12) = x_11^(1/2) x_12^(1/2)
```

Consumer 2:

```text
omega_2 = (0,1)
u_2(x_21,x_22) = x_21^(1/2) x_22^(1/2)
```

Good 2 is the numeraire: `p_2=1`. Excess demand is defined consistently throughout the project as:

```text
z(p) = aggregate demand - aggregate endowment.
```

## 3. Analytical Equilibrium

Cobb-Douglas Marshallian demand is:

```text
x_l = alpha_l w / p_l.
```

When `alpha_1=alpha_2=1/2`:

```text
w_1 = p_1
w_2 = 1

z_1(p_1,1) = -1/2 + 1/(2p_1)
z_2(p_1,1) = (p_1-1)/2
```

Solving `z_1=0` gives:

```text
p* = (1,1)
x_1* = (1/2,1/2)
x_2* = (1/2,1/2)
```

See `docs/analytical_benchmark.md` for the complete derivation.

## 4. Numerical Method

- Price coordinates: `FixedNumeraire(index=1, value=1.0)`;
- independent unknown: `p_1`;
- sole solved equation: `z_1(p_1,1)=0`;
- market unused in root finding: good 2, checked by diagnostics;
- method: SciPy `root_scalar(..., method="brentq")`;
- bracket: `[0.05,20.0]`;
- `xtol=1e-13`, `rtol=1e-13`, `maxiter=100`.

The solver neither imposes two market equations on one unknown nor uses Walras law to modify or replace a residual.

## 5. Solver Result

Actual run results:

```text
solver method      = brentq
solver success     = true
iterations         = 13
function calls     = 14
numerical prices   = [1.0, 1.0]
allocations        = [[0.5,0.5], [0.5,0.5]]
price L2 distance  = 0.0
allocation distance= 0.0
```

The signed-L1 reporting prices are `[0.5,0.5]`. This step is only for reporting and does not change the solver's numeraire coordinates.

## 6. Independent Diagnostics

Diagnostics recompute demand, budgets, and market quantities from `Economy + candidate.prices + candidate.allocations`, without trusting aggregate demand, aggregate endowment, or excess demand cached in the candidate.

Actual strict diagnostic results:

| Check | Numerical error | Result |
|---|---:|---|
| Numeraire error | `0.0` | PASS |
| Good 1 residual | `0.0` | PASS |
| Good 2 residual | `0.0` | PASS |
| Max market violation | `0.0` | PASS |
| Consumer 1 budget residual | `0.0` | PASS |
| Consumer 2 budget residual | `0.0` | PASS |
| Max budget violation | `0.0` | PASS |
| Max budget exhaustion gap | `0.0` | PASS |
| Consumer 1 optimality gap | `0.0` | PASS |
| Consumer 2 optimality gap | `0.0` | PASS |
| Walras residual `p dot z(p)` | `0.0` | PASS |

Final classification:

```text
VERIFIED_CANDIDATE
```

The invalid-candidate test manually sets `solver_success=True` and cached `excess_demand=[0,0]`, while using `p=(2,1)` and incorrect allocations. Independent diagnostic recomputation gives:

```text
z(p) = [-0.25, 0.5]
p dot z(p) = 0.0
classification = SOLVER_POINT
```

The test therefore shows that solver success cannot replace equilibrium verification and that Walras law cannot replace market-by-market clearing.

## 7. Test Results

Actual final run:

```text
python -m pytest -q
.......................... [100%]
26 passed in 0.55s
```

Coverage includes:

- Cobb-Douglas demand ground truth;
- invalid alpha, alpha values that do not sum to one, and dimension errors;
- explicit rejection of zero/negative Cobb-Douglas prices;
- wealth `p dot omega`;
- the sign of the budget residual;
- FixedNumeraire encode/decode;
- sign preservation, positive-scale invariance, and zero-vector errors for signed L1;
- analytical equilibrium prices and allocations;
- separate clearing of both markets;
- Walras law at nonequilibrium prices;
- return of `FAILED_RUN` when the bracket has no sign change;
- rejection of fabricated solver success and cached residuals;
- rejection of incorrect shapes in candidate cache vectors.

Other verification:

```text
python scripts/run_baseline.py   -> exit code 0
python -m compileall src         -> success
python -m pip check              -> No broken requirements found
package import                   -> duanmu_ge_lab 0.1.0
```

Verification environment: Python 3.12.13, NumPy 2.5.2, SciPy 1.18.0, and pytest 9.1.1. Project metadata declares Python `>=3.11`.

## 8. Files Created

Project and documentation:

- `pyproject.toml`
- `README.md`
- `CITATIONS.md`
- `MILESTONE_1_REPORT.md`
- `docs/analytical_benchmark.md`
- `scripts/run_baseline.py`
- `results/milestone1_baseline.json`

Core package:

- `src/duanmu_ge_lab/__init__.py`
- `src/duanmu_ge_lab/benchmarks.py`
- `src/duanmu_ge_lab/core/{commodity,preferences,consumer,economy}.py`
- `src/duanmu_ge_lab/equilibrium/{candidate,normalization,diagnostics}.py`
- `src/duanmu_ge_lab/solvers/exchange_solver.py`
- three nonempty package `__init__.py` files

Tests:

- `tests/test_preferences.py`
- `tests/test_consumer.py`
- `tests/test_price_normalization.py`
- `tests/test_market_clearing.py`
- `tests/test_walras_law.py`
- `tests/test_analytical_equilibrium.py`
- `tests/test_diagnostics_reject_invalid.py`

The project also generated `.venv`, the pytest cache, Python bytecode, and editable-install metadata, all within the designated `codepart/duanmu_ge_lab` directory.

## 9. Known Limitations

- The solver supports only two goods, one non-numeraire price, and `EXACT` clearing for all commodities.
- `CobbDouglasUtility.marshallian_demand` supports only strictly positive prices and explicitly raises `UnsupportedPriceDomainError` otherwise.
- `ClearingRule.FREE_DISPOSAL` is represented in data and diagnostic semantics, but this milestone's solver and benchmark do not use it.
- There is no production, firm income, government, quota, emission tax, bad-specific feasible set, or externality.
- There is no multistart, continuation, clustering, or claim of multiple-equilibrium completeness.
- Numerical results validate only the current finite benchmark and do not prove general existence or uniqueness.

## 10. Design Decisions

1. `PreferenceModel` is an abstract interface; Cobb-Douglas is this milestone's computational choice.
2. `CommodityKind` does not determine price signs, monotonicity, disposal, or regulation.
3. `FixedNumeraire` is separate from price-sign restrictions.
4. There is no softmax; the signed-L1 function preserves negative signs and rejects the zero vector.
5. The solver solves only `z_1=0`; diagnostics check `z_2` and Walras law separately.
6. A candidate stores no solver self-certification field such as `market_clearing_pass`.
7. Diagnostics do not use cached candidate residuals to make decisions.
8. Strict tolerances are centralized in `NumericalTolerances`; there are no scattered permissive magic tolerances.
9. A bracket without a sign change returns a failed candidate; numerical failure is not interpreted as equilibrium nonexistence.
10. Benchmark constants appear only in `benchmarks.py`, benchmark documentation, script output, and tests; they do not leak into general `Consumer`, `Economy`, or solver logic.

## 11. Failed Attempts / Bugs Encountered

- The ordinary system `PATH` had no `python` command. Resolution: use Codex-provided Python 3.12.13 to create the project-local `.venv`; the README still gives standard Windows Python 3.11+ installation commands.
- On the first attempt to create test files, the patch tool did not automatically create the parent `tests/` directory. Work continued after explicitly creating it, with no lost files.
- The first full suite reported `25 passed`. A software self-audit found that diagnostics should also reject shape errors in cached aggregate candidate vectors; after adding the check and one test, the final count was `26 passed`.
- On bracket `[2,3]`, the residual has no sign change. The solver returns `FAILED_RUN` as designed without crashing; this case is tested.
- There are no unresolved test failures or known runtime defects.

In the code, `np.maximum.reduce` is used only to construct market-error scales for diagnostics, and `np.abs(price_array)` is used only for the required signed-L1 normalization. There is no clipping, replacement of prices by absolute values, epsilon price replacement, or residual patching.

## 12. Exact Commands to Reproduce

Windows PowerShell:

```powershell
cd <path-to-project>\duanmu_ge_lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\run_baseline.py
.\.venv\Scripts\python.exe -m compileall src
```

JSON result:

```text
<project-root>\results\milestone1_baseline.json
```

## 13. Recommended Milestone 2

Under the approved `IMPLEMENTATION_PLAN.md`, the recommended next stage was Production, but it required explicit initiation by a new task. This milestone created no production code.

The recommended first objectives for Milestone 2 were:

1. minimal interfaces for `Firm` and `ProductionTechnology`;
2. net-production vectors and profit maximization;
3. firm ownership and dividends entering consumer income;
4. resource accounting extended to `demand - endowment - production`;
5. a production-economy benchmark with an analytical solution;
6. independent profit-gap and ownership-accounting diagnostics.

Before entering Milestone 2, the most valuable files for mathematical review were:

- `docs/analytical_benchmark.md`
- `src/duanmu_ge_lab/equilibrium/diagnostics.py`
- `src/duanmu_ge_lab/solvers/exchange_solver.py`
- `tests/test_diagnostics_reject_invalid.py`
