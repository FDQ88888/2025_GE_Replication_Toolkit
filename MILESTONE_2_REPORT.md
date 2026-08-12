# Duanmu GE Lab - Milestone 2 Report

> Completion date: 2026-08-10  
> Scope: Production Economy  
> Status: **PASS**; quota, emission tax, and paper replication were not yet started

## 1. Objective

Milestone 2 extends the M1.1-audited exchange economy to a finite production economy without policy. The central invariant is:

```text
candidate_resource_residual
= sum_i candidate.x_i
  - sum_i e_i
  - sum_j candidate.y_j.
```

Firms use the net-output convention: positive coordinates are outputs and negative coordinates are inputs. Market clearing uses only the candidate `(x,y)`; consumer and firm optimality are recomputed by independent utility and profit oracles, respectively.

## 2. New Mathematical Objects

- `ProductionTechnology`: abstract interface for production sets and a global profit oracle;
- `CapacityConstrainedLinearTechnology`: analytical benchmark technology `Y={a*v:0<=a<=capacity}`;
- `Firm`: firm ID, technology, and ownership;
- `FirmOwnership`: preserves raw shares without silent normalization;
- `IncomeBreakdown`: endowment income, firm dividend income, policy income, and total income;
- `ProductionEconomy`: firms, ownership, demand, profit, income, and `x-e-y` resource accounting;
- `ProductionEquilibriumCandidate`: records only a solver point and carries no verification conclusion;
- `ProductionEquilibriumDiagnostics`: independently recomputes all production-economy conditions;
- `ProductionEquilibriumSolver`: a Brent scalar root solver used only for the two-good analytical benchmark.

`policy_income` is identically zero in this milestone and serves only as an explicit income coordinate; no policy rule is implemented here.

## 3. Analytical Production Benchmark

This benchmark is labeled `ANALYTICAL_PRODUCTION_BENCHMARK` and `OUR COMPUTATIONAL CHOICE`; it is not an Anderson-Duanmu paper replication.

Both consumers have:

```text
e_i=(1,0),
u_i(x)=x_i1^(1/2)x_i2^(1/2).
```

The firm's production set and ownership shares are:

```text
Y={a(-1,1):0<=a<=1/2},
theta_1=1/4,
theta_2=3/4.
```

Fix `p_2=1` and let `p_1=q`. Within the benchmark bracket `q in [0.1,0.8]`, unit profit is `1-q>0`, so production at capacity is the unique optimal plan:

```text
y*=(-1/2,1/2),
pi*=(1-q)/2.
```

After ownership income is included for both consumers, the market equation for good 1 gives:

```text
(3q+1)/(4q)=3/2,
q=1/3.
```

The complete analytical solution is:

```text
p*=(1/3,1)
y*=(-1/2,1/2)
pi*=1/3

I_1=endowment 1/3 + dividend 1/12 = 5/12
I_2=endowment 1/3 + dividend 1/4  = 7/12

x_1*=(5/8,5/24)
x_2*=(7/8,7/24)
```

See `docs/analytical_production_benchmark.md` for the complete derivation.

## 4. Independent Diagnostics

Hard checks in production diagnostics include:

1. solver success;
2. shape and finite values for the candidate and all caches;
3. the numeraire;
4. ownership shares adding up to 1 for each firm;
5. feasibility in each firm's production set;
6. availability of the firm profit oracle;
7. the gap between candidate profit and the independent maximum;
8. reconciliation of aggregate dividends with firm profit;
9. consumption-set feasibility;
10. candidate budget feasibility;
11. availability of the consumer utility oracle;
12. utility gaps;
13. consistency between solver caches and independent recomputation;
14. commodity-by-commodity candidate resource clearing;
15. the formal candidate Walras residual.

Budget exhaustion is reported separately but is not imposed unconditionally as a hard assumption in a general production economy. All tolerances are centralized in `NumericalTolerances`, with new thresholds for production feasibility, profit, ownership, and accounting.

## 5. Numerical Results

Running `scripts/run_production_baseline.py` gives:

