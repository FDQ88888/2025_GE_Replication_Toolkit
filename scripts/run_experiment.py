"""Run any registered YAML experiment through one stable command-line entry point."""

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Callable

from duanmu_ge_lab.experiment_io import load_yaml_mapping
from duanmu_ge_lab.experiment_status import is_registered_success

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _resolve_config(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    config_root = (ROOT / "configs").resolve()
    if config_root not in resolved.parents:
        raise ValueError("Experiment configs must be stored under the project configs directory.")
    if not resolved.is_file():
        raise FileNotFoundError(f"Config does not exist: {resolved}")
    return resolved


def run_config(config_path: Path) -> dict[str, Any]:
    config = load_yaml_mapping(config_path)
    runner = config.get("runner")
    if not isinstance(runner, dict):
        raise ValueError("Config must declare a runner mapping.")
    module_name = runner.get("module")
    callable_name = runner.get("callable", "run")
    if not isinstance(module_name, str) or not isinstance(callable_name, str):
        raise ValueError("runner.module and runner.callable must be strings.")
    module = importlib.import_module(module_name)
    function: Callable[[Path], dict[str, Any]] = getattr(module, callable_name)
    result = function(config_path)
    if not isinstance(result, dict):
        raise TypeError("Experiment runner must return a mapping.")
    return result


def experiment_exit_code(status: object) -> int:
    """Return success only for an explicitly registered successful status."""
    return 0 if isinstance(status, str) and is_registered_success(status) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="YAML path under configs/")
    args = parser.parse_args(argv)
    config_path = _resolve_config(args.config)
    result = run_config(config_path)
    status = result.get("status", "COMPLETED_WITHOUT_TOP_LEVEL_STATUS")
    print(f"{config_path.relative_to(ROOT)}: {status}")
    return experiment_exit_code(status)


if __name__ == "__main__":
    sys.exit(main())
