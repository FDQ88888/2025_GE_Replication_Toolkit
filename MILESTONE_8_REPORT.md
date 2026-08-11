# Milestone 8: Multistart and Verified-Candidate Clustering

## Verdict

**VERIFIED.** The generic multistart engine retains deterministic, seeded random,
and continuation attempts, including failures. Clustering accepts only candidates
classified `VERIFIED_CANDIDATE`.

## Example 3 experiment

At Table-I tax rate `tau=0.010`, the run combined:

- 3 deterministic theoretical starts;
- 24 random starts with explicit seed `20250810`;
- 3 continuation starts from verified roots at `tau=0.008`.

All 30 attempts happened to verify. The economic-block distance clustered them as:

| Cluster | Members | `eta` | Emissions | Reduction |
|---:|---:|---:|---:|---:|
| 0 | 16 | 2.0711660937 | 0.2951473490 | 26.2132% |
| 1 | 8 | 0.8556519119 | 0.2730085036 | 31.7479% |
| 2 | 6 | 0.5775837140 | 0.2476566251 | 38.0858% |

Maximum within-cluster representative distance was below `7.6e-10`, against a
configured threshold `1e-6`.

The formal output language is:

> discovered 3 verified candidate clusters

It does not infer an exact equilibrium count from multistart. The paper supplies the
analytical count for this parameter.

## Distance and filtering

Candidate distance jointly uses:

- prices converted to signed-L1;
- consumer allocations;
- firm production plans;
- policy quantities (emissions and tax revenue in this experiment).

Each block is scaled by the larger of one and the two block norms before root-mean-
square aggregation. Solver points and approximate candidates are excluded from
clustering.

## Verification

```text
pytest: 90 passed in 0.72s
multistart status: MULTISTART_CLUSTERING_SUCCESS
total attempts: 30
verified attempts: 30
discovered verified clusters: 3
```

Result: `results/milestone8_example3_multistart.json`.
