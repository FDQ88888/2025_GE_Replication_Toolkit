# Paper Example 3: Mathematical Ledger

## Sources

- Main article PDF pages 21-24 (journal pages 377-380), Example 3 and Table I.
- Supplement PDF pages 13-15, Section 3.3.

## Economy

There are commodities `(0,1,2)` and two agents with `X_i=R_+^3`. Commodity 0 is
regulated and `V=R_- x {0}^2`. Let

```text
r = 2^(8/9) - 2^(1/9).
e_1 = (0.2, 2, r),
e_2 = (0.2, r, 2).
```

There are no firms. Tax revenue is rebated equally. Utilities are

```text
U_1 = x_11 - (1/8)x_21^(-8) - (1/10)x_01^2,
U_2 = x_22 - (1/8)x_12^(-8) - (1/2)x_02^2.
```

## Example-specific price convention

The example sets `p0=-tau` and normalizes `p1+p2=1`. With `eta=p1/p2`,

```text
p_table = (-tau, eta/(1+eta), 1/(1+eta)).
```

This vector has signed L1 norm `1+tau`. Core paper coordinates are therefore

```text
p_L1   = p_table/(1+tau),
t_L1   = tau/(1+tau).
```

All Table I comparisons use `tau`, explicitly labeled `table_goods_sum_tax_rate`.

## Closed-form demands

Supplement Section 3.3 gives

```text
x_01 = 5 tau (1+eta)/eta,
x_02 = tau (1+eta),

I_1 = [2 eta+r]/(1+eta)
      - tau/2 [x_02-x_01],
I_2 = [r eta+2]/(1+eta)
      - tau/2 [x_01-x_02],

x_1 = (x_01,
       I_1/p1-(p2/p1)^(8/9),
       (p1/p2)^(1/9)),

x_2 = (x_02,
       (p2/p1)^(1/9),
       I_2/p2-(p1/p2)^(8/9)).
```

Roots of commodity-1 excess demand determine equilibrium `eta`; rebate Walras law
then gives commodity-2 clearing.

Emissions reduction is

```text
100 * (x_01+x_02)/0.4 percent.
```

## Replication target

The checked Table I row is `tau=0.010`. The paper reports three equilibria:

```text
eta:          2.071, 0.856, 0.578
% reduction: 26.21, 31.75, 38.09
```

These values are rounded. The computation compares rounded output to the table and
also saves unrounded roots, allocations, emissions, and complete diagnostics.
