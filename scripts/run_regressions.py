# ruff: noqa: E402, I001
from __future__ import annotations

import argparse

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.econometrics.local_projection import run_local_projections  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402


def run_regressions(dataset: str = "sample") -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel = pd.read_csv(paths.data_processed / panel_name, parse_dates=["date_month"])

    results = run_local_projections(
        panel,
        horizons=[1, 3, 6],
        config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
    )
    results.round(6).to_csv(paths.reports_tables / "table_02_baseline_regressions.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GeoRiskLab regressions.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    args = parser.parse_args()
    run_regressions(dataset=args.dataset)


if __name__ == "__main__":
    main()
