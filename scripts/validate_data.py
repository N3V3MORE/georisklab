# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def validate_data(dataset: str = "sample", root: Path | None = None) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel_path = paths.data_processed / panel_name
    metadata_path = _metadata_path(paths.data_metadata, dataset)

    if not panel_path.exists():
        raise FileNotFoundError(f"{panel_name} is missing; run make features first")
    if not metadata_path.exists():
        raise FileNotFoundError(f"{metadata_path.name} is missing; run the data task first")
    _validate_metadata(metadata_path, dataset)

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
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    validate_data(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
    )


def _metadata_path(metadata_dir: Path, dataset: str) -> Path:
    if dataset == "sample":
        return metadata_dir / "source_manifest.json"
    return metadata_dir / "source_manifest_real.json"


def _validate_metadata(metadata_path: Path, dataset: str) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if dataset == "real":
        sources = metadata.get("sources", [])
        if len(sources) < 3:
            raise ValueError("source_manifest_real.json must list GPR and Fama-French sources")


if __name__ == "__main__":
    main()
