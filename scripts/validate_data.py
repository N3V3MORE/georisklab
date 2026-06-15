# ruff: noqa: E402, I001
from __future__ import annotations

import argparse

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.validation import (  # noqa: E402
    assert_dates_are_month_start,
    assert_no_duplicate_keys,
    ensure_columns,
    missingness_report,
)


def validate_data(dataset: str = "sample") -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel_path = paths.data_processed / panel_name
    metadata_path = paths.data_metadata / "source_manifest.json"

    if not panel_path.exists():
        raise FileNotFoundError("sample_analysis_panel.csv is missing; run make features first")
    if not metadata_path.exists():
        raise FileNotFoundError("source_manifest.json is missing; run make data-monthly first")

    panel = pd.read_csv(panel_path, parse_dates=["date_month"])
    ensure_columns(
        panel,
        [
            "date_month",
            "market_id",
            "market_class",
            "excess_return",
            "ret_fwd_1m",
            "gpr_global_z",
            "gdelt_risk_z",
        ],
    )
    assert_dates_are_month_start(panel, "date_month")
    assert_no_duplicate_keys(panel, ["date_month", "market_id"])

    report = missingness_report(panel)
    report.to_csv(paths.reports_tables / "table_00_missingness.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate GeoRiskLab processed data.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    args = parser.parse_args()
    validate_data(dataset=args.dataset)


if __name__ == "__main__":
    main()
