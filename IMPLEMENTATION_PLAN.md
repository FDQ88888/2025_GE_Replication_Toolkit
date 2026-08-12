# Duanmu GE Lab - Implementation Plan

> Status: Historical first-round implementation roadmap, created 2026-08-09. Milestones 1-11 were implemented and passed the final audit on 2026-08-10. See `REPORT.md`, `FINAL_AUDIT.md`, and `OPEN_QUESTIONS.md` for current completion status, limitations, and future directions. This file is retained to trace the original design constraints.

## 1. Project Objective and Boundaries

`Duanmu GE Lab` aims to build an auditable finite-dimensional general-equilibrium research toolkit that can:

- replicate the quota and emission-tax examples in Anderson-Duanmu (2025);
- study finite weighted economies with production, bads, comprehensive externalities, exact market clearing, and potentially negative prices;
- search for and distinguish multiple equilibrium branches;
- compare quota-right allocations, tax rebates, emission levels, prices, and welfare distributions;
- provide an experimental framework for future research on how finite economies approximate measure economies.

Outside the current scope: SAM, GTAP, input-output calibration, representative-household macro CGE, dynamic integrated climate assessment, deep learning, GPUs, web frontends, databases, and cloud deployment.

## 2. Three-Layer Output Structure

### 2.1 Paper Replication

This layer implements only economic objects and examples defined in the original paper. Every parameter, formula, and expected result cites a specific page, definition, theorem, or supplementary source.

Preferred replication order:

1. **Example 1**: a three-good quota economy with two agents and one private firm. Its unique analytical equilibrium in the article provides an end-to-end check of signs, budgets, and market clearing.
2. **Example 2**: vary the allocation of quota rights between government and private firms to test how prices may remain unchanged while consumption and welfare distributions change.
3. **Examples 3-4**: multiple emission-tax equilibria at one tax rate and no equilibrium at certain rates.
4. **Examples 5-6**: multiple quota prices for one quota and nonuniqueness of quota/tax mappings.

Computational details unsupported by the article must await the Supplementary Material rather than be filled in speculatively.

### 2.2 General Toolkit

The general layer abstracts finite consumers, finite firms, production technologies, externalities, policies, and diagnostics. It permits computational choices beyond the paper's examples, but outputs must label them `OUR COMPUTATIONAL CHOICE`.

### 2.3 Future Extensions

- finite weighted consumers;
- population discretization and sample-size sweeps;
- parameter continuation and equilibrium-branch tracking;
- numerical diagnostics related to assumptions in measure economies, such as bad-absorption bounds and empirical uniform-integrability indicators;
- the quota welfare theorem from unpublished work, in a separate milestone after the manuscript is obtained.

These extensions do not enter the MVP or alter the mathematical definitions in the paper-replication layer.

## 3. Development Gates

### Gate 0: Freeze Research Definitions

Core coding may begin only after:

- the mapping of paper objects in `RESEARCH_NOTES.md` has been reviewed manually;
- `BLOCKING` items in `OPEN_QUESTIONS.md` have been resolved or assigned an explicit conservative choice;
- the Econometrica Supplementary Material has been obtained, or the first stage has been explicitly limited to Examples 1-2, for which the article contains sufficient information;
- the initial price normalization and tax-rate scale have been selected;
- the commodity-level configuration of exact clearing versus free disposal has been selected;
- the utility and production-technology representations for the first MVP have been selected.

### Gate 1: Mathematical Specification Tests

Every implemented object first receives a one-page mathematical specification containing at least:

- its mathematical definition;
- dimensions and sign conventions;
- inputs and outputs;
- assumptions and infeasible states;
- sources;
- a minimal test with an analytical answer.

### Gate 2: Separate Solver and Validator

A solver may only generate an `EquilibriumCandidate`; independent `EquilibriumDiagnostics` determine whether it meets reporting standards. They must not share a cached boolean asserting that optimality holds.

## 4. Proposed MVP Mathematical Model

The MVP is a finite, static, deterministic Arrow-Debreu production economy:

- `I` heterogeneous consumers, optionally with population weights `lambda_i > 0` summing to one;
- `J` firms;
- `L` commodities, with good, bad, and regulated as mutually independent semantic attributes;
- consumption and production sets defined by explicit constraints;
- externalities computed by an independent `ExternalityModel(x,y,p)`;
- prices that may be negative, zero, or positive;
- exact clearing or a free-disposal inequality specified separately for every commodity;
- policy represented by `NoRegulation`, `QuotaPolicy`, or `EmissionTaxPolicy`;
- static competitive equilibrium jointly defined by consumer optimality, firm optimality, resource/compliance conditions, and price normalization.

The MVP does not directly represent the incomplete or intransitive preferences permitted by the paper. Its first computational version represents preferences with continuous utility functions. This is **OUR COMPUTATIONAL CHOICE**; the interface remains named `PreferenceModel` to avoid confusing utility representation with the paper's general definition.

## 5. Variables, Parameters, and Normalization

### 5.1 Endogenous Variables

