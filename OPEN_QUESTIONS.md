# Duanmu GE Lab: Current Open Questions

> Updated 2026-08-10. Completed software components are no longer labeled `BLOCKING`; this list retains only genuinely unresolved research questions and model extensions.

## Resolved Key Issues

- The Econometrica Supplement has been obtained from the official source and archived; the parameters and derivations for Examples 1-6 are no longer source-blocked.
- Quota prices, government-firm allocations, tax rebates, `Z(m)`, `V`, and `proj_k(p)=-t` have been checked against the original text.
- `PaperTaxConvention` implements and tests the joint scaling of the tax rate between signed-L1 and numeraire normalizations.
- Candidate resource accounting is strictly separated from reoptimized optimality.
- Population and welfare weights are separated; feasible regions for bads are specified explicitly by `ConsumptionSet`.
- Numerical non-discovery is recorded separately from theoretical nonexistence established in the paper.

## Q1. How Can the Paper's General Preferences Be Represented Computationally?

The paper permits preferences that are incomplete, intransitive, and dependent on prices, other agents' allocations, and production. The current code supports only finite models with explicit choice rules or utility representations. The next step must decide whether to study choice correspondences, a computationally tractable utility subclass, or extensions limited to particular examples. Until then, the project cannot claim to cover the paper's full generality of preferences.

## Q2. Can Completeness of the Numerically Discovered Branches Be Certified?

Current multistart, continuation, and clustering procedures reliably discover branches in the paper's examples, but cannot exclude undiscovered roots. Possible next methods include analytical elimination, interval arithmetic, homotopy continuation, and degree theory. Outputs therefore retain the wording `discovered verified candidate clusters`.

## Q3. How Can Nonexistence Be Certified in a General Model?

The no-equilibrium status of Example 4 is supported by the paper's proof. In a general model, failure of a solver to find a root remains non-certifying. Research is needed on verifiable inequality contradictions, unbounded-profit prechecks, interval methods, or problem-specific dual certificates.

## Q4. Which Social Objective Should Welfare Comparisons Use?

The current project compares agents individually at fixed emissions and refuses to construct aggregate welfare where the paper supplies no cardinal utilities. Studying policies across emission levels requires guidance from the professor on external damages, welfare weights, and interpersonal comparability assumptions.

## Q5. Which Continuum Economy Should the Finite Weighted Experiment Approximate?

Milestone 11 currently uses a self-contained continuum-type target with midpoint discretization. A convergence study would additionally require a specified type space, measure, preference and endowment mappings, topology, equilibrium correspondence, convergence concept, and an analytical or theoretical reference result.

## Q6. Can Bad-Absorption Tail Diagnostics Be Linked Theoretically to Uniform Integrability?

Current reports include maximum absorption, upper-tail population shares, weighted tail integrals, and truncated means; these are heuristic statistics only. Future work could investigate which finite-sample conditions, under additional assumptions, yield testable sufficient conditions for tightness or uniform integrability.

## Q7. Have Professor Duanmu's Related Working Papers Been Obtained?

The latest versions of "The Second Welfare Theorem for Quota Equilibrium," "Measure-theoretic Production Economies with Externalities and Bads," and "Pareto Optimality with Externality" still require confirmation from the author. Before they are obtained, the project will neither restate unpublished theorems nor implement conjectured content based on titles alone.

## Q8. What Should Be Prioritized in the Next Discussion with the Professor?

1. Should priority go to a computationally tractable subclass of general preferences or to completeness certification for multiple-equilibrium branches?
2. Which specific theorem or counterexample in a measure economy should guide the finite weighted component?
3. Should the welfare module adopt a specified social objective, or continue to report only agent-by-agent rankings and income decompositions?
