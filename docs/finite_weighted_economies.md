# Finite Weighted Economies

## 1. Two Kinds of Weights Must Not Be Confounded

`population_weight` (denoted by `lambda_i`) is the economic mass of a consumer type or atom. It enters only the paper-defined aggregate quantities:

```text
aggregate consumption = sum_i lambda_i x_i,
aggregate endowment   = sum_i lambda_i e_i.
```

Social welfare weights belong to an additional welfare aggregator chosen by the researcher. They do not enter resource constraints, market clearing, firm profits, or consumer budgets. The current core model has no social-welfare-weight field; any future welfare module must use a separate, explicitly named data structure.

```text
population weights != social welfare weights.
```

## 2. Per-Capita and Aggregate Objects

`Consumer.endowment`, consumption bundles, and income are per-capita objects for a type. Population weights do not multiply individual budgets:

```text
individual income_i = p dot e_i + sum_j theta_ij pi_j.
```

The factor `lambda_i` is applied only when individual objects are aggregated into economy-wide totals. Weights must be finite and strictly positive. The core permits total mass to differ from one; whether masses are normalized to a probability measure is determined by the particular economy specification.

## 3. Weighted Ownership Densities

In a weighted economy, `theta_ij` is interpreted as an ownership density. The adding-up condition for each firm is:

```text
sum_i lambda_i theta_ij = 1.
```

Consequently, one must neither sum the raw share values in the dictionary without weights nor normalize the shares automatically. Aggregate dividend accounting is:

```text
sum_i lambda_i theta_ij pi_j = pi_j.
```

When every `lambda_i=1`, this reduces to the ordinary finite-consumer share adding-up condition from Milestone 2.

## 4. Split-Agent Invariance

The original economy has one consumer type:

```text
lambda=1,
e=(2,0),
theta=1.
```

The split economy replaces it with two otherwise identical types:

```text
lambda_A=0.4,
lambda_B=0.6,
e_A=e_B=(2,0),
theta_A=theta_B=1.
```

Therefore:

```text
lambda_A+lambda_B=1,
lambda_A theta_A+lambda_B theta_B=1.
```

The two types have identical per-capita demands. Weighted aggregate demand, aggregate endowment, ownership income, firm plans, equilibrium prices, and resource residuals should therefore equal those in the original economy. Notice that the raw values in the split ownership dictionary sum to 2, whereas the correctly weighted ownership total is 1.

## 5. Acceptance Criteria

Both the original and split economies must independently attain `VERIFIED_CANDIDATE`, with the following distances below strict tolerances:

- price distance;
- weighted aggregate allocation distance;
- weighted aggregate endowment distance;
- firm-plan and profit distance;
- candidate resource-residual distance.

This invariant is a structural test of the finite weighted aggregation implementation. It is not numerical proof of convergence for measure economies or of any result involving Loeb measure.
