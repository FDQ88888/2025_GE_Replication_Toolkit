# Emission Tax Accounting Specification

## Primary definitions

This specification follows Anderson and Duanmu (2025), main article PDF pages
19-20, Definition 4.1, Remark 4.2, and Definition 4.3. Theorem 3 and Theorem 4 are
on PDF pages 20-21.

An emission tax economy contains only private firms. For the first `k` regulated
commodity coordinates:

```text
proj_k(p) = -t.
```

The paper price vector is signed-L1 normalized. Thus `t` is a normalized relative
price, not an invariant currency amount.

For candidate allocation and production coordinates, define

```text
r(x,y) = sum_i lambda_population_i x_i
         - sum_i lambda_population_i e_i
         - sum_j y_j,

C(x,y) = -proj_k(r(x,y)).
```

The tax compliance region requires `r_l<=0` on regulated coordinates. Its
unregulated coordinates are configured for exact clearing or free disposal.

Tax revenue and consumer income are

```text
T(x,y) = t dot C(x,y),

I_i = p dot e_i
      + sum_j theta_ij (p dot y_j)
      + rebate_share_i T(x,y).
```

Population-weighted rebate shares add to one. The policy layer is the sole source
of `C`, `T`, and the rebate component used by both demand and diagnostics.

## Rebate-adjusted Walras identity

Aggregate consumer budgets imply

```text
p dot r(x,y) - t dot C(x,y) = 0.
```

Because `proj_k(p)=-t` and `C=-proj_k(r)`, the regulated-coordinate part supplies
the tax revenue term. Raw `p dot r` is not generally zero.

## Price-coordinate conversion

Let paper coordinates be `(p,t)` with `sum_l |p_l|=1`. Converting to a fixed
numeraire uses one positive scale `s`:

```text
p_internal = s p,
t_internal = s t.
```

Scaling only prices would break `proj_k(p)=-t`. Scaling both preserves budget sets,
firm argmax sets, candidate quantities, compliance, and all zero residuals. Nominal
income, profit, tax revenue, and expenditure scale by `s`; scale-adjusted values are
identical.

Conversion back to paper coordinates divides both vectors by
`sum_l |p_internal,l|`. Negative or zero scales are rejected.

## Computational Theorem 3/4 check

For a verified quota candidate, the Theorem 3 mapping uses

```text
t = -proj_k(p),

rebate_share_i =
    [sum_j theta_ij proj_k(p) dot m^(j)]
    / [proj_k(p) dot m].
```

With one regulated commodity this reduces to

```text
rebate_share_i = [sum_j theta_ij m^(j)] / m.
```

The government firm is removed. In the reverse Theorem 4 mapping, a government
firm with `Y_0={0}` is added, its ownership equals the rebate shares, and all quota
rights `m=-C` are assigned to it.

The implemented experiment is a `NUMERICAL CHECK OF THEORETICAL MAPPING`. It is
not a proof of either theorem.