| Variable | Meaning | Note |
|---|---|---|
| `x_i in R_+^L` | Consumer allocation | Must belong to `X_i` |
| `y_j in R^L` | Firm net production | Must belong to `Y_j` |
| `p in R^L` | Commodity prices | May be signed; must be normalized |
| `s` or multipliers | Inequality slack/optimality certificates | Added explicitly only in a KKT/MCP formulation |
| `externality_state` | Emissions or comprehensive externality | Recomputed from candidate `(x,y,p)`, not an arbitrary free variable |

### 5.2 Exogenous Policy Parameters

- Quota: aggregate quota, firm quota rights, government-firm quota, and compliance regions for unregulated commodities.
- Emission tax: tax-rate vector `t`, rebate vector `lambda`, and compliance region.
- No regulation: commodity-level clearing/disposal rules.

### 5.3 Candidate Price Normalizations

The first choice is the paper-consistent signed `L1` normalization:

```text
sum_l |p_l| = 1.
```

Its numerical implementation cannot simply pass an absolute-value equation to a smooth root solver. Options include:

1. fix a nonzero coordinate as numeraire and convert back to the paper's `L1` normalization in diagnostics;
2. enumerate price-sign regions and linearize `|p_l|` within each region;
3. use optimization or complementarity methods with nonsmooth constraints;
4. fix the known sign pattern of a paper example, only for paper replication.

MVP recommendation: use the paper's known price-sign patterns to test Examples 1-2. In the general engine, use a fixed nonzero numeraire plus explicit sign restrictions, retaining a conversion function for the `L1` convention. Normalization is then a coordinate choice, while the economic model specifies sign restrictions separately.

The emission-tax model additionally requires `proj_k(p)=-t`. Under `L1` normalization, `t` is a relative price rather than an arbitrary dimensional tax amount; tax-rate sweeps must record normalization and units.

## 6. Numerical Representation of Equilibrium Conditions

### 6.1 Equalities

- Resource residual equals zero for commodities assigned exact clearing.
- Aggregate net emissions exactly equal the aggregate quota for regulated commodities in the quota model.
- Price normalization.
- Regulated price coordinates equal `-t` in the emission-tax model.
- Policy-revenue conservation: government revenue from quota sales or taxation equals aggregate rebates.

### 6.2 Inequalities

- consumption-set, production-set, and nonnegativity constraints;
- consumer budget `p*x_i <= income_i`;
- resource residual in `R_<=0` for commodities permitting free disposal;
- coordinate-wise inequalities in quota/tax compliance regions.

Budget equality should be a derived check only where conditions such as local nonsatiation genuinely guarantee it; it must not be imposed unconditionally.

### 6.3 Optimality and Complementarity

Three implementation levels are available:

1. **Analytical best responses**: preferred for paper examples and analytically solvable benchmarks.
2. **Nested optimization plus market root finding**: solve consumer demand and firm supply at given prices and external states, then solve for zero market residuals.
3. **Unified KKT/MCP**: use only when utility, production, and constraints satisfy appropriate convexity and differentiability conditions. KKT conditions are not sufficient for arbitrary nonconvex problems.

The first version does not depend on a proprietary MCP solver. Prefer `scipy.optimize.root`, `least_squares`, and `minimize`; use `cvxpy` only for consumer or firm subproblems that are genuinely convex.

## 7. Division Between Analytical and Numerical Methods

### 7.1 Material That Must Be Derived First

- consumption, production, price, and welfare formulas for paper Example 1;
- how government/private quota ownership enters profit and budgets;
- aggregate tax rebates and Walras-type accounting identities;
- transformations between normalizations;
- firm-supply boundaries under simple linear technologies.

### 7.2 Responsibilities of Numerical Methods

- nonlinear demand and supply;
- simultaneous clearing of multiple markets;
- multistart discovery of multiple candidates;
- policy-parameter sweeps and branch continuation;
- finite population-weight and size experiments.

Numerical methods do not prove general existence, uniqueness, or convergence of measure economies.

## 8. EquilibriumCandidate Verification Protocol

A result may be labeled `verified_candidate` only after all of the following independent checks pass:

1. **Domain**: every variable is finite and has the correct dimension; consumption and production belong to their feasible sets.
2. **Price normalization**: normalization error is below tolerance; sign restrictions are checked independently.
3. **Consumer budget**: each consumer's expenditure does not exceed income recomputed from the candidate.
4. **Consumer optimality**: independent optimization or analytical best response, reporting a utility gap or revealed-preference violation.
5. **Firm optimality**: recomputed maximum profit and reported profit gap.
6. **Market/compliance**: commodity-level exact residuals, free-disposal slack, quota residuals, or tax-compliance residuals.
7. **Policy accounting**: itemized reconciliation of firm quota income, government quota income, tax revenue, rebates, and ownership distributions.
8. **Walras law**: report the value-aggregate residual as a diagnostic, never as a substitute for commodity-level clearing.
9. **Complementarity**: check product residuals only for complementarity relations actually present in the model.
10. **Externality consistency**: recompute the externality state from `(x,y,p)` and match the state used in preference calculations.

Suggested levels:

