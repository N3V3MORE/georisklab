# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.models.forecasting import ForecastModelSpec, forecast_metric_rows  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.outputs import table_path  # noqa: E402


def run_forecasts(
    dataset: str = "sample",
    root: Path | None = None,
    min_train_months: int = 120,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel = pd.read_csv(paths.data_processed / panel_name, parse_dates=["date_month"])

    target = (
        panel.pivot_table(index="date_month", columns="market_id", values="ret_fwd_1m")
        .assign(spread_fwd_1m=lambda df: df["emerging"] - df["developed"])
        [["spread_fwd_1m"]]
        .reset_index()
    )
    if dataset == "sample":
        feature_cols = ["date_month", "sample_global_cycle", "gpr_global", "gdelt_risk_raw"]
    else:
        feature_cols = ["date_month", "gpr_change"]
    features = panel.drop_duplicates("date_month")[feature_cols]
    forecast_data = target.merge(features, on="date_month").dropna()

    rows = _forecast_rows(forecast_data, dataset, min_train_months)
    pd.DataFrame(rows).round(6).to_csv(
        table_path(paths, "table_03_forecast_comparison.csv", dataset),
        index=False,
    )


def _forecast_rows(
    forecast_data: pd.DataFrame,
    dataset: str,
    min_train_months: int,
) -> list[dict]:
    if dataset == "real":
        return forecast_metric_rows(
            forecast_data,
            "spread_fwd_1m",
            [
                ForecastModelSpec("historical_mean", []),
                ForecastModelSpec(
                    "gpr_only",
                    ["gpr_change"],
                    standardize_feature_cols=["gpr_change"],
                ),
                ForecastModelSpec(
                    "regularized_gpr_only",
                    ["gpr_change"],
                    ridge_alpha=1.0,
                    standardize_feature_cols=["gpr_change"],
                ),
            ],
            min_train_months,
        )

    return forecast_metric_rows(
        forecast_data,
        "spread_fwd_1m",
        [
            ForecastModelSpec(
                "historical_mean",
                [],
            ),
            ForecastModelSpec("macro_only", ["sample_global_cycle"]),
            ForecastModelSpec(
                "macro_plus_gpr",
                ["sample_global_cycle", "gpr_global"],
                standardize_feature_cols=["gpr_global"],
            ),
            ForecastModelSpec(
                "macro_plus_gpr_gdelt",
                ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
                standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
            ),
            ForecastModelSpec(
                "regularized_linear",
                ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
                ridge_alpha=1.0,
                standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
            ),
        ],
        min_train_months,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GeoRiskLab forecasts.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    parser.add_argument("--min-train-months", type=int, default=120)
    args = parser.parse_args()
    run_forecasts(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        min_train_months=args.min_train_months,
    )


if __name__ == "__main__":
    main()
