# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.outputs import table_path  # noqa: E402
from georisklab.utils.validation import (  # noqa: E402
    assert_dates_are_month_start,
    assert_no_duplicate_keys,
    ensure_columns,
    missingness_report,
)

EXPECTED_REAL_SOURCES = {
    "Caldara-Iacoviello GPR",
    "Kenneth French Developed Factors",
    "Kenneth French Emerging Factors",
}


def validate_data(
    dataset: str = "sample",
    root: Path | None = None,
    min_overlap_months: int = 120,
    check_results: bool = False,
) -> None:
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
            "gpr_change_z",
            "gdelt_risk_z",
        ],
    )
    assert_dates_are_month_start(panel, "date_month")
    assert_no_duplicate_keys(panel, ["date_month", "market_id"])
    _validate_forward_return_missingness(panel, [1, 3, 6])

    if dataset == "real":
        gpr = pd.read_csv(paths.data_processed / "gpr_monthly.csv", parse_dates=["date_month"])
        returns = pd.read_csv(
            paths.data_processed / "market_returns_monthly.csv",
            parse_dates=["date_month"],
        )
        _validate_real_source_frames(gpr, returns, min_overlap_months=min_overlap_months)

    if check_results:
        _validate_result_outputs(paths, dataset)

    report = missingness_report(panel)
    report.to_csv(table_path(paths, "table_00_missingness.csv", dataset), index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate GeoRiskLab processed data.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    parser.add_argument("--min-overlap-months", type=int, default=120)
    parser.add_argument("--check-results", action="store_true")
    args = parser.parse_args()
    validate_data(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        min_overlap_months=args.min_overlap_months,
        check_results=args.check_results,
    )


def _metadata_path(metadata_dir: Path, dataset: str) -> Path:
    if dataset == "sample":
        return metadata_dir / "source_manifest.json"
    return metadata_dir / "source_manifest_real.json"


def _validate_metadata(metadata_path: Path, dataset: str) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if dataset == "real":
        sources = metadata.get("sources", [])
        names = {source.get("source_name") for source in sources}
        if names != EXPECTED_REAL_SOURCES:
            raise ValueError("source_manifest_real.json must list expected source names")
        for source in sources:
            raw_path = str(source.get("raw_file_path", ""))
            if "://" not in raw_path and not source.get("file_hash_sha256"):
                raise ValueError("local real source manifest entries must include a file hash")


def _validate_real_source_frames(
    gpr: pd.DataFrame,
    returns: pd.DataFrame,
    min_overlap_months: int = 120,
) -> None:
    ensure_columns(gpr, ["date_month", "gpr_global"])
    ensure_columns(
        returns,
        ["date_month", "market_id", "return_usd", "risk_free_rate", "excess_return"],
    )
    assert_no_duplicate_keys(gpr, ["date_month"])
    assert_no_duplicate_keys(returns, ["date_month", "market_id"])

    counts = returns.groupby("date_month")["market_id"].agg(lambda values: set(values))
    bad_months = counts[counts != {"developed", "emerging"}]
    if not bad_months.empty:
        raise ValueError("returns must contain developed and emerging markets for every month")

    overlap = set(pd.to_datetime(gpr["date_month"])) & set(pd.to_datetime(returns["date_month"]))
    if len(overlap) < min_overlap_months:
        raise ValueError(
            f"GPR and returns overlap must include at least {min_overlap_months} months"
        )

    for column in ["return_usd", "risk_free_rate", "excess_return"]:
        values = pd.to_numeric(returns[column], errors="raise")
        if values.abs().gt(100).any():
            raise ValueError("returns must be in a plausible percentage-point range")


def _validate_forward_return_missingness(panel: pd.DataFrame, horizons: list[int]) -> None:
    for horizon in horizons:
        column = f"ret_fwd_{horizon}m"
        if column not in panel.columns:
            continue
        for _, group in panel.sort_values("date_month").groupby("market_id"):
            missing = group[column].isna().to_numpy()
            allowed = [False] * max(len(group) - horizon, 0) + [True] * min(horizon, len(group))
            if missing.tolist() != allowed:
                raise ValueError(f"{column} missing values are only final horizon rows")


def _validate_result_outputs(paths, dataset: str) -> None:
    forecast_path = table_path(paths, "table_03_forecast_comparison.csv", dataset)
    if not forecast_path.exists():
        raise FileNotFoundError(f"{forecast_path.name} is missing; run make forecasts first")
    _validate_forecast_windows(pd.read_csv(forecast_path))


def _validate_forecast_windows(forecasts: pd.DataFrame) -> None:
    ensure_columns(
        forecasts,
        ["n_forecasts", "first_forecast_date", "last_forecast_date"],
    )
    windows = forecasts[["n_forecasts", "first_forecast_date", "last_forecast_date"]]
    if len(windows.drop_duplicates()) != 1:
        raise ValueError("forecast rows must use the same forecast evaluation dates")


if __name__ == "__main__":
    main()
