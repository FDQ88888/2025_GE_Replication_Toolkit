# Milestone 6 Emission Tax Report

## Verdict

**VERIFIED.** `EmissionTaxPolicy`, candidate-dependent tax accounting, signed tax
coordinate conversion, and the bidirectional Theorem 3/4 numerical check pass.

This is a **NUMERICAL CHECK OF THEORETICAL MAPPING**, not a proof of Theorem 3 or
Theorem 4.

## Source basis

- Definition 4.1, Remark 4.2, and Definition 4.3: main article PDF pages 19-20
  (journal pages 375-376).
- Theorem 3 and Theorem 4: main article PDF pages 20-21 (journal pages 376-377).
- Rebate Walras Law: Supplement PDF pages 3-6.

## Implemented accounting

For candidate resource residual `r=sum x-sum e-sum y`, the policy computes

```text
proj_k(p) = -t
C(x,y)    = -proj_k(r)
tax       = t dot C(x,y)
rebate_i  = lambda_i tax
```

Consumer budgets and diagnostics both call
`EmissionTaxEconomy.income_breakdowns`; no duplicate rebate formula exists in the
consumer object. The regulated coordinates of `V` permit `r<=0`, while each
unregulated coordinate explicitly selects exact clearing or free disposal.

The tax diagnostic reports and verifies

```text
p dot r - t dot C(x,y) = 0.
```

## Theorem 3 check

The source is the verified Example 1 global-quota candidate with `v=1/2`. The
mapped tax economy removes the government firm and obtains

```text
p      = (-1/4, 1/4, 1/2)
t      = 1/4
C      = 1/2
tax    = 1/8
lambda = (0,1)
```

The allocation, private production, and consumer incomes are unchanged. The mapped
tax candidate is `VERIFIED_CANDIDATE`, and its rebate-adjusted Walras residual is
zero.

## Theorem 4 check

The reverse mapping adds a government firm with `Y_0={0}`, gives its ownership
shares `(0,1)`, and assigns it `m=-C=-1/2`. The resulting global-quota candidate is
also `VERIFIED_CANDIDATE` and matches the source allocation, price, production, and
income accounting.

## Tax-coordinate gate

`PaperTaxConvention` always rescales `(p,t)` together. With electricity fixed as
numeraire one, the positive scale is two:

```text
paper:    p=(-1/4,1/4,1/2), t=1/4
internal: p=(-1/2,1/2,1),   t=1/2
```

Demand and physical equilibrium quantities are invariant. Nominal incomes, firm
profits, expenditure, and tax revenue scale by two, so scale-adjusted accounting
values are identical. A price-only rescaling is explicitly rejected.

## Verification

```text
pytest: 73 passed in 0.75s
Theorem 3 tax candidate: VERIFIED_CANDIDATE
Theorem 4 reverse quota candidate: VERIFIED_CANDIDATE
mapping status: NUMERICAL_MAPPING_CHECK_SUCCESS
```

Result: `results/milestone6_theorem_3_4_mapping.json`.

## Scope boundary

This milestone does not prove the theorems and does not yet reproduce Examples
3-6. It validates the policy accounting and one finite paper-defined mapping at a
verified candidate.
