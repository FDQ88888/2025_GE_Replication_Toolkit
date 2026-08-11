# Scope and Limitations

## What the package is

`Duanmu GE Lab` is a reproducible paper-replication, equilibrium-search, and independent numerical-diagnostics framework for a family of **finite** general-equilibrium models related to Anderson and Duanmu's quota and emission-tax research.

Its strongest supported uses are:

- analytical software-validation benchmarks for finite exchange and production economies;
- finite weighted aggregation with explicit population masses;
- signed-price and bad-absorption accounting under declared consumption sets;
- paper-specific implementations of Anderson-Duanmu Examples 1-6;
- quota and emission-tax accounting with independent candidate diagnostics;
- multistart searches, candidate clustering, and parameter sweeps that retain all discovered verified branches;
- reproducible result and figure generation from declared YAML experiment parameters.

The baseline exchange solver is deliberately limited to two goods and one independent price after fixing a numeraire. Paper-example solvers encode model-specific reductions and equations. These limitations are intentional and documented, not hidden generality.

## What the package is not

The project is not:

- a universal or arbitrary-dimensional general-equilibrium solver;
- an automatic compiler from a mathematical model or YAML file to equilibrium equations;
- a general solver for incomplete, non-transitive, or comprehensive-externality preferences;
- a full comprehensive-externality engine accepting utilities that depend on every allocation, production plan, and price;
- a measure-theoretic economy solver;
- an implementation of Loeb measure, hyperfinite economies, or nonstandard analysis;
- a proof assistant for existence, nonexistence, uniqueness, or convergence;
- a social-planner or optimal-carbon-policy package.

## Numerical claim boundary

`VERIFIED_CANDIDATE` means that a finite candidate passed the implemented feasibility, optimality, accounting, normalization, and policy diagnostics at the recorded tolerances. It does not prove that an equilibrium exists in a broader model or that all equilibria have been found.

`DISCOVERED_N_VERIFIED_CANDIDATE_CLUSTERS` reports a search result under explicit starts, continuation rules, and clustering tolerances. It does not mean that exactly `N` equilibria exist.

The finite weighted experiment in Milestone 11 is a construction-specific finite-grid stability exercise. Its nearly constant aggregates follow from the midpoint-linear benchmark structure. Tail statistics are heuristic diagnostics and do not establish uniform integrability or continuum convergence.

## Configuration boundary

YAML files drive exposed experiment parameters such as taxes, quotas, ownership regimes, initial guesses, grids, population sizes, random seeds, and solver settings. The mathematical structure of each paper example still lives in model-specific Python builders and solvers. A new finite model therefore requires an explicit mathematical translation and cannot be supplied as arbitrary YAML alone.
