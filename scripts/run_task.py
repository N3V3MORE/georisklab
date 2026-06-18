# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from _bootstrap import add_project_root

add_project_root()

TASKS = {
    "setup": [[sys.executable, "-m", "pip", "install", "-c", "constraints.txt", "-e", ".[dev]"]],
    "data-monthly": [[sys.executable, "scripts/build_monthly_data.py"]],
    "data-real": [
        [
            sys.executable,
            "scripts/build_real_monthly_data.py",
            "--config",
            "config/sources.yml",
        ]
    ],
    "features": [[sys.executable, "scripts/build_features.py"]],
    "regressions": [[sys.executable, "scripts/run_regressions.py"]],
    "forecasts": [[sys.executable, "scripts/run_forecasts.py"]],
    "figures": [[sys.executable, "scripts/make_figures.py"]],
    "report": [[sys.executable, "scripts/build_report.py", "--dataset", "sample"]],
    "validate-data": [[sys.executable, "scripts/validate_data.py"]],
    "validate-results": [[sys.executable, "scripts/validate_data.py", "--check-results"]],
    "test": [[sys.executable, "-m", "pytest"]],
    "lint": [[sys.executable, "-m", "ruff", "check", "."]],
}

PIPELINE = [
    "data-monthly",
    "features",
    "validate-data",
    "regressions",
    "forecasts",
    "validate-results",
    "figures",
    "report",
]

PIPELINE_REAL = [
    "data-real",
    "features-real",
    "validate-data-real",
    "regressions-real",
    "forecasts-real",
    "validate-results-real",
    "figures-real",
    "report-real",
]

TASKS.update(
    {
        "features-real": [[sys.executable, "scripts/build_features.py", "--dataset", "real"]],
        "validate-data-real": [
            [sys.executable, "scripts/validate_data.py", "--dataset", "real"]
        ],
        "validate-results-real": [
            [
                sys.executable,
                "scripts/validate_data.py",
                "--dataset",
                "real",
                "--check-results",
            ]
        ],
        "regressions-real": [
            [sys.executable, "scripts/run_regressions.py", "--dataset", "real"]
        ],
        "forecasts-real": [[sys.executable, "scripts/run_forecasts.py", "--dataset", "real"]],
        "figures-real": [[sys.executable, "scripts/make_figures.py", "--dataset", "real"]],
        "report-real": [[sys.executable, "scripts/build_report.py", "--dataset", "real"]],
    }
)

ROOT_AWARE_SCRIPTS = {
    "scripts/build_monthly_data.py",
    "scripts/build_real_monthly_data.py",
    "scripts/build_features.py",
    "scripts/run_regressions.py",
    "scripts/run_forecasts.py",
    "scripts/make_figures.py",
    "scripts/build_report.py",
    "scripts/validate_data.py",
}

DEFAULT_CONFIG = "config/sources.yml"


def run_task(
    name: str,
    root: Path | None = None,
    *,
    config: str = DEFAULT_CONFIG,
    horizons: str = "1,3,6",
    min_train_months: int = 120,
    min_overlap_months: int = 120,
    min_forecast_train_months: int = 120,
) -> int:
    config = _rooted_default_config(config, root)
    if name == "pipeline":
        task_names = PIPELINE
    elif name == "pipeline-real":
        task_names = PIPELINE_REAL
    else:
        task_names = [name]
    for task_name in task_names:
        if task_name not in TASKS:
            valid = ", ".join([*TASKS, "pipeline", "pipeline-real"])
            raise ValueError(f"unknown task '{task_name}'. Valid tasks: {valid}")
        for command in TASKS[task_name]:
            command = _command_with_options(
                command,
                config=config,
                horizons=horizons,
                min_train_months=min_train_months,
                min_overlap_months=min_overlap_months,
                min_forecast_train_months=min_forecast_train_months,
            )
            result = subprocess.run(_command_with_root(command, root), check=False)
            if result.returncode != 0:
                return result.returncode
    return 0


def _command_with_options(
    command: list[str],
    *,
    config: str,
    horizons: str,
    min_train_months: int,
    min_overlap_months: int,
    min_forecast_train_months: int,
) -> list[str]:
    if len(command) < 2:
        return command
    script = command[1].replace("\\", "/")
    result = list(command)
    if script == "scripts/build_real_monthly_data.py":
        result = _replace_option(result, "--config", config)
    if script == "scripts/run_regressions.py":
        result = _append_missing_option(result, "--horizons", horizons)
    if script == "scripts/run_forecasts.py":
        result = _append_missing_option(result, "--min-train-months", str(min_train_months))
    if script == "scripts/validate_data.py":
        result = _append_missing_option(result, "--min-overlap-months", str(min_overlap_months))
        result = _append_missing_option(
            result,
            "--min-forecast-train-months",
            str(min_forecast_train_months),
        )
    return result


def _rooted_default_config(config: str, root: Path | None) -> str:
    if root is None or config != DEFAULT_CONFIG:
        return config
    return str(root / config)


def _replace_option(command: list[str], option: str, value: str) -> list[str]:
    if option not in command:
        return [*command, option, value]
    index = command.index(option)
    return [*command[: index + 1], value, *command[index + 2 :]]


def _append_missing_option(command: list[str], option: str, value: str) -> list[str]:
    if option in command:
        return command
    return [*command, option, value]


def _command_with_root(command: list[str], root: Path | None) -> list[str]:
    if root is None or len(command) < 2:
        return command
    script = command[1].replace("\\", "/")
    if script not in ROOT_AWARE_SCRIPTS:
        return command
    return [*command, "--root", str(root)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GeoRiskLab project tasks.")
    parser.add_argument("task", choices=[*TASKS, "pipeline", "pipeline-real"])
    parser.add_argument("--root", default=None)
    parser.add_argument("--config", default="config/sources.yml")
    parser.add_argument("--horizons", default="1,3,6")
    parser.add_argument("--min-train-months", type=int, default=120)
    parser.add_argument("--min-overlap-months", type=int, default=120)
    parser.add_argument("--min-forecast-train-months", type=int, default=120)
    args = parser.parse_args()
    raise SystemExit(
        run_task(
            args.task,
            root=Path(args.root) if args.root else None,
            config=args.config,
            horizons=args.horizons,
            min_train_months=args.min_train_months,
            min_overlap_months=args.min_overlap_months,
            min_forecast_train_months=args.min_forecast_train_months,
        )
    )


if __name__ == "__main__":
    main()
