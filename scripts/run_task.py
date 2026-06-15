# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import subprocess
import sys

from _bootstrap import add_project_root

add_project_root()

TASKS = {
    "setup": [[sys.executable, "-m", "pip", "install", "-e", ".[dev]"]],
    "data-monthly": [[sys.executable, "scripts/build_monthly_data.py"]],
    "features": [[sys.executable, "scripts/build_features.py"]],
    "regressions": [[sys.executable, "scripts/run_regressions.py"]],
    "forecasts": [[sys.executable, "scripts/run_forecasts.py"]],
    "figures": [[sys.executable, "scripts/make_figures.py"]],
    "report": [[sys.executable, "scripts/build_report.py"]],
    "validate-data": [[sys.executable, "scripts/validate_data.py"]],
    "test": [[sys.executable, "-m", "pytest"]],
    "lint": [[sys.executable, "-m", "ruff", "check", "."]],
}

PIPELINE = [
    "data-monthly",
    "features",
    "validate-data",
    "regressions",
    "forecasts",
    "figures",
    "report",
]


def run_task(name: str) -> int:
    task_names = PIPELINE if name == "pipeline" else [name]
    for task_name in task_names:
        if task_name not in TASKS:
            valid = ", ".join([*TASKS, "pipeline"])
            raise ValueError(f"unknown task '{task_name}'. Valid tasks: {valid}")
        for command in TASKS[task_name]:
            result = subprocess.run(command, check=False)
            if result.returncode != 0:
                return result.returncode
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GeoRiskLab project tasks.")
    parser.add_argument("task", choices=[*TASKS, "pipeline"])
    args = parser.parse_args()
    raise SystemExit(run_task(args.task))


if __name__ == "__main__":
    main()
