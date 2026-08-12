# Milestone 11: Finite Weighted Economies and Bad-Absorption Experiment

## 1. Research Question

This milestone constructs a **paper-inspired finite weighted experiment** to study midpoint discretization of a continuum-type economy, market aggregation with population weights, and tail statistics for the distribution of bad absorption. It is neither a literal replication of an example in Anderson--Duanmu (2025) nor a computational proof involving Loeb measure, hyperfinite economies, or a measure-theoretic convergence theorem.

The continuum-type target has `z ~ Uniform[0,1]`. Each type has endowment `(1,2)`, an upper bound on bad absorption of `0.5+z`, and marginal disutility from the bad of `0.25+0.5z`. At signed prices `p=(-1,1)`, each agent chooses its absorption bound and uses the income associated with the bad's price to purchase the ordinary good. Consequently, weighted aggregate consumption in the continuum target is `(1,2)`, with no unabsorbed bad.

## 2. Finite Approximation

The experiment uses `N = 10, 20, 50, 100, 200` equally weighted atoms, taking the midpoint type in each equal-length interval. Every consumer has population weight `1/N`; endowments, demands, utility summaries, and tail integrals are all aggregated with these weights. For every `N`, the candidate equilibrium is checked by the independent `EquilibriumDiagnostics` rather than declared successful merely from its construction formula.

## 3. Verification Results

All five sizes return `VERIFIED_CANDIDATE`:

| N | Price | Weighted aggregate consumption | Maximum individual absorption | Resource-residual bound |
|---:|:---:|:---:|---:|---:|
| 10 | `(-1,1)` | `(1,2)` | 1.4500 | below `4.45e-16` |
| 20 | `(-1,1)` | `(1,2)` | 1.4750 | below `2.23e-16` |
| 50 | `(-1,1)` | `(1,2)` | 1.4900 | `0` |
| 100 | `(-1,1)` | `(1,2)` | 1.4950 | below `2.23e-16` |
| 200 | `(-1,1)` | `(1,2)` | 1.4975 | below `2.23e-16` |

As the midpoint grid is refined, maximum absorption approaches the continuum supremum `1.5`. The results also report upper-tail population mass, weighted tail integrals, truncated means, and maximum atom mass. These quantities help inspect concentration and discretization behavior; they cannot replace a mathematical proof of uniform integrability.

## 4. Reproduction Entry Point

```powershell
.\.venv\Scripts\python.exe scripts\run_finite_weighted_lab.py --config configs\experiments\finite_weighted_bad_absorption.yaml
```

Machine-readable results are stored in `results/milestone11_finite_weighted_lab.json`, and regression tests are in `tests/test_finite_weighted_lab.py`.

## 5. Scope of the Conclusion

This experiment supports the following finite-dimensional conclusions: population weights enter every aggregate; a negative-price bad can have a finite optimum under an explicit upper bound in the consumption set; and midpoint discretization preserves aggregate resource clearing exactly in this linear construction. It does not support stronger claims that equilibrium existence has been proved for a continuum economy, that a hyperfinite method has been implemented, or that finite results automatically extend to a general type space.
