# Duanmu GE Lab: Final Research Report

## 1. Motivation

Standard computational policy analysis often maps a tax rate to a single emission level and a quota to a single price. The Anderson-Duanmu general-equilibrium framework shows that these relations may instead be multivalued when bads, negative prices, production, and property-right accounting are allowed. The project does not aim to build a black-box carbon-policy calculator. It builds an auditable finite-model laboratory in which every candidate undergoes independent economic diagnostics and numerical evidence is explicitly separated from theoretical conclusions.

## 2. Primary Sources

The primary sources are Anderson and Duanmu (2025), "Cap-and-Trade and Carbon Tax Meet Arrow-Debreu," *Econometrica* 93(2): 357-393, and its official 17-page Supplement. `CITATIONS.md` records local archives, SHA-256 hashes, page locations, and example mappings for both sources. Detailed calculations for Examples 1-4 come from Supplement pp. 11-16; Examples 5-6 come from pp. 382-384 of the article and inherit the preceding economy.

## 3. Mathematical Models

The foundational layer contains finite commodities, consumers, consumption sets, preferences, firms, production sets, ownership shares, and population weights. Under the net-output convention, positive coordinates denote outputs and negative coordinates denote inputs. The pure-exchange resource residual is `sum_i x_i - sum_i omega_i`; for a production economy it is `sum_i x_i - sum_i omega_i - sum_j y_j`. The quota model retains the emission-commodity coordinate rather than creating an additional permit commodity. The emission-tax model explicitly implements the tax rate, net emissions, revenue, and rebates.

## 4. Architecture

The project separates models, candidates, solvers, diagnostics, policy accounting, and experiment runners. `EquilibriumCandidate` carries no equilibrium conclusion. Diagnostics compute the formal resource residual from candidate quantities while independently reoptimizing consumers and firms. Price normalization and sign restrictions, market clearing and Walras law, quota and tax accounting, and population weights and welfare concepts are all represented as distinct objects.

## 5. Milestone History

Milestone 1 established the analytical exchange benchmark. Milestone 1.1 corrected the candidate/reoptimized distinction and added consumption feasibility. Milestones 2-4 added production, dividends, firm diagnostics, population weights, signed prices, and bads. Milestones 5-7 implemented the paper's quota and tax systems and Examples 1-6. Milestones 8-9 added multistart search, clustering, and parameter sweeps. Milestone 10 studied property-right allocations, and Milestone 11 implemented the finite weighted approximation experiment. Unified configuration, reproduction metadata, figures, and artifact auditing completed the toolkit.

## 6. Analytical Benchmarks

The analytical solution of the 2x2 Cobb-Douglas exchange economy is `p=(1,1)`, with both consumers choosing `(1/2,1/2)`. Brent scalar root finding recovers the same solution. At those prices, the incorrect allocation `(0.8,0.2),(0.8,0.2)` produces candidate residual `(0.6,-0.6)` and must be rejected even though reoptimized demand clears. This test fixes the core semantics introduced in Milestone 1.1.

## 7. Production Benchmark

The analytical production benchmark gives `p=(1/3,1)`, firm plan `(-1/2,1/2)`, profit `1/3`, and allocations approximately `(0.625,0.20833)` and `(0.875,0.29167)`. Ownership dividends enter `IncomeBreakdown`; the resource and Walras residuals are zero up to floating-point error, while firm feasibility and the global profit-gap check pass independently.

## 8. Quota Replication

The quota layer implements `m^(j)`, aggregate quota `m`, `Z(m)`, `q=-proj_k(p)`, the government firm, and property-right income. Example 1 at `v=0.5` gives signed-L1 prices `(-0.25,0.25,0.5)` and matches the analytical result component by component. Example 2 fixes aggregate quota `v=3`: global quota and cap-and-trade have identical prices and aggregate consumption, but individual electricity consumptions are `(1,1.5,2)` and `(0.75,1.5,2.25)`, respectively, demonstrating the effect of property-right allocation.

## 9. Emission-Tax Replication

The tax layer implements `proj_k(p)=-t`, aggregate net emissions `C(x,y)`, tax revenue, and `lambda` rebates. `PaperTaxConvention` rescales prices and the tax rate together, preventing direct misuse of the paper's L1-normalized tax rate in numeraire coordinates. The Theorem 3 quota-to-tax and Theorem 4 tax-to-global-quota mappings pass in both directions for Example 1. This is labeled `NUMERICAL_MAPPING_CHECK_SUCCESS`, not a proof.

