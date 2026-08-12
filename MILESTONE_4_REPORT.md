# Duanmu GE Lab - Milestone 4 Report

> Completion date: 2026-08-10  
> Scope: Signed Prices, Bads, Clearing Rules  
> Status: **PASS**

## 1. Implemented Components

- `PriceSign` and coordinate-wise `PriceSignRestrictions`;
- positive-proportional round trips between signed L1 and fixed-numeraire normalization;
- `ConsumptionSet`, `NonnegativeOrthant`, and `BoxConsumptionSet`;
- an analytical negative-price demand oracle for `BadAbsorptionLinearUtility`;
- independent hard checks for price normalization and price signs in diagnostics;
- an exact, non-free-disposal bad benchmark;
- a contrastive regression test for free disposal and exact clearing.

All objects maintain the following invariant:

```text
commodity semantic kind
!= price sign restriction
!= consumption feasibility
!= clearing rule.
```

## 2. Signed-Price Handling

Price restrictions may be `ANY`, `NONNEGATIVE`, `NONPOSITIVE`, `POSITIVE`, `NEGATIVE`, or `ZERO`. The economy specification passes restrictions explicitly to diagnostics; a BAD commodity label creates no default restriction.

`normalize_signed_l1` preserves signs, and `rescale_to_fixed_numeraire` permits only positive proportional scaling. Tests confirm:

```text
(-2,1) -> (-2/3,1/3) -> (-2,1).
```

Attempting to obtain an oppositely signed numeraire through negative scaling raises an explicit error.

## 3. Bad-Absorption Benchmark

This benchmark is a software-validation choice, not a paper replication:

```text
e=(1 bad, 2 good),
X=[0,1] x R_+,
u(b,g)=g-b/2,
p=(-1,1),
x*=(1,2).
```

Formal results:

```text
fixed-numeraire prices = [-1,1]
signed-L1 prices       = [-0.5,0.5]
candidate residual     = [0,0]
candidate Walras       = 0
classification         = VERIFIED_CANDIDATE
```

`BoxConsumptionSet` enforces the consumption bound; candidate bad consumption of `1.1` has feasibility violation `0.1`.

## 4. Clearing-Rule Regression

For candidate residual `(-0.5,0)`:

- with `FREE_DISPOSAL` for the first commodity, the market-clearing check passes;
- with `EXACT` for the first commodity, the market-clearing check fails.

This test validates only the commodity-by-commodity resource region and adds no complementarity condition absent from the model definition.

## 5. Test Results

New tests cover:

- signed-L1/numeraire round trips;
- rejection of negative proportional scaling;
- the fact that a BAD label does not imply a negative price;
- a verified candidate with a negative-price bad;
- bounded bad absorption;
- distinct decisions under exact clearing and free disposal.

The full test suite after implementation reports:

```text
50 passed in 0.49s
```

## 6. Files and Outputs

```text
src/duanmu_ge_lab/core/consumption.py
src/duanmu_ge_lab/equilibrium/prices.py
tests/test_signed_prices_and_bads.py
scripts/run_signed_bad_baseline.py
docs/signed_prices_bads_clearing.md
results/milestone4_signed_bad_absorption.json
MILESTONE_4_REPORT.md
```

## 7. Research Boundaries

- The current negative-price preference is a two-coordinate analytical benchmark, not a general incomplete preference.
- The current benchmark has no production byproducts, sequestration, externalities, or policy.
- `FREE_DISPOSAL` implements only the residual inequality in its definition, with no automatic complementarity condition.
- Anderson-Duanmu's `Z(m)` and emission-tax compliance region were not yet implemented at this milestone; they must be defined separately from the original text in policy milestones.

M4 was closed only after all existing and new tests, four experiment sets, compilation, and dependency checks passed.
