# Duanmu GE Lab - Milestone 3 Report

> Completion date: 2026-08-10  
> Scope: Finite Weighted Economies  
> Status: **PASS**

## 1. Implementation Summary

`Consumer` now has a strictly positive, finite `population_weight`. This weight enters only economic aggregates:

```text
X = sum_i lambda_i x_i,
E = sum_i lambda_i e_i.
```

Consumer budgets, utilities, and per-capita endowments are not multiplied by population weights. The core model has no social-welfare-weight field; any future welfare module must use a separate object. Both code and documentation therefore maintain:

```text
population weights != welfare weights.
```

## 2. Weighted Ownership

In a finite weighted production economy, `theta_ij` is an ownership density. Firm ownership and dividend accounting become:

```text
sum_i lambda_i theta_ij = 1,
sum_i lambda_i theta_ij pi_j = pi_j.
```

`FirmOwnership` preserves the raw input densities without silent normalization. Their unweighted, context-free sum is only a raw debugging statistic; `ProductionEconomy` computes the formal adding-up condition using population weights.

When all `lambda_i=1`, the new formulas reduce to the ordinary finite-consumer ownership accounting from Milestone 2, leaving the existing production benchmark unchanged.

## 3. Split-Agent Invariance Benchmark

The original economy has one type:

```text
lambda=1, e=(2,0), theta=1.
```

The split economy replaces it with two otherwise identical types:

```text
lambda_A=0.4, lambda_B=0.6,
e_A=e_B=(2,0),
theta_A=theta_B=1.
```

After splitting, the raw values in the ownership dictionary sum to `2`, but formal weighted ownership is `0.4+0.6=1`. The two economies use the same technology, preferences, and numeraire.

## 4. Experimental Results

`scripts/run_weighted_invariance.py` produces:

```text
original prices = [0.33333333333333454, 1.0]
split prices    = [0.33333333333333454, 1.0]

original aggregate allocation
= [1.4999999999999973, 0.5000000000000009]

split aggregate allocation
= [1.4999999999999973, 0.5000000000000009]

original classification = VERIFIED_CANDIDATE
split classification    = VERIFIED_CANDIDATE
```

All invariant distances:

| Object | L2 distance |
|---|---:|
| prices | `0.0` |
| weighted aggregate allocations | `0.0` |
| weighted aggregate endowments | `0.0` |
| firm plans | `0.0` |
| firm profits | `0.0` |
| candidate resource residuals | `0.0` |

Results are stored in `results/milestone3_split_agent_invariance.json`.

## 5. Automated Tests

New tests cover:

- rejection of zero, negative, NaN, and infinite population weights;
- equality of weighted endowments between the original and split economies;
- an explicit distinction between the raw share sum and weighted ownership total;
- independent solution and diagnostic verification of both economies;
- preservation of prices, aggregate allocations, production, profits, and residuals.

The full test suite after implementation reports:

```text
44 passed in 0.60s
```

## 6. Scope of Changes

- `Consumer.population_weight`;
- weighted aggregation in `ExchangeEconomy` and `ProductionEconomy`;
- weighted adding-up in production ownership/dividend diagnostics;
- use of the economy aggregate API by exchange/production solver caches;
- `build_split_agent_invariance_benchmarks()`;
- `tests/test_weighted_economy.py`;
- `scripts/run_weighted_invariance.py`;
- `docs/finite_weighted_economies.md`.

## 7. Research Boundaries

- This milestone validates finite atomic-mass accounting; it is not a continuum economy.
- Split-agent invariance is a structural regression test, not a proof of measure convergence, weak convergence, or a result involving Loeb measure.
- Current weights are not used for social-welfare aggregation; no welfare module has been implemented.
- Sampling, type partitioning, tail absorption, and large-economy size sweeps are absent.

Milestone 3 was closed only after the full tests, M1/M2/M3 experiments, compilation, and dependency checks all passed.
