# Hardening Fix 02: Experiment Status Semantics

## Defect

The pre-hardening reproducibility suite executed every runner but did not compare returned statuses with required expected statuses. A runner could therefore return `PAPER_REPLICATION_FAILURE`, `NUMERICAL_MAPPING_CHECK_FAILURE`, `BLOCKED`, or an unknown string while the suite still printed `REPRODUCIBILITY_SUITE_SUCCESS`.

The parameter-sweep script also emitted `SWEEP_SUCCESS` unconditionally after completing execution, even if the discovered branch counts did not match the declared validation target.

## Fix

- `experiment_status.py` defines exact registered status-to-outcome mappings. No substring or suffix heuristic is used.
- Every YAML runner declares `expected_status` and `required`.
- Baseline requirements declare the same contract in `run_reproducibility_suite.py`.
- The suite records experiment name, expected status, actual status, coarse outcome, required/optional flag, result path, and details.
- A required failure, block, partial result, skip, missing status, unknown status, exception, or nonzero process result fails the suite.
- An optional `SKIPPED` or `BLOCKED` item may pass only with an explicit warning.
- Suite failure prints each mismatch, writes `results/reproducibility_suite.json`, and returns process exit code `1`.
- Sweep success now requires config-declared tax and quota cluster-count targets to match the actual saved sets.

## Regression Tests

Tests cover:

1. all required exact success statuses;
2. one required failure;
3. one required blocked experiment;
4. one optional skipped experiment with a warning;
5. nonzero suite exit code on failure;
6. sweep validation failure when one required candidate cluster is missing.

## Final-Audit Dependency

The hardened final audit reads `results/reproducibility_suite.json` and requires all of the following: exact status `REPRODUCIBILITY_SUITE_SUCCESS`, `passed=true`, and an empty failure list. It also independently rechecks every critical persisted paper/result status. A failed critical experiment can no longer coexist with `FINAL_AUDIT_PASSED`.
