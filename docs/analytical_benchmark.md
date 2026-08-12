# Milestone 1 Analytical Benchmark

## 1. Purpose

This benchmark uses a 2-consumer by 2-good exchange economy with a known exact solution to validate the following computational chain:

```text
endowments -> wealth -> individual demand -> aggregate excess demand
-> price normalization -> scalar root -> candidate -> independent diagnostics
```

It is a `SOFTWARE VALIDATION BENCHMARK`, not a replication of the Anderson-Duanmu paper.

## 2. Economy

There are two ordinary goods and two consumers. Every market requires `EXACT` clearing.

Consumer 1 has endowment and utility

```text
omega_1 = (1, 0),
u_1(x_11,x_12) = x_11^(1/2) x_12^(1/2).
```

Consumer 2 has endowment and utility

```text
omega_2 = (0, 1),
u_2(x_21,x_22) = x_21^(1/2) x_22^(1/2).
```

Prices are `p=(p_1,p_2)`. Good 2 is selected as the numeraire:

```text
p_2 = 1.
```

This is a choice of numerical coordinates, not a permanent theoretical assumption of the project.

## 3. Cobb-Douglas Marshallian Demand

For utility

```text
u(x_1,x_2) = x_1^alpha x_2^(1-alpha)
```

and budget constraint

```text
p_1 x_1 + p_2 x_2 <= w,
```

when `p_1,p_2>0` and `0<alpha<1`, the interior optimum spends the fraction `alpha` of wealth on good 1 and the fraction `1-alpha` on good 2:

```text
x_1 = alpha w / p_1,
x_2 = (1-alpha) w / p_2.
```

Both consumers in this benchmark have `alpha=1/2`.

## 4. Wealth and Individual Demand

Wealth is the market value of the endowment:

```text
w_i(p) = p dot omega_i.
```

Consumer 1:

```text
w_1 = p_1,
x_11 = (1/2) p_1 / p_1 = 1/2,
x_12 = (1/2) p_1 / p_2 = p_1/2.
```

Consumer 2:

```text
w_2 = p_2 = 1,
x_21 = (1/2) / p_1,
x_22 = (1/2) / p_2 = 1/2.
```

## 5. Market for Good 1 and the Relative Price

Aggregate demand for good 1 is

```text
X_1(p_1,1) = 1/2 + 1/(2p_1).
```

Aggregate endowment is

```text
Omega_1 = 1.
```

The project uses a fixed sign convention for excess demand:

```text
z(p) = aggregate demand - aggregate endowment.
```

Thus,

```text
z_1(p_1,1) = -1/2 + 1/(2p_1).
```

Exact clearing requires `z_1=0`:

```text
-1/2 + 1/(2p_1) = 0,
p_1 = 1.
```

Because `p_2=1`, the analytical equilibrium price is

```text
p* = (1,1).
```

## 6. Equilibrium Allocation

Substituting `p_1=p_2=1` into demand gives:

```text
x_1* = (1/2,1/2),
x_2* = (1/2,1/2).
```

## 7. Independent Check of Good 2

Aggregate demand for good 2 is

```text
X_2(p_1,1) = p_1/2 + 1/2.
```

Aggregate endowment is `Omega_2=1`; hence,

```text
z_2(p_1,1) = (p_1-1)/2.
```

At `p_1=1`:

```text
z_2(1,1) = 0.
```

The solver does not use this equation to find `p_1`; diagnostics recompute and check it independently.

## 8. Walras Law

For every positive `p_1`:

```text
p dot z(p)
= p_1[-1/2 + 1/(2p_1)] + [(p_1-1)/2]
= (-p_1/2 + 1/2) + (p_1/2 - 1/2)
= 0.
```

This example clearly shows that Walras law can hold before markets clear commodity by commodity. For example, at `p=(2,1)`, `z_1=-1/4` and `z_2=1/2`, yet `p dot z=0`.

The following must therefore remain distinct:

1. **SOLVED MARKET CONDITION**: solve `z_1(p_1,1)=0`;
2. **UNUSED MARKET CLEARING CHECK**: independently check `z_2(p_1,1)=0`;
3. **WALRAS LAW CHECK**: independently report `p dot z(p)`.

Walras law cannot replace commodity-by-commodity market diagnostics and must not be used to modify the residual.

## 9. Ground Truth for Automated Tests

The tests use:

```text
p* = [1.0, 1.0]
allocations* = [
  [0.5, 0.5],
  [0.5, 0.5]
]
aggregate demand = [1.0, 1.0]
aggregate endowment = [1.0, 1.0]
z(p*) = [0.0, 0.0]
p* dot z(p*) = 0.0
```

The numerical solver's output may be classified as `VERIFIED_CANDIDATE` only after independent diagnostics jointly verify price normalization, budgets, individual optimality, both markets, and Walras law.

## 10. Candidate Allocations Must Be Separated from Reoptimized Demand

`z(p)` is excess demand obtained by resolving the consumer problems at given prices. It is used to solve for prices and inspect the demand system. When validating a specific candidate `(p,x)`, however, market feasibility must use the candidate allocation itself:

```text
r(x) = sum_i x_i - sum_i omega_i,
formal candidate Walras residual = p dot r(x).
```

For example, at `p=(1,1)`, consider the fabricated allocation

```text
x_1 = x_2 = (0.8,0.2).
```

Reoptimized demand remains `(0.5,0.5)`, so `z(p)=(0,0)`; but the candidate resource residual is

```text
r(x) = (0.6,-0.6),
p dot r(x) = 0.
```

Thus this candidate neither clears markets commodity by commodity nor gives consumer-optimal allocations. The counterexample also shows that even a zero formal candidate Walras residual does not imply clearing in every market.

Consumer optimality uses the utility gap

```text
utility_gap_i = u_i(x_i^opt) - u_i(x_i^candidate),
```

where `x_i^opt` is supplied by an independent Marshallian-demand oracle under the budget constraint and consumption set. Optimal demand is unique in the Cobb-Douglas benchmark, so bundle distance is also reported; it is labeled only `UNIQUE_DEMAND_BENCHMARK_CHECK` and is not a formal criterion under general preferences. The current validator supports only preferences with numerical utility and a valid optimization oracle. Relation-only preferences from the paper that have not been made computational are explicitly unsupported.
