# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.econometrics.local_projection import run_local_projections  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.outputs import table_path  # noqa: E402


def run_regressions(
    dataset: str = "sample",
    root: Path | None = None,
    horizons: list[int] | None = None,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel = pd.read_csv(paths.data_processed / panel_name, parse_dates=["date_month"])
    controls = ["sample_global_cycle"] if dataset == "sample" else []

    results = run_local_projections(
        panel,
        horizons=horizons or [1, 3, 6],
        config={"shock_col": "gpr_global_z", "controls": controls},
    )
    results.round(6).to_csv(
        table_path(paths, "table_02_baseline_regressions.csv", dataset),
        index=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GeoRiskLab regressions.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    parser.add_argument("--horizons", default="1,3,6")
    args = parser.parse_args()
    run_regressions(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        horizons=_parse_horizons(args.horizons),
    )


def _parse_horizons(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


if __name__ == "__main__":
    main()