- `verified_candidate`: all hard constraints and optimality gaps satisfy strict tolerances;
- `approximate_candidate`: feasible, but one or more gaps meet only relaxed tolerances;
- `solver_point`: returned by a solver but not independently verified;
- `failed_run`: no reportable candidate; retain the reason and initial value.

## 9. Multiple-Equilibrium Search Protocol

1. Use deterministic grids, random seeds, and theoretically derived starting points.
2. Solve independently from every start and store a solver-log summary.
3. Cluster and deduplicate only candidates that pass diagnostics.
4. Compute clustering distance on normalized `(p,x,y)`, not on prices or emissions alone.
5. Record basin size without interpreting start-hit frequency as an equilibrium-selection probability.
6. Prefer continuation for policy sweeps: initialize the next parameter value from every branch at the previous value, while adding independent fresh starts to reduce missed branches.
7. Report "N candidates discovered under this search protocol," not "there are N equilibria," absent an analytical proof.

## 10. Anticipated Directory Structure (Created Only in Round Two)

```text
duanmu_ge_lab/
  README.md
  pyproject.toml
  src/duanmu_ge_lab/
    core/
      commodity.py
      consumer.py
      firm.py
      economy.py
    preferences/
    technologies/
    externalities/
    policies/
      base.py
      no_regulation.py
      quota.py
      emission_tax.py
    equilibrium/
      system.py
      candidate.py
      diagnostics.py
    solvers/
    experiments/
  configs/
  scripts/run_experiment.py
  tests/
  results/
  docs/
```

This was only a plan; no empty skeleton was to be created in round one, lest directory structure dictate the design before the mathematical objects were frozen.

## 11. Milestones and Acceptance Criteria

### Milestone 0 - Research

Deliver the three Markdown files from round one. Sources, definitions, open questions, and development gates must be clear; no core code.

### Milestone 1 - Minimal GE Engine

Implement a finite economy with no production or minimal linear production, price normalization, commodity-level clearing, diagnostics, and at least one analytical equilibrium test.

### Milestone 2 - Production

Add general `ProductionTechnology`, profit maximization, firm ownership, and dividends. Verify profit and budget accounting.

### Milestone 3 - Weighted Economies

Add consumer population weights; aggregate consumption, endowment, and welfare use one consistent weight convention. Test the invariance that splitting a consumer does not change the aggregate economy.

### Milestone 4 - Bads and Exact Clearing

Allow negative prices, bad-absorption bounds, production byproducts, and non-free-disposal. Add a Hara-style stress test, explicitly as a finite-economy experiment.

### Milestone 5 - Quota

Implement the government firm, firm quota rights, `Z(m)`, quota profit, and compliance diagnostics. Accept against the analytical solution of Example 1.

### Milestone 6 - Emission Tax

Implement the tax-rate-fixed price coordinate, aggregate emissions, government revenue, and rebates. Test with the quota-to-tax accounting identity.

### Milestone 7 - Paper Replication

Replicate Examples 1-2 and, after obtaining the Supplement, Examples 3-6. Report parameters, formulas, tolerances, figures, and sources of deviation.

### Milestone 8 - Multi-equilibrium Search

Implement multistart, deduplication, branch labels, and failure records; accept on a known multiple-equilibrium example.

### Milestone 9 - Policy Sweeps

Sweep quotas and tax rates continuously, retaining branches, emissions, prices, and regions where candidates exist. A single polyline must not hide a multivalued relation.

### Milestone 10 - Welfare Distribution

Compare effects of quota rights and rebate rules on individual utilities, weighted welfare, and distribution. Strictly distinguish constrained Pareto from full Pareto.

### Milestone 11 - Finite Approximation

Add population-size and weight experiments, reporting tails of bad consumption, maximum individual shares, empirical uniform-integrability indicators, and equilibrium residuals. Conclusions remain limited to numerical evidence.

Every milestone must deliver automated tests, one end-to-end experiment, an independent diagnostic summary, failed-experiment records, and source documentation.

## 12. Technology Stack and Coding Standards

- Python 3.11+;
- `numpy`, `scipy`, `pandas`, `matplotlib`, `pyyaml`, and `pytest`;
- add `cvxpy` only where a convex subproblem genuinely benefits;
- dataclasses, type annotations, short functions, and explicit inputs and outputs;
- mathematical-core docstrings must state economic meaning, mathematical definition, parameters, return values, and source;
- use YAML configuration, targeting this execution interface:

```text
python scripts/run_experiment.py --config configs/example.yaml
```

Each experiment stores a configuration snapshot, code-version information, random seed, solver settings, candidates, and diagnostics. Parameters must not be fabricated, and failed results must not be deleted.

## 13. Recommended Scope of the First Coding Round

After Gate 0, round two was to implement only the minimal closed loop of Milestone 1:

1. mathematical objects and data validation;
2. a signed-price normalization interface;
3. one analytical finite-GE benchmark;
4. `EquilibriumCandidate` and independent `EquilibriumDiagnostics`;
5. pytest and concise research output.

Quota and emission tax were not to be completed together in the same round. Each policy module would therefore rest on already validated resource accounting, consumer/firm optimality, and price handling.
