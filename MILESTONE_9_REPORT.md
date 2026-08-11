# Milestone 9: Tax and Quota Correspondence Sweeps

## Verdict

**VERIFIED for the configured grids.** Every grid point combines fresh deterministic
and seeded random starts with continuation starts, then applies independent
diagnostics and verified-only clustering.

## Tax to set of emissions

For Example 3 table-convention tax rates, discovered verified cluster counts are:

```text
tau       0      .004  .008  .010  .012  .020  .038  .040
clusters  3       3     3     3     3     1     1     0
```

Each equilibrium record includes prices, emissions, production, allocations,
individual utilities, profits, tax revenue, residuals, and classification. At
`tau=.040`, the paper status is separately recorded as `NO_EQUILIBRIUM`, while the
numerical status says only `DISCOVERED_0_VERIFIED_CANDIDATE_CLUSTERS`.

The three emissions values at one tax are retained as a set. They are never averaged
and the first branch is not privileged.

## Quota to set of prices

The configured 20%, 30%, and 40% reduction targets each produce three discovered
verified price clusters. Within each target row, all candidates have the same quota
emissions coordinate, while goods-sum quota prices differ. Each record includes
allocations, individual utilities, ownership and quota income, and full residuals.

## Verification

```text
pytest: 93 passed in 1.26s
tax grid points: 8
quota target points: 3
all retained equilibria: VERIFIED_CANDIDATE
```

Result: `results/milestone9_tax_quota_sweeps.json`.

The output wording remains `discovered N verified candidate clusters`; exact branch
counts are not inferred from numerical search.
