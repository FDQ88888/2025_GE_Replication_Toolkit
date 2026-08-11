# Milestone 7: Paper Examples 3-6

## Verdict

**VERIFIED for the configured replication targets.** All four scripts return
`PAPER_REPLICATION_SUCCESS`; every saved candidate is independently verified.

## Example 3

For the Table I row `tau=0.010` under the paper's `p1+p2=1` convention, the scalar
Supplement equation yields three verified branches:

| Branch | `p1/p2` | Reduction |
|---:|---:|---:|
| 1 | 2.0711660937 | 26.21316274% |
| 2 | 0.8556519114 | 31.74787410% |
| 3 | 0.5775837140 | 38.08584374% |

Rounded values match Table I `(2.071,0.856,0.578)` and
`(26.21,31.75,38.09)`. Prices and tax rates are jointly converted to signed-L1
before core diagnostics.

Result: `results/milestone7_paper_example_3.json`.

## Example 4

- At `t=0.20<1/4`, the verified candidate emits one unit.
- At `t=1/4`, five sampled points `v=(0,.25,.5,.75,1)` from the paper's continuum
  are all verified.
- At `t=0.30>1/4`, metadata records the paper status `NO_EQUILIBRIUM` separately
  from the computational precheck. The precheck obtains firm 2 unit margin `0.1>0`
  under the necessary price equations, hence unbounded profit.

The no-equilibrium claim is sourced to Claim 5.1 and its Supplement proof, not to a
failed numerical search.

Result: `results/milestone7_paper_example_4.json`.

## Example 5

Solving market clearing jointly with a 30 percent reduction target recovers the
three Table III goods-sum quota prices:

```text
0.0114479939
0.0095170442
0.0075832159
```

Each corresponding global-quota candidate emits exactly `0.28`. At each tax rate,
the Example 3 scalar solver also retains all three tax equilibria and reproduces
Table II's distinct reductions. Thus tax fixes price but not emissions; quota fixes
emissions but not the equilibrium quota price.

Result: `results/milestone7_paper_example_5.json`.

## Example 6

For desired emissions `v_hat=1/2`, the `t=1/4` tax branch and its Theorem 4 global
quota mapping are both verified. The same tax rate supports every `v in [0,1]`,
while the quota candidate's compliance coordinate is exactly `m=-1/2`.

Result: `results/milestone7_paper_example_6.json`.

## Verification

```text
pytest: 86 passed in 0.72s
Example 3: 3 verified candidate branches
Example 4: 1 below-boundary + 5 boundary candidates verified
Example 5: 3 tax target + 3 quota target branches verified
Example 6: tax and quota candidates verified
```

## Scope

Root scanning discovers sign-changing roots in a configured interval. Numerical
output says `discovered verified candidate branches`; exact equilibrium counts and
nonexistence statements are attributed to the paper. General multistart, clustering,
and continuation are the next milestone.
