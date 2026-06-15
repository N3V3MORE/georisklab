# ruff: noqa: E402, I001
from __future__ import annotations

import argparse

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.features.panel import build_analysis_panel  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402


def build_features(dataset: str = "sample") -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    files = _dataset_files(dataset)

    market_returns = pd.read_csv(
        paths.data_processed / files["market_returns"],
        parse_dates=["date_month"],
    )
    gpr = pd.read_csv(paths.data_processed / files["gpr"], parse_dates=["date_month"])
    gdelt = _read_optional_gdelt(paths.data_processed / files["gdelt"], gpr)
    macro = _read_optional_macro(paths.data_processed / files["macro"], gpr)

    panel = build_analysis_panel(market_returns, gpr, gdelt, macro)
    panel.to_csv(paths.data_processed / files["analysis_panel"], index=False)

    summary = (
        panel.groupby("market_class", as_index=False)
        .agg(
            observations=("excess_return", "count"),
            mean_excess_return=("excess_return", "mean"),
            mean_next_month_return=("ret_fwd_1m", "mean"),
            negative_next_month_share=("neg_ret_1m", "mean"),
        )
        .round(4)
    )
    summary.to_csv(paths.reports_tables / "table_01_summary_stats.csv", index=False)


def _dataset_files(dataset: str) -> dict[str, str]:
    if dataset == "sample":
        return {
            "gpr": "sample_gpr_monthly.csv",
            "market_returns": "sample_market_returns_monthly.csv",
            "gdelt": "sample_gdelt_country_monthly.csv",
            "macro": "sample_macro_controls_monthly.csv",
            "analysis_panel": "sample_analysis_panel.csv",
        }
    if dataset == "real":
        return {
            "gpr": "gpr_monthly.csv",
            "market_returns": "market_returns_monthly.csv",
            "gdelt": "gdelt_country_monthly.csv",
            "macro": "macro_controls_monthly.csv",
            "analysis_panel": "analysis_panel.csv",
        }
    raise ValueError("dataset must be 'sample' or 'real'")


def _read_optional_gdelt(path, gpr: pd.DataFrame) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, parse_dates=["date_month"])
    return pd.DataFrame(
        {
            "date_month": gpr["date_month"],
            "country_iso3": "GLB",
            "risk_index_raw": 0.0,
            "risk_index_zscore": 0.0,
        }
    )


def _read_optional_macro(path, gpr: pd.DataFrame) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, parse_dates=["date_month"])
    return pd.DataFrame(
        {
            "date_month": gpr["date_month"],
            "country_iso3": "GLB",
            "indicator_code": "sample_global_cycle",
            "value": 0.0,
            "frequency_original": "not_available",
            "frequency_converted": "monthly",
            "source": "real_pipeline_placeholder",
            "source_download_date": "",
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GeoRiskLab features.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    args = parser.parse_args()
    build_features(dataset=args.dataset)


if __name__ == "__main__":
    main()
