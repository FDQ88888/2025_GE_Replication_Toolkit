from scripts.run_experiment import experiment_exit_code


def test_experiment_exit_code_accepts_only_registered_success() -> None:
    assert experiment_exit_code("PAPER_REPLICATION_SUCCESS") == 0
    assert experiment_exit_code("PAPER_REPLICATION_FAILURE") == 1
    assert experiment_exit_code("UNKNOWN_SUCCESS") == 1
    assert experiment_exit_code(None) == 1
