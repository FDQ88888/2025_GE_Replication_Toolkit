# Tested Environments

`pyproject.toml` declares the supported range. This file records only environments that were actually exercised; it does not present an unexecuted CI configuration as verified evidence.

| Platform | Python | NumPy | SciPy | pytest | Matplotlib | PyYAML | Tests | Compile | Reproducibility suite | Final audit |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| Windows 11 | CPython 3.12.13 | 2.5.2 | 1.18.0 | 9.1.1 | 3.11.1 | 6.0.3 | 113 passed, 0 failed | passed | `REPRODUCIBILITY_SUITE_SUCCESS` | `FINAL_AUDIT_PASSED` |
| Windows 11 | CPython 3.13.0 | 2.5.2 | 1.18.0 | 9.1.1 | 3.11.1 | 6.0.3 | 113 passed, 0 failed | passed | `REPRODUCIBILITY_SUITE_SUCCESS` | `FINAL_AUDIT_PASSED` |

Both rows were executed in independent virtual environments on the same Windows machine. The 3.13 environment also ran the baseline, Examples 1 and 3, and the Theorems 3-4 mapping CI smoke commands.

GitHub Actions is configured with an Ubuntu matrix for CPython 3.11, 3.12, and 3.13. Each job installs the package, runs pytest and compileall, executes the baseline and critical paper replications, rebuilds the complete suite, and runs the strict final audit. No remote workflow run was available when this record was created, so the accurate status is **CI CONFIGURED**, not CI verified. Python 3.11 is therefore not listed as a locally tested environment.

`requirements-tested.txt` pins the exact dependency versions from the verified 3.12 reference environment. The 3.13 run resolved to the same direct and transitive versions, but this does not imply that the pins cover every operating system or future interpreter.
