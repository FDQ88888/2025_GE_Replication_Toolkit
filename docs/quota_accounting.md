# Quota Accounting and Diagnostics

## Paper convention

`QuotaPolicy` implements Definitions 3.2-3.5 of Anderson and Duanmu (2025). The
first `k` coordinates of the existing commodity vector are regulated. The policy
does not add a permit commodity.

For every firm `j`, the configured vector `m^(j) <= 0` is the negative of its quota:

```text
m = sum_j m^(j),
q = -proj_k(p),
pi_j^m = p dot y_j + proj_k(p) dot m^(j).
```

The government firm has `Y_0={0}`. Its production revenue is zero, while its quota
profit can be nonzero. Government revenue reaches consumers through ownership of
the government firm, exactly as in the paper.

## Single accounting source

`QuotaEconomy.firm_profit_breakdowns` computes operating and quota-right profits.
`QuotaEconomy.income_breakdowns` then distributes both components through the same
firm ownership objects used by diagnostics:

```text
endowment_income      = p dot e_i,
firm_dividend_income  = sum_j theta_ij (p dot y_j),
policy_income         = sum_j theta_ij (proj_k(p) dot m^(j)),
total_income          = their exact sum.
```

Consumer demand and candidate budget diagnostics call this method. There is no
second quota-income formula in `Consumer` or the diagnostics module.

For finite weighted economies, ownership adding-up remains
`sum_i population_weight_i * theta_ij = 1`. Population mass is not a welfare
weight.

## Compliance

Candidate resource accounting always starts from authoritative candidate
coordinates:

```text
r(x,y) = sum_i lambda_i x_i - sum_i lambda_i e_i - sum_j y_j.
```

Membership in `Z(m)` requires:

- `r_1:k = m` on regulated coordinates;
- `r_l = 0` on exact-clearing unregulated coordinates;
- `r_l <= 0` on free-disposal unregulated coordinates.

The solver-cached residual is never substituted for this recomputation.

## Quota-adjusted Walras identity

Because quota value is distributed as income, raw `p dot r` generally is not zero.
The diagnostic identity is

```text
p dot r - proj_k(p) dot m = 0.
```

Both terms are reported separately. Treating raw `p dot r=0` as the policy Walras
law would incorrectly reject valid quota equilibria with valuable quota rights.

## Strict failure behavior

An unbounded linear production ray has no finite profit maximizer when its unit
margin is positive, however small. `LinearRayTechnology` raises
`UnboundedProfitError`; diagnostics do not clip the margin or silently call the
candidate optimal. The Example 2 solver therefore projects its price estimate onto
the two zero-margin equations and the signed-L1 equation before verification.

`PAPER_REPLICATION_SUCCESS` requires both:

1. independent equilibrium diagnostics classify the candidate as
   `VERIFIED_CANDIDATE`;
2. every reported analytical coordinate and accounting field passes absolute and
   relative comparison tolerances.
