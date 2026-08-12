# Duanmu GE Lab

`Duanmu GE Lab` is a reproducible framework for **finite-model paper replication, equilibrium search, and independent numerical diagnostics**, developed around the quota and emission-tax general-equilibrium models studied by Anderson and Duanmu. The project includes analytical benchmarks, finite production and population-weighted components, signed prices, dedicated implementations of paper Examples 1-6, multiplicity experiments, policy sweeps, and strict candidate diagnostics.

It is not a universal general-equilibrium solver and does not implement mathematical proofs for measure-theoretic economies, comprehensive externalities, or nonstandard analysis. See [Scope and Limitations](docs/SCOPE_AND_LIMITATIONS.md) for the precise boundary.

## Implemented

- Pure-exchange and production economies with explicit net output, firm ownership, and income decomposition.
- Candidate resource accounting separated from independently reoptimized consumer and firm optimality diagnostics.
- Population-weighted aggregation kept distinct from social-welfare weights.
- Signed-L1 and numeraire coordinates, signed prices, and commodity-specific clearing rules.
- Bads with negative prices and explicit consumption sets.
- Quota accounting from Definitions 3.1-3.5 and tax accounting from Definitions 4.1-4.3 of the paper.
- Dedicated finite-model replications of Anderson-Duanmu Examples 1-6.
- Numerical consistency checks for the mappings in Theorems 3-4.
- Deterministic, random, and continuation multistart search with verified-candidate clustering.
- Parameter sweeps from tax rates to emissions sets and from quota targets to quota-price sets.
- Quota-rights allocation experiments at fixed emissions.
- A construction-specific finite weighted bad-absorption experiment.
- YAML experiment parameters, reproducibility metadata, research figures, and a strict final audit.

## Claim Boundaries

- `VERIFIED_CANDIDATE` means that a finite candidate passes every implemented diagnostic at the recorded tolerances. It is not a general existence proof.
- `DISCOVERED_N_VERIFIED_CANDIDATE_CLUSTERS` describes candidate clusters found under a specified search protocol. It does not assert that exactly `N` equilibria exist.
- Example 4's `NO_EQUILIBRIUM` label comes from the paper's theory. A numerical search that finds no candidate is not itself a proof.
- Milestone 11 is a paper-inspired finite-grid experiment. Its aggregate stability mainly reflects the linear midpoint construction; it is not a continuum-convergence theorem or a verification of uniform integrability.
- The project has no general comprehensive-externality preference interface, Loeb-measure or hyperfinite implementation, or automatic computation of an "optimal carbon policy."

## Installation

`pyproject.toml` specifies supported dependency ranges. `requirements-tested.txt` records one reference Windows/CPython environment that was actually tested; those pins do not imply validation on every operating system.

Cross-platform setup:

```text
cd <path-to-project>/2025_GE_Replication_Toolkit
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q src scripts paper_replications
```

Windows PowerShell without activating the virtual environment:

```powershell
cd <path-to-project>\2025_GE_Replication_Toolkit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts paper_replications
```

POSIX without activating the virtual environment:

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

To reproduce the exact reference environment, run `python -m pip install -r requirements-tested.txt`, followed by `python -m pip install -e . --no-deps`.

## Smoke Tests

Minimal analytical benchmark:

```text
python scripts/run_baseline.py
```

Rebuild all required experiments and figures from scratch. Either command returns a nonzero exit code if any expected status does not match:

```text
python scripts/run_reproducibility_suite.py
python scripts/run_final_audit.py
```

On Windows, `python` may be replaced with `.\.venv\Scripts\python.exe` in these commands.

## Configuration Boundary

YAML controls exposed experiment parameters such as quotas, tax rates, ownership regimes, initial values, grids, population sizes, random seeds, and solver settings:

```text
python scripts/run_experiment.py --config configs/paper/example_3.yaml
python scripts/run_experiment.py --config configs/experiments/tax_quota_sweeps.yaml
```

The commodity structure, preferences, technologies, and equation reductions for the paper examples remain encoded in paper-specific Python builders and solvers. Arbitrary YAML cannot automatically generate a new model or solver.

## Research Results

- **Examples 1-2:** analytical prices, allocations, profits, and property-rights assignments are compared coordinate by coordinate and pass the complete diagnostics.
- **Example 3:** three verified candidate branches are found consistently at the paper's tax rate and match Table I.
- **Example 4:** the paper's theoretical nonexistence statement and the computational precheck are stored separately.
- **Example 5:** different tax-rate and quota-price candidates attain the same target and match Tables II-III.
- **Example 6:** a numerical check records the difference between the guarantees supplied by a tax and by a quota.

Key figure: [tax-emission correspondence](figures/tax_emission_correspondence.png). Its caption and source JSON are documented in [figures/README.md](figures/README.md).

## Navigation

- [Professor demo](PROFESSOR_DEMO.md)
- [Final research report](REPORT.md)
- [Post-hardening audit](FINAL_AUDIT.md)
- [Hardening report](FINAL_HARDENING_REPORT.md)
- [Tested environments](TESTED_ENVIRONMENTS.md)
- [Tolerance audit](TOLERANCE_AUDIT.md)
- [Paper parameter audit](PAPER_PARAMETER_AUDIT.md)
- [Research claim audit](RESEARCH_CLAIM_AUDIT.md)
- [Collaborator guide](COLLABORATOR_GUIDE.md)
- [Citations and source locations](CITATIONS.md)
- [Current research questions](OPEN_QUESTIONS.md)
- [Mathematical specifications](docs/)
- [Machine-readable results](results/)

CI is configured for CPython 3.11, 3.12, and 3.13 in `.github/workflows/tests.yml`. Until a remote workflow run is available, this is accurately described as **CI CONFIGURED**, not CI verified.
