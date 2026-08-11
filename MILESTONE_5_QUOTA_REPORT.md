# Milestone 5 Quota Report

## Verdict

**VERIFIED.** The quota accounting layer and paper Examples 1-2 pass their full
gates. Both result files carry `PAPER_REPLICATION_SUCCESS`, and every solved regime
is independently classified `VERIFIED_CANDIDATE`.

## Primary-source basis

- Quota economy and equilibrium: main article PDF pages 7-10, Definitions 3.1-3.5
  and Remark 3.3.
- Example 1: main article PDF pages 11-12 (journal pages 367-368); Supplement PDF
  pages 11-12, Section 3.1, Claims 3.1-3.2.
- Example 2: main article PDF pages 12-13 (journal pages 368-369); Supplement PDF
  pages 12-14, Section 3.2, Claims 3.3-3.4.
- Rebate/Walras accounting cross-check: Supplement PDF pages 3-6.

The archived official sources are listed in `CITATIONS.md`.

## Implemented objects

- `QuotaPolicy`: signed `m^(j)`, `m=sum_j m^(j)`, `Z(m)`, and
  `q=-proj_k(p)` without a permit commodity.
- `QuotaEconomy`: one source of truth for operating profit, quota profit,
  ownership distributions, consumer income, and the adjusted Walras identity.
- `ZeroTechnology` and `LinearRayTechnology`: paper government and private
  production sets, including explicit rejection of unbounded positive profit.
- `SingleGoodLinearUtility`: own-demand oracle for the paper's fixed-zero CO2
  consumption sets and one desired commodity.
- `QuotaEquilibriumCandidate` and `QuotaEquilibriumDiagnostics`: candidate-only
  coordinates, cache auditing, consumer/firm optimality, ownership, budget,
  compliance, signed prices, and quota-adjusted Walras checks.
- YAML configs and independently solved replication entry points for Examples 1-2.

## Example 1

The checked paper parameter is `v=-m=1/2`. Analytical values are:

```text
p       = (-1/4, 1/4, 1/2)
x_1     = (0, 0, 1/2)
x_2     = (0, 1/2, 0)
y_1     = (1/2, -1/2, 1/2)
q       = 1/4
pi_0    = 1/8
I_1     = 1/4
I_2     = 1/8
u_1=u_2 = 1/4
```

The nonlinear equation solver recovered prices with maximum absolute difference
`2.78e-17` and allocations with maximum absolute difference `5.55e-17`. Candidate
cache error, compliance violation, and quota-adjusted Walras residual are exactly
zero in the saved result.

Result: `results/milestone5_paper_example_1.json`.

## Example 2

The checked total emissions quota is `v=3`. Both property-rights allocations recover

```text
p = (-1/4, 1/4, 1/2).
```

Global quota electricity consumption is

```text
(1, 3/2, 2).
```

Cap-and-trade electricity consumption is numerically

```text
(0.75000000000005, 1.49999999999998, 2.24999999999998),
```

with maximum allocation error `5.00e-14`. Global minus cap-and-trade is therefore
`(1/4, 0, -1/4)` up to solver error: agent 1 is better off under global quota,
agent 2 is indifferent, and agent 3 is better off under cap-and-trade at the same
total emissions. Prices, total consumption, technology, endowments, preferences,
and total quota remain invariant.

The paper does not specify cardinal utility functions for Example 2. The output
labels electricity quantities as own-consumption utility components and reports only
the paper-supported ordinal welfare ordering.

Result: `results/milestone5_paper_example_2.json`.

## Verification gate

At the milestone gate:

```text
pytest: 65 passed in 0.59s
Example 1: PAPER_REPLICATION_SUCCESS / VERIFIED_CANDIDATE
Example 2 global quota: PAPER_REPLICATION_SUCCESS / VERIFIED_CANDIDATE
Example 2 cap-and-trade: PAPER_REPLICATION_SUCCESS / VERIFIED_CANDIDATE
```

The new tests reject positive `m^(j)`, distinguish exact clearing from free disposal,
detect unbounded ray profit, reject a tampered quota-price cache, and reject candidate
coordinates outside `Z(m)`.

## Scope boundary

This milestone validates finite Examples 1-2. It does not implement a general
externality-preference engine, a general-purpose quota equilibrium solver, emission
taxes, equilibrium multiplicity discovery, or the measure-economy existence proofs.
Those claims remain outside the verified scope.
