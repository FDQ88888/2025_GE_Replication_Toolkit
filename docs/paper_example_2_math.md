# Paper Example 2: Mathematical Replication Specification

## Status and source boundary

This document specifies the replication of Anderson and Duanmu (2025), Example 2.
Primary locations are main article PDF pages 12-13 (journal pages 368-369) and
Supplementary Material PDF pages 12-14, Section 3.2, Claims 3.3-3.4.

The paper does not provide a cardinal utility formula for Example 2. It states that
each agent derives utility from electricity, is indifferent to coal, and is affected
by total CO2 emissions. Therefore the replication reports exact consumption and the
welfare ordering identified by the paper. It must not label a fabricated cardinal
number as "paper utility."

## Paper primitives

The commodity order is `(CO2, coal, electricity)`, with CO2 regulated. There are
three agents `omega in {1,2,3}`. Each has

```text
X_omega = {0} x R_+^2,
e_omega = (0, omega, 0).
```

All agents demand only electricity in their own-consumption problem. Total coal
endowment is six.

The government firm has `Y_0={0}`. The private production sets are

```text
Y_1 = {(r, -r, r) : r >= 0},
Y_2 = {(-2s, 0, -s) : s >= 0}.
```

Firm 1 burns coal and produces electricity with CO2 as a byproduct. Firm 2 uses
electricity to sequester CO2. Ownership is

```text
theta_omega,0 = 1/3,
theta_omega,2 = 1/3,
theta_omega,1 = omega/6.
```

For total emissions `v=-m in [0,6)`, the compliance region is

```text
Z(m) = {m} x {0} x {0}.
```

Firm 2 always receives zero quota. The paper compares:

- global quota: `m^(0)=m`, `m^(1)=m^(2)=0`;
- cap-and-trade: `m^(1)=m`, `m^(0)=m^(2)=0`.

## Analytical equilibrium

Claim 3.3 gives the unique signed-L1 normalized equilibrium price in both quota
allocations:

```text
p^* = (-1/4, 1/4, 1/2),
q^* = 1/4.
```

Market clearing and quota compliance determine production. Firm 1 uses all coal,
so its activity is 6. Firm 2's activity is `(6-v)/2`:

```text
y_0^* = (0, 0, 0),
y_1^* = (6, -6, 6),
y_2^* = (-(6-v), 0, -(6-v)/2).
```

Both private firms have zero operating profit because

```text
p_CO2 - p_coal + p_electricity = 0,
-2 p_CO2 - p_electricity      = 0.
```

Claim 3.4 gives consumption.

Global quota:

```text
x_omega^G = (0, 0, omega/2 + v/6).
```

The government firm's quota profit is `v/4`; each agent receives `v/12`.

Cap-and-trade:

```text
x_omega^C = (0, 0, omega/2 + v*omega/12).
```

Firm 1's quota profit is `v/4`; agent `omega` receives `v*omega/24` through firm
ownership.

At fixed `v`, total electricity consumption and all aggregate resources are the
same in the two regimes. Property rights change individual income and consumption.
For every `v in [0,6)`, agent 1 is better off under global quota and agent 3 is
better off under cap-and-trade. Agent 2 receives the same electricity in both:

```text
x_electricity,1^G - x_electricity,1^C =  v/12,
x_electricity,2^G - x_electricity,2^C =  0,
x_electricity,3^G - x_electricity,3^C = -v/12.
```

This ordinal comparison is the paper-supported welfare result. The externality is
held fixed because total emissions `v` is identical across the two allocations.

## Checked computational instance

The replication config selects `v=3`, an interior value with exact binary prices
and simple rational quantities:

```text
y_1^* = (6, -6, 6),
y_2^* = (-3, 0, -3/2).
```

Global quota electricity consumptions are `(1, 3/2, 2)`. Cap-and-trade electricity
consumptions are `(3/4, 3/2, 9/4)`. Both sum to `9/2`.

The numerical output will report the utility representation used by the demand
oracle as `own_electricity_component`, separately from the paper-supported ordinal
welfare comparison. It will not claim that this component is a cardinal utility
specified in the paper.
