# Collaborator Guide

## Information Required for a New Finite Model

A theoretical researcher should first provide:

1. The commodities and the economic meaning of each coordinate, including goods, bads, and price-sign restrictions.
2. The consumer set, endowments, consumption sets, preferences, or computable choice rules.
3. Firms, production sets, ownership shares, and profit-distribution rules.
4. Exact accounting identities for quotas, taxes, rebates, or other policies.
5. The price normalization and the conversion between numeraire and paper coordinates.
6. The resource, budget, optimality, and complementarity conditions that a candidate must satisfy.
7. Known analytical solutions, theoretical boundaries, counterexamples, or table values, with precise sources.
8. Justification for the search region, initial-value information, and acceptable numerical errors.

## Integration Procedure

First translate the model into a finite structure expressible by the existing core and policy objects. If its mathematical structure differs, implement the smallest paper-specific builder, candidate solver, and diagnostic layer required. Keep paper parameters separate from computational parameters in YAML, add analytical or high-precision benchmark tests, register exact success and failure statuses, and include the experiment in the reproducibility suite.

New results must retain failed runs, record random seeds and search protocols, and use the candidate's own quantities for resource and policy accounting. Reoptimized quantities are used only to compare utility or profit gaps.

## Current Boundary

The package does not generate an equilibrium solver from an arbitrary mathematical description or arbitrary YAML. A new model still requires model-specific mathematical translation. Models involving incomplete preferences, comprehensive externalities, infinite-dimensional spaces, or measure-theoretic economies require theory and software design beyond the current finite framework.