## 10. Examples 3-6 Status

Examples 3-6 each have a mathematical note, an official-source location, YAML configuration, and regression tests. Example 3 matches three roots and the Table I abatement rates. Example 4 distinguishes the paper's theoretical nonexistence result from a computational precheck. Example 5 reproduces Tables II-III, and Example 6 reproduces the difference between tax and quota target guarantees. Every success concerns the configuration targets of a finite example and is not extrapolated to the paper's full generality.

## 11. Multiple Equilibria

`solve_multistart()` supports theoretical, random, and continuation initial values and retains the starting point, method, status, and reason for every run. Clustering accepts only `VERIFIED_CANDIDATE` results and compares jointly normalized prices, allocations, production, and policy quantities. For Example 3 at a fixed tax rate, 30 runs produce three stable candidate clusters with membership counts 16, 8, and 6. The conclusion is always worded as "three clusters discovered."

## 12. Parameter Sweeps

On the tax-rate grid `[0,.004,.008,.01,.012,.02,.038,.04]`, the numbers of discovered emission candidate clusters are `[3,3,3,3,3,1,1,0]`. Three distinct quota prices are discovered for each of the 20%, 30%, and 40% abatement targets. For example, the goods-sum prices for the 30% target are approximately `0.011448`, `0.009517`, and `0.007583`. Results retain every branch rather than averaging them.

## 13. Welfare Distribution

Milestone 10 fixes the technology, preferences, endowments, aggregate quota, and aggregate emissions of Example 2, varying only quota ownership. It reports each agent's consumption, endowment income, firm dividend, quota income, and total income. Because the paper supplies no cardinal utilities suitable for social aggregation, the project refuses to calculate aggregate welfare or an "optimal carbon policy."

## 14. Finite Weighted Experiments

Milestone 11 explicitly specifies a continuum-type target with `z~Uniform[0,1]` and approximates it using midpoint, equally weighted atoms for `N=10,20,50,100,200`. At all five sizes, prices are `(-1,1)`, weighted aggregate consumption is `(1,2)`, and no bad remains unabsorbed; maximum individual absorption moves from `1.45` to `1.4975`. Tail shares, tail integrals, and truncated means are heuristic diagnostics, not proofs of uniform integrability or measure-theoretic convergence.

## 15. Numerical Diagnostics

Each class of candidate is checked for finite values, consumption and production feasibility, budgets, budget exhaustion, utility and profit gaps, ownership and rebate adding-up, policy constraints, commodity-level resource residuals, and the policy-adjusted Walras residual. The final `results/final_audit.json` audits 15 result files, six figures, and 130 recorded verified-candidate classifications; configuration snapshots and runtime-environment metadata are complete.

## 16. Failures

Numerical failures are retained rather than deleted. At tax rate `0.02`, 11 of 22 searches produce verified candidates; at `0.038`, 19 of 20 do so; at `0.04`, none of 20 finds a candidate. The last case also has the paper-supported status `NO_EQUILIBRIUM`, but zero numerical discoveries alone are not treated as proof. The positive-unit-profit precheck for Example 4 likewise serves only as a cross-check.

## 17. Limitations

The current preference classes are far narrower than the paper's general preferences. Example-specific solvers are not a general GE solver; multistart search does not guarantee branch completeness; there is no general nonexistence certificate; welfare analysis has no social objective across emission levels; finite approximations have no general convergence theorem; and neither nonstandard analysis nor hyperfinite economies are implemented.

## 18. Research Questions Generated by Computation

The computations generate four classes of next questions: how to certify completeness of discovered branches; which parameter changes cause branches to appear or disappear; how quota ownership changes constrained-Pareto rankings under more general preferences; and under which additional conditions finite bad-absorption tail statistics can be linked provably to uniform integrability. See `OPEN_QUESTIONS.md`.

## 19. Suggested Next Work with Professor Duanmu

The most valuable next step is not to accumulate further examples, but to select a provable question with the professor's guidance: certify the branches in Examples 3/5 using analytical elimination or interval methods; select a specific continuum or measure economy and identify the correct convergence target for finite weighted approximations; or, after obtaining the quota-welfare working paper, build a rigorous replication of a welfare proposition for one finite example. The existing code can serve as an experimental foundation for accounting, candidate search, and the generation of counterexample leads.
