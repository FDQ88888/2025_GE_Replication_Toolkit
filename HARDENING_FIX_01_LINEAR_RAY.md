# Hardening Fix 01: Linear-Ray Zero Profit

## Defect

Before hardening, `LinearRayTechnology.optimal_plan()` used the strict floating-point branch `margin > 0.0`, where `margin = p dot v`. A theoretical zero-profit ray could therefore be classified as unbounded if a BLAS/NumPy evaluation returned a tiny positive value such as `5e-17`.

The generic firm oracle also compared every candidate plan with the arbitrary shutdown plan. At theoretical zero margin every feasible activity is optimal, so plan equality is not an appropriate optimality condition.

## Mathematical Fix

The new sign assessment uses

```text
scale = ||p||_2 ||v||_2
tol = 1e-14 + 1e-12 * scale
```

and classifies the unit margin as `NEGATIVE_SHUTDOWN`, `NUMERICAL_ZERO`, or `POSITIVE_UNBOUNDED`. In the numerical-zero regime, a feasible candidate plan is used as its own value-level optimality witness, giving a zero profit gap without requiring equality to an arbitrary optimizer plan.

No margin is rounded, clipped, overwritten, or treated specially by paper example number.

## Regression Tests

The actual `LinearRayTechnology` API is tested for:

- exact zero margin;
- `+5e-17` and `-5e-17` numerical margins;
- a clearly positive `1e-3` margin raising `UnboundedProfitError`;
- a clearly negative margin returning shutdown;
- stable classification under positive price/vector rescaling;
- acceptance of a nonzero feasible activity as optimal at zero margin.

## Paper Revalidation

After the fix, Examples 1-6 and the Theorem 3/4 mapping were rerun from their YAML configurations. All returned their required success status. Recorded assessments include:

| Case | Raw margin | L2 scale | Effective tolerance | Regime |
|---|---:|---:|---:|---|
| Example 1, firm 1 | `0` | `1.0606601717798212` | `1.0706601717798211e-12` | `NUMERICAL_ZERO` |
| Example 2, firm 1 | `0` | `1.0606601717798212` | `1.0706601717798211e-12` | `NUMERICAL_ZERO` |
| Example 2, firm 2 | `0` | `1.3693063937629153` | `1.3793063937629153e-12` | `NUMERICAL_ZERO` |
| Theorem 3 tax mapping, firm 1 | `0` | `1.0606601717798212` | `1.0706601717798211e-12` | `NUMERICAL_ZERO` |
| Theorem 4 reverse mapping, firm 1 | `0` | `1.0606601717798212` | `1.0706601717798211e-12` | `NUMERICAL_ZERO` |

The current environment happened to compute these paper margins as exact zeros, so the old bug did not trigger locally. The new regression tests reproduce the cross-environment perturbation directly.

## Numerical Preservation

The post-fix Examples 1-6 and mapping JSON were compared with the pre-hardening snapshot. Excluding timestamps, runtime metadata, and the intentionally changed arbitrary `optimal_plan` witness, the maximum common numerical difference was `0.0` for every paper result file. No paper parameter, analytical target, solver start, or comparison tolerance was changed to recover a match.
