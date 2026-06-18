# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.datasets import dataset_files  # noqa: E402
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
    min_forecast_train_months: int = 120,
    check_results: bool = False,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    files = dataset_files(dataset)
    panel_path = paths.data_processed / files.analysis_panel
    metadata_path = paths.data_metadata / files.source_manifest
    analysis_manifest_path = paths.data_metadata / files.analysis_manifest

    if not panel_path.exists():
        raise FileNotFoundError(f"{files.analysis_panel} is missing; run make features first")
    if not metadata_path.exists():
        raise FileNotFoundError(f"{metadata_path.name} is missing; run the data task first")
    if not analysis_manifest_path.exists():
        raise FileNotFoundError(
            f"{analysis_manifest_path.name} is missing; run the feature task first"
        )
    _validate_metadata(metadata_path, dataset)

    panel = pd.read_csv(panel_path, parse_dates=["date_month"])
    analysis_manifest = _validate_analysis_panel_manifest(analysis_manifest_path, dataset)
    ensure_columns(
        panel,
        [
            "date_month",
            "market_id",
            "market_class",
            "excess_return",
            "ret_fwd_1m",
            "gpr_change_z",
            "gdelt_risk_raw",
            "gdelt_risk_z",
        ],
    )
    assert_dates_are_month_start(panel, "date_month")
    assert_no_duplicate_keys(panel, ["date_month", "market_id"])
    _validate_forward_return_missingness(panel, [1, 3, 6])

    if dataset == "real":
        # Real-data checks are stricter because these outputs can be mistaken for findings.
        gpr = pd.read_csv(paths.data_processed / files.gpr, parse_dates=["date_month"])
        returns = pd.read_csv(
            paths.data_processed / files.market_returns,
            parse_dates=["date_month"],
        )
        _validate_real_source_frames(gpr, returns, min_overlap_months=min_overlap_months)
        if min_forecast_train_months <= min_overlap_months:
            _validate_real_forecast_feasibility(
                gpr,
                returns,
                min_forecast_train_months=min_forecast_train_months,
            )
        _validate_real_panel_sample(panel, gpr, returns, analysis_manifest)

    if check_results:
        _validate_result_outputs(paths, dataset)

    report = missingness_report(panel)
    report.to_csv(table_path(paths, "table_00_missingness.csv", dataset), index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate GeoRiskLab processed data.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    parser.add_argument("--min-overlap-months", type=int, default=120)
    parser.add_argument("--min-forecast-train-months", type=int, default=120)
    parser.add_argument("--check-results", action="store_true")
    args = parser.parse_args()
    validate_data(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        min_overlap_months=args.min_overlap_months,
        min_forecast_train_months=args.min_forecast_train_months,
        check_results=args.check_results,
    )


def _validate_metadata(metadata_path: Path, dataset: str) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if dataset == "real":
        sources = metadata.get("sources", [])
        names = {source.get("source_name") for source in sources}
        if names != EXPECTED_REAL_SOURCES:
            raise ValueError("source_manifest_real.json must list expected source names")
        for source in sources:
            if not source.get("file_hash_sha256"):
                raise ValueError("real source manifest entries must include a file hash")


def _validate_analysis_panel_manifest(metadata_path: Path, dataset: str) -> dict:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("dataset") != dataset:
        raise ValueError(f"{metadata_path.name} must describe the {dataset} dataset")
    for key in ["sample_start", "sample_end", "n_months"]:
        if key not in metadata:
            raise ValueError(f"{metadata_path.name} is missing {key}")
    if dataset == "real":
        for key in [
            "used_placeholder_gdelt",
            "used_placeholder_macro",
            "processed_input_hashes",
            "analysis_panel_hash_sha256",
            "aligned_to_common_gpr_returns_sample",
            "common_sample_start",
            "common_sample_end",
            "common_sample_n_months",
        ]:
            if key not in metadata:
                raise ValueError(f"{metadata_path.name} is missing {key}")
        if metadata["used_placeholder_gdelt"] not in {True, False}:
            raise ValueError("used_placeholder_gdelt must be boolean")
        if metadata["used_placeholder_macro"] not in {True, False}:
            raise ValueError("used_placeholder_macro must be boolean")
        if not metadata["processed_input_hashes"]:
            raise ValueError("processed_input_hashes must not be empty")
        if not metadata["analysis_panel_hash_sha256"]:
            raise ValueError("analysis_panel_hash_sha256 must not be empty")
        if metadata["aligned_to_common_gpr_returns_sample"] is not True:
            raise ValueError("real analysis panel must be aligned to common GPR/returns sample")
    return metadata


def _validate_real_source_frames(
    gpr: pd.DataFrame,
    returns: pd.DataFrame,
    min_overlap_months: int = 120,
) -> None:
    ensure_columns(gpr, ["date_month", "gpr_global", "source_download_date"])
    ensure_columns(
        returns,
        [
            "date_month",
            "market_id",
            "return_usd",
            "risk_free_rate",
            "excess_return",
            "source_download_date",
        ],
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

    _require_finite_numeric(gpr, ["gpr_global"], "real GPR")
    _require_finite_numeric(
        returns,
        ["return_usd", "risk_free_rate", "excess_return"],
        "real returns",
    )

    for column in ["return_usd", "risk_free_rate", "excess_return"]:
        values = pd.to_numeric(returns[column], errors="raise")
        if values.abs().gt(100).any():
            raise ValueError("returns must be in a plausible percentage-point range")


def _validate_real_forecast_feasibility(
    gpr: pd.DataFrame,
    returns: pd.DataFrame,
    min_forecast_train_months: int,
) -> None:
    overlap = set(pd.to_datetime(gpr["date_month"])) & set(pd.to_datetime(returns["date_month"]))
    usable_months = len(overlap) - 2
    if usable_months <= min_forecast_train_months:
        raise ValueError(
            "real GPR and returns overlap is too short for the default forecast split: "
            f"{len(overlap)} overlap months leaves {usable_months} usable forecast rows "
            f"after first-difference and forward-return edge rows"
        )


def _validate_real_panel_sample(
    panel: pd.DataFrame,
    gpr: pd.DataFrame,
    returns: pd.DataFrame,
    analysis_manifest: dict,
) -> None:
    panel_dates = set(pd.to_datetime(panel["date_month"]).drop_duplicates())
    common_dates = set(pd.to_datetime(gpr["date_month"])) & set(
        pd.to_datetime(returns["date_month"])
    )
    if panel_dates != common_dates:
        raise ValueError("analysis panel dates must match the common GPR and returns sample")
    required_markets = {"developed", "emerging"}
    coverage = panel.groupby("date_month")["market_id"].agg(lambda values: set(values))
    bad_months = coverage[coverage != required_markets]
    if not bad_months.empty:
        raise ValueError("real analysis panel must contain developed and emerging markets")
    sample_named_columns = [column for column in panel.columns if column.startswith("sample_")]
    if sample_named_columns:
        raise ValueError(
            f"real analysis panel contains sample-named columns: {sample_named_columns}"
        )
    if analysis_manifest.get("used_placeholder_gdelt"):
        for column in ["gdelt_risk_raw", "gdelt_risk_z"]:
            values = pd.to_numeric(panel[column], errors="raise")
            if not values.eq(0).all():
                raise ValueError(f"{column} must be zero when placeholder GDELT is recorded")
    if (
        analysis_manifest.get("used_placeholder_macro")
        and "placeholder_macro_zero" not in panel.columns
    ):
        raise ValueError("real placeholder macro manifest requires placeholder_macro_zero column")


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
    regression_path = table_path(paths, "table_02_baseline_regressions.csv", dataset)
    if not regression_path.exists():
        raise FileNotFoundError(f"{regression_path.name} is missing; run make regressions first")
    _validate_regression_outputs(pd.read_csv(regression_path))

    forecast_path = table_path(paths, "table_03_forecast_comparison.csv", dataset)
    if not forecast_path.exists():
        raise FileNotFoundError(f"{forecast_path.name} is missing; run make forecasts first")
    _validate_forecast_outputs(pd.read_csv(forecast_path))


def _validate_regression_outputs(regressions: pd.DataFrame) -> None:
    ensure_columns(regressions, ["horizon", "term", "estimate", "std_error", "p_value"])
    assert_no_duplicate_keys(regressions, ["horizon", "term"])
    if regressions.empty:
        raise ValueError("baseline regression table must contain at least one row")
    _require_finite_numeric(
        regressions,
        ["estimate", "std_error", "t_value", "p_value", "nobs", "adjusted_r2"],
        "baseline regression table",
    )
    if pd.to_numeric(regressions["std_error"], errors="raise").lt(0).any():
        raise ValueError("baseline regression standard errors must be non-negative")


def _validate_forecast_outputs(forecasts: pd.DataFrame) -> None:
    ensure_columns(
        forecasts,
        [
            "model",
            "rmse",
            "mae",
            "oos_r2",
            "n_forecasts",
            "first_forecast_date",
            "last_forecast_date",
        ],
    )
    assert_no_duplicate_keys(forecasts, ["model"])
    _require_finite_numeric(
        forecasts,
        ["rmse", "mae", "oos_r2", "n_forecasts"],
        "forecast comparison table",
    )
    for column in ["rmse", "mae"]:
        if pd.to_numeric(forecasts[column], errors="raise").lt(0).any():
            raise ValueError(f"{column} must be non-negative")
    if pd.to_numeric(forecasts["n_forecasts"], errors="raise").le(0).any():
        raise ValueError("n_forecasts must be positive")
    _validate_forecast_windows(forecasts)


def _validate_forecast_windows(forecasts: pd.DataFrame) -> None:
    ensure_columns(
        forecasts,
        ["n_forecasts", "first_forecast_date", "last_forecast_date"],
    )
    windows = forecasts[["n_forecasts", "first_forecast_date", "last_forecast_date"]]
    if len(windows.drop_duplicates()) != 1:
        raise ValueError("forecast rows must use the same forecast evaluation dates")


def _require_finite_numeric(df: pd.DataFrame, columns: list[str], context: str) -> None:
    ensure_columns(df, columns)
    for column in columns:
        values = pd.to_numeric(df[column], errors="raise")
        if not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{context} column {column} must contain only finite numeric values")


if __name__ == "__main__":
    main()
