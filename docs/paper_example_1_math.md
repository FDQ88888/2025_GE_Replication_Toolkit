# Paper Example 1: Mathematical Replication Specification

## Status and scope

This document is the pre-implementation specification for Anderson and Duanmu
(2025), Example 1. It distinguishes the paper's model from later computational
choices. The replication uses the paper's existing commodity coordinates; it does
not introduce a permit commodity.

Primary locations:

- Main article, PDF pages 11-12 (journal pages 367-368), Example 1.
- Supplementary Material, PDF pages 11-12, Section 3.1, Claims 3.1-3.2.
- Quota accounting: main article, PDF pages 7-10, Definitions 3.1-3.5 and
  Remark 3.3.

## Paper primitives

### Commodities and prices

There are three commodities in this order:

1. CO2 emissions, the single regulated commodity;
2. coal;
3. electricity.

The paper uses signed L1 normalization,

```text
Delta = {p in R^3 : |p_CO2| + |p_coal| + |p_electricity| = 1}.
```

The quota price is not another commodity price. For one regulated coordinate it is

```text
q = -p_CO2.
```

### Consumers

The agents are `omega_1` and `omega_2`. Both consumption sets are

```text
X_i = {0} x R_+^2.
```

Thus consumers cannot absorb the CO2 coordinate in this example. Endowments are

```text
e_1 = (0, 1, 0),
e_2 = (0, 0, 0).
```

Given total net CO2 emissions `v`, the paper's utility representations are

```text
u_1(x_1; v) = x_electricity,1 - v^2,
u_2(x_2; v) = x_coal,2        - v^2.
```

The external term is constant in each consumer's own-demand problem once the
aggregate allocation and production of the other market participants are fixed.

### Firms and ownership

The government firm `firm_0` has production set

```text
Y_0 = {0}.
```

The private firm `firm_1` has the unbounded linear production set

```text
Y_1 = {(r, -r, r) : r >= 0}.
```

It burns coal, produces electricity, and emits CO2. The ownership shares are

```text
theta_1,0 = 0,   theta_2,0 = 1,
theta_1,1 = 1/2, theta_2,1 = 1/2.
```

### Quota and compliance region

Write `m <= 0` for the negative of the emissions cap and `v=-m`. Example 1 studies
`v in (0,1]`. All quota rights are assigned to the government firm:

```text
m^(0) = (m),
m^(1) = (0),
m = m^(0) + m^(1),
Z(m) = {m} x {0} x {0}.
```

For firm `j`, paper profit is

```text
pi_j^m(p,y_j) = p dot y_j + p_CO2 m^(j).
```

The quota term is constant in `y_j`, so the firm's production choice still
maximizes `p dot y_j`. Consumer `i` has budget income

```text
I_i = p dot e_i + sum_j theta_i,j pi_j^m(p,y_j).
```

These formulas are from the discussion immediately before Definition 3.5 on main
article PDF pages 9-10.

## Paper analytical equilibrium

Claim 3.1 in Supplement Section 3.1 gives the unique quota equilibrium for every
`v=-m in (0,1]`. Rewritten in `v` notation:

```text
x_1^* = (0, 0, v),
x_2^* = (0, 1-v, 0),
y_0^* = (0, 0, 0),
y_1^* = (v, -v, v),
p^*   = ((v-1)/2, v/2, 1/2).
```

The associated quota price and profits are

```text
q^*    = (1-v)/2,
pi_0^* = p_CO2^* (-v) = v(1-v)/2,
pi_1^* = p^* dot y_1^* = 0.
```

Consumer incomes are

```text
I_1^* = p_coal^* = v/2,
I_2^* = pi_0^*   = v(1-v)/2.
```

Consequently, consumer 1 spends all income on electricity and consumer 2 spends
all income on coal:

```text
I_1^* / p_electricity^* = v,
I_2^* / p_coal^*        = 1-v.
```

The paper utilities are

```text
u_1^* = v - v^2,
u_2^* = 1-v - v^2.
```

## Identities required from the implementation

The candidate resource residual must be computed from candidate coordinates:

```text
r = sum_i x_i^* - sum_i e_i - sum_j y_j^* = (-v, 0, 0) in Z(-v).
```

The signed normalization identity is

```text
|(v-1)/2| + v/2 + 1/2 = 1.
```

The private firm's unit margin is zero:

```text
p_CO2^* - p_coal^* + p_electricity^* = 0.
```

The quota-adjusted Walras identity is

```text
p^* dot r - p_CO2^* m = 0.
```

This is the relevant identity because aggregate consumer income includes the quota
profit `p_CO2 m`; raw `p dot r` is generally not zero.

## Computational benchmark choice

The checked configuration uses

```text
v = 1/2, m = -1/2.
```

This is an implementation choice inside the paper's admissible interval. It makes
all analytical coordinates exactly representable in binary floating point:

```text
p^*   = (-1/4, 1/4, 1/2),
x_1^* = (0, 0, 1/2),
x_2^* = (0, 1/2, 0),
y_1^* = (1/2, -1/2, 1/2),
q^*   = 1/4,
pi_0^*= 1/8.
```

The replication may use numerical root finding to recover these values, but it may
claim `PAPER_REPLICATION_SUCCESS` only after independent diagnostics compare every
reported coordinate and accounting identity with the analytical target.
