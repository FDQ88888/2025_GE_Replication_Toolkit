# Delivery Manifest

## Recommended Starting Points for the Professor

1. `PROFESSOR_DEMO.md`: a 3-5 minute overview of the research position, relationship to the paper, results, and boundaries.
2. `README.md`: runnable commands, implementation scope, claim boundaries, and navigation.
3. `FINAL_HARDENING_REPORT.md`: critical defects, test evidence, two-environment verification, the largest critical residual, and claims that remain unsupported.

## Recommended Full Reading Order

1. `PROFESSOR_DEMO.md`
2. `README.md`
3. `docs/paper_example_3_math.md` and `MILESTONE_7_EXAMPLES_3_6_REPORT.md`
4. `figures/tax_emission_correspondence.png` and `results/milestone9_tax_quota_sweeps.json`
5. `FINAL_HARDENING_REPORT.md`, `FINAL_AUDIT.md`, and `TESTED_ENVIRONMENTS.md`
6. `src/`, `paper_replications/`, `scripts/`, and `tests/`

## Main Files

| Path | Purpose |
|---|---|
| `README.md` | Project position, installation, smoke commands, configuration boundaries, and result navigation |
| `PROFESSOR_DEMO.md` | Concise presentation for a theoretical researcher |
| `REPORT.md` | Overall research report |
| `FINAL_HARDENING_REPORT.md` | Final hardening process and quantitative evidence |
| `FINAL_AUDIT.md` | Post-hardening audit and preserved historical audit |
| `PRE_HARDENING_AUDIT.md` | Factual pre-hardening baseline summary |
| `HARDENING_FIX_01_LINEAR_RAY.md` | Zero-margin floating-point defect and revalidation |
| `HARDENING_FIX_02_STATUS_SEMANTICS.md` | False-success defect and status contract |
| `TOLERANCE_AUDIT.md` | Itemized semantics of critical numerical tolerances |
| `PAPER_PARAMETER_AUDIT.md` | Parameter sources and computational choices for Examples 1-6 |
| `RESEARCH_CLAIM_AUDIT.md` | Wording boundaries for SUCCESS, VERIFIED, EXISTENCE, and related terms |
| `TESTED_ENVIRONMENTS.md` | Distinction between two actual local environments and unexecuted CI |
| `CITATIONS.md` | Bibliographic information, official links, and source-page mapping |
| `OPEN_QUESTIONS.md` | Unresolved theoretical questions and research directions |
| `COLLABORATOR_GUIDE.md` | Mathematical information required to add a new finite model |
| `docs/SCOPE_AND_LIMITATIONS.md` | Precise boundaries on generality and unimplemented capabilities |
| `requirements-tested.txt` | Pins for the verified CPython 3.12 reference environment |
| `.github/workflows/tests.yml` | CPython 3.11/3.12/3.13 CI configuration |
| `results/reproducibility_suite.json` | Machine-readable status of 16 required observations |
| `results/final_audit.json` | Machine-readable evidence from the strict final audit |

The mathematical ledgers for paper Examples 1-6 are in `docs/paper_example_1_math.md` through `docs/paper_example_6_math.md`. Historical reports, research notes, and implementation plans are retained for every stage.

## Clean Archive

The professor-facing archive is named `duanmu_ge_lab_hardened_source.zip`. It retains source code, tests, configurations, documentation, necessary results, and figures, while explicitly excluding:

- `.venv/`, `.venv313/`, and other local virtual environments;
- `__pycache__/`, `.pytest_cache/`, `*.pyc`, `*.egg-info/`, `build/`, and `dist/`;
- machine-local temporary logs and snapshots under `hardening/pre_hardening/`;
- paper PDFs and local text extractions under `sources/`;
- the obsolete `duanmu_ge_lab_source.zip`;
- all personal absolute paths.

Copyrighted papers should be obtained independently from the official links in `CITATIONS.md`. Results in the clean archive are those most recently rebuilt in the CPython 3.12 reference environment; independent CPython 3.13 verification is recorded in `TESTED_ENVIRONMENTS.md`.
