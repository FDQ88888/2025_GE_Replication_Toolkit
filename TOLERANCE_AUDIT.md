# Tolerance Audit

## Principle

Numerical tolerances are attached to economic quantities with different units and roles. Solver termination, candidate verification, paper-value comparison, and candidate clustering are not interchangeable. No residual is rounded, clipped, or overwritten to make a candidate pass.

## Core Diagnostic Tolerances

Defaults are defined by `NumericalTolerances` unless noted otherwise.

| Name | Default | Type and scale | Quantity | Main use and rationale |
|---|---:|---|---|---|
| `market_abs_tol` | `1e-10` | absolute term | commodity resource/compliance residual | Combined with `market_rel_tol`; small enough for the normalized finite examples while allowing solver roundoff. |
| `market_rel_tol` | `1e-10` | relative to the maximum relevant allocation/resource/target scale | market residual | Avoids applying one absolute unit to differently scaled commodity coordinates. |
| `budget_tol` | `1e-10` | absolute in the current normalized value coordinate | budget violation and budget exhaustion | Prices are normalized in every verified candidate; both feasibility and equality are reported separately. |
| `feasibility_tol` | `1e-12` | absolute | consumer-set violation | Consumer sets expose a nonnegative violation measure; diagnostics apply this strict boundary tolerance. |
| `optimality_tol` | `1e-10` | absolute in each model's utility representation | `optimal_utility - candidate_utility` | Used only where an explicit utility/demand oracle exists; it is not a bundle-distance tolerance. |
| `normalization_tol` | `1e-12` | absolute | fixed-numeraire or signed-L1 normalization error | Checks the selected coordinate convention without modifying prices. |
| `walras_tol` | `1e-10` | absolute in normalized value units | candidate Walras or policy-adjusted Walras residual | Applied to candidate accounting, never to reoptimized quantities. |
| `production_feasibility_tol` | `1e-10` | absolute violation | production-set membership | Covers ray reconstruction and activity-bound roundoff. |
| `profit_tol` | `1e-10` | absolute in normalized profit units | `optimal_profit - candidate_profit` | Accepts value-level numerical error and does not require candidate and oracle plans to coincide. |
| `ownership_tol` | `1e-12` | absolute | weighted ownership/rebate adding-up | These are dimensionless identities with simple arithmetic. |
| `accounting_tol` | `1e-10` | absolute | cached quantities, quota/tax identities, policy price identity | Detects stale or fabricated candidate caches and policy-accounting drift. |
| `price_sign_tol` | `1e-12` | absolute strict-sign margin | declared positive/negative price coordinates | Separate from normalization and commodity semantics. |
| `approximate_factor` | `100` | multiplicative reporting band | approximate-candidate classification | Does not promote a point to `VERIFIED_CANDIDATE`; it only distinguishes approximate points from generic solver points. |

## Linear-Ray Profit-Margin Zero

`LinearRayTechnology` uses centralized defaults from `core/numerics.py`:

```text
profit_margin_abs_tol = 1e-14
profit_margin_rel_tol = 1e-12
scale = ||p||_2 ||v||_2
effective tolerance = abs_tol + rel_tol * scale
```

For `margin = p dot v`, values above `+tolerance` are positive/unbounded, values below `-tolerance` imply shutdown, and values inside the band are numerical zero. The relative term makes the classification stable under ordinary positive coordinate rescaling; the much smaller absolute term protects near-zero scales. This tolerance is stricter than the general `profit_tol` because it decides the qualitative bounded/unbounded regime.

## Price Coordinates

| Setting | Value | Meaning |
|---|---:|---|
| `FixedNumeraire.tolerance` | `1e-12` | Absolute `np.isclose(..., rtol=0)` check on the fixed coordinate; the input is never silently rewritten. |
| `PriceSignRestrictions.strict_tolerance` | `1e-12` | Required distance from zero for strict `POSITIVE`/`NEGATIVE` signs. |
| signed-L1 zero check | exact zero norm | Structural invalid-input check, not an approximate equilibrium test. |

Positive rescaling preserves signed-L1 prices. `rescale_to_fixed_numeraire` rejects a negative scale because sign reversal is not the same price representation. `PaperTaxConvention` rescales prices and tax rates together.

## Solver and Search Settings

| Name | Default/config value | Role |
|---|---:|---|
| exchange Brent `xtol`, `rtol` | `1e-13` | Scalar root termination for the analytical two-good benchmark. |
| paper quota least-squares `xtol/ftol/gtol` | `1e-13` | Solver termination; success still requires independent diagnostics and paper comparison. |
| Example 3 Brent root tolerance | `1e-13` | Scalar root refinement after a 10,000-point sign-change scan. |
| Example 3 root deduplication | `1e-8` | Distinguishes repeated numerical roots in the scalar `eta` coordinate; now a named solver field/config value. |
| Example 5 system residual acceptance | `1e-9` | Required infinity norm after least-squares termination; named separately from solver termination. |
| Example 5 root deduplication | `1e-7` | Euclidean separation in the two-dimensional `(eta,tau)` search coordinate. |
| multistart terminal residual acceptance | `1e-9` | Configured gate before a solver point may enter independent diagnostics. |
| candidate clustering threshold | `1e-6` | RMS of relative block distances across signed-L1 price, allocations, production, and policy quantities. Only verified candidates are clustered. |

The lower bound `1e-12` in paper quota least-squares price coordinates is a numerical domain floor enforcing strict positivity during optimization, not a paper parameter or an equilibrium tolerance.

## Paper Comparisons

Examples 1-2 and Theorem 3/4 numerical mappings use config-declared absolute and relative comparison tolerances, generally `1e-10`. Examples 3-6 compare against the decimal precision printed in the paper, so their tolerances follow the published rounding unit (for example `0.0005` for three-decimal `eta` and `0.005` percentage points for two-decimal reductions). These paper-rounding tolerances do not replace complete equilibrium diagnostics.

## Operations That Are Not Residual Repair

- `np.maximum` in diagnostics constructs nonnegative violations or scale denominators.
- `np.minimum` in Milestone 11 computes the explicitly reported truncated-mean statistic.
- `round` in reports/tests is used for paper-table display or set comparison only.
- No source implementation uses `np.clip` to alter prices, quantities, or residuals.