```text
prices       = [0.33333333333333454, 1.0]
firm plans   = [[-0.5, 0.5]]
firm profits = [0.3333333333333327]
classification = VERIFIED_CANDIDATE
```

Distances from the analytical solution:

| Object | L2 distance |
|---|---:|
| prices | `1.22124532708767e-15` |
| allocations | `2.29835607586495e-15` |
| firm plans | `0.0` |
| firm profits | `6.10622663543836e-16` |

Diagnostic errors:

| Diagnostic | Maximum error |
|---|---:|
| ownership adding-up | `0.0` |
| firm feasibility | `0.0` |
| profit gap | `0.0` |
| dividend accounting | `0.0` |
| consumer feasibility | `0.0` |
| budget violation/exhaustion | `0.0` |
| utility gap | `0.0` |
| candidate cache consistency | `0.0` |
| market violation | `2.66453525910038e-15` |
| candidate Walras residual | `3.15544362088405e-30` |

Results are stored in:

```text
results/milestone2_production_baseline.json
```

## 6. Key Regression Tests

- known globally optimal firm plan and profit;
- production-set violation by an over-capacity plan;
- firm shutdown at a negative profit margin;
- shares `0.4+0.4` remain `0.8` and are never normalized;
- dividend incomes `1/12` and `1/4`;
- `sum x = sum e + sum y`;
- recovery of the full analytical solution by the solver;
- a `y=0` candidate that clears markets exactly but is rejected for a firm profit gap of `1/3` and a consumer utility gap;
- simultaneous failure of ownership and dividend accounting when shares do not add up;
- rejection by finite-value and cache-consistency hard gates when a nested income cache contains `NaN`.

## 7. Testing and Verification

Final test gate:

```text
.venv\Scripts\python.exe -m pytest -q
......................................... [100%]
41 passed in 0.57s
```

The first full Milestone 2 run reported `1 failed, 39 passed`: the general `Consumer` layer rejected negative income too early, causing an existing negative-price test to receive an income-domain error rather than the Cobb-Douglas price-domain error. After the fix, the general layer checks only that total income is finite, while support for negative income is determined by the specific preference oracle; budget diagnostics can still compute negative income. This preserves the correct boundary for future transmission of firm losses through ownership.

A subsequent self-audit found a `NaN` risk in nested income caches. Adding a finite-value gate and regression test brought the total to 41 tests. No test was repaired through clipping, residual modification, or looser mathematical tolerances.

## 8. File Inventory

Core:

```text
src/duanmu_ge_lab/core/income.py
src/duanmu_ge_lab/core/production.py
src/duanmu_ge_lab/core/production_economy.py
src/duanmu_ge_lab/equilibrium/production_diagnostics.py
src/duanmu_ge_lab/solvers/production_solver.py
```

Experiments and documentation:

```text
scripts/run_production_baseline.py
docs/analytical_production_benchmark.md
results/milestone2_production_baseline.json
MILESTONE_2_REPORT.md
```

Tests:

```text
tests/test_production.py
tests/test_production_equilibrium.py
```

## 9. Research Boundaries

- The current technology is a bounded, single-activity linear set; this does not solve general nonlinear or unbounded production correspondences.
- The current production solver supports only two goods, one independent price, and exact clearing in every market.
- Cobb-Douglas demand still supports only strictly positive prices; signed-price economies are handled in a separate milestone.
- Firm losses may enter income accounting as signed profits, but this benchmark produces no losses.
- There is no government firm, quota right, tax revenue, rebate rule, or externality state.
- Anderson-Duanmu Example 1 is not implemented at this milestone. The official Supplement has been obtained, but Definitions 3.1-3.5 must first be represented in a later quota module.

## 10. Gate Conclusion

Milestone 2 completed its analytical solution, solver, firm optimality, ownership income, candidate resource accounting, independent diagnostics, negative cases, and reproducible experiment. Progression to Milestone 3 was allowed only after the final full suite, M1/M2 scripts, compileall, and pip check all passed again.
