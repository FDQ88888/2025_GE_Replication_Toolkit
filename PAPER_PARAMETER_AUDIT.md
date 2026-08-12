# Paper Parameter Audit

## Audit Conclusion

Every paper parameter used in Examples 1-6 and the numerical mappings for Theorems 3-4 is traceable to a mathematical ledger, a YAML configuration, and an official source listed in `CITATIONS.md`. No constant was found only inside a solver while being presented as a paper definition. Paper parameters and computational parameters remain separate: the former define the replicated economy, while the latter control search, root finding, deduplication, and numerical comparison.

## Source Map

| Object | Paper source | Paper quantities entering the computation | Configuration and mathematical specification |
|---|---|---|---|
| Example 1 | Main PDF pp. 11-12, journal pp. 367-368; Supplement pp. 11-12, Claims 3.1-3.2 | Commodities, preferences, technology, property-rights accounting, and the demonstration instance `v=0.5` | `configs/paper/example_1.yaml`; `docs/paper_example_1_math.md` |
| Example 2 | Main PDF pp. 12-13, journal pp. 368-369; Supplement pp. 12-14, Claims 3.3-3.4 | Three consumers, two quota-rights regimes, and the demonstration instance `v=3` | `configs/paper/example_2.yaml`; `docs/paper_example_2_math.md` |
| Example 3 | Main PDF pp. 21-24, journal pp. 377-380, Table I; Supplement pp. 13-15 | Demand formulas, price coordinates, Table I value `tau=0.010`, and rounded targets | `configs/paper/example_3.yaml`; `docs/paper_example_3_math.md` |
| Example 4 | Main PDF pp. 24-26, journal pp. 380-382, Claims 5.1-5.3; Supplement pp. 15-17 | Boundary tax rate `0.25`, instances on either side of the boundary, and the paper's theoretical nonexistence label | `configs/paper/example_4.yaml`; `docs/paper_example_4_math.md` |
| Example 5 | Main PDF pp. 26-28, journal pp. 382-384, Tables II-III; inherits Example 3 | 30% reduction target and the tax-rate, reduction, and quota-price targets in the tables | `configs/paper/example_5.yaml`; `docs/paper_example_5_math.md` |
| Example 6 | Main PDF p. 28, journal p. 384; inherits Example 4 | `v_hat=0.5` and supporting tax rate `0.25` | `configs/paper/example_6.yaml`; `docs/paper_example_6_math.md` |
| Theorems 3-4 mapping | Main PDF pp. 20-21, journal pp. 376-377 | Quota-tax mappings and the relation between signed-L1 and numeraire coordinates | `configs/paper/theorem_3_4_mapping.yaml`; Example 1 and the policy documentation |

The values `v=0.5`, `v=3`, the sample points on either side of the boundary, and the boundary-emissions grid are reproducible instances selected from parameter families permitted by the paper. The mathematical ledgers distinguish the paper's general formulas from the instances checked by this project. These values were not adjusted to repair tests.

## Computational Choices

The following are not economic primitives from the paper:

- Initial guesses, multistart seeds, and continuation starts.
- Root brackets, scan bounds, scan-point counts, and maximum evaluations.
- Solver residual-acceptance and root or cluster deduplication tolerances.
- Tolerances used to compare rounded values in paper tables.
- The finite grid used to display a boundary continuum.

These values are stored in YAML under `solver`, `comparison`, or explicitly named computational fields. Their numerical semantics and risks are documented in `TOLERANCE_AUDIT.md`. Changing them may change what is discovered under a specified search protocol, but it must not change the paper model or be interpreted as an analytical existence or completeness claim.

## Unresolved Source Questions

This audit found no unresolved parameter source that affects the current status of Examples 1-6. Other working papers that have not been obtained or confirmed remain listed in `OPEN_QUESTIONS.md` and are not represented as verified theorem implementations.
