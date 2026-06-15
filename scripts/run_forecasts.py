# ruff: noqa: E402, I001
from __future__ import annotations

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.models.forecasting import forecast_metric_row  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402


def run_forecasts() -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    panel = pd.read_csv(
        paths.data_processed / "sample_analysis_panel.csv",
        parse_dates=["date_month"],
    )

    target = (
        panel.pivot_table(index="date_month", columns="market_id", values="ret_fwd_1m")
        .assign(spread_fwd_1m=lambda df: df["emerging"] - df["developed"])
        [["spread_fwd_1m"]]
        .reset_index()
    )
    features = panel.drop_duplicates("date_month")[
        ["date_month", "sample_global_cycle", "gpr_global", "gdelt_risk_raw"]
    ]
    forecast_data = target.merge(features, on="date_month").dropna()

    rows = [
        forecast_metric_row("historical_mean", forecast_data, "spread_fwd_1m", [], 120),
        forecast_metric_row(
            "macro_only",
            forecast_data,
            "spread_fwd_1m",
            ["sample_global_cycle"],
            120,
        ),
        forecast_metric_row(
            "macro_plus_gpr",
            forecast_data,
            "spread_fwd_1m",
            ["sample_global_cycle", "gpr_global"],
            120,
            standardize_feature_cols=["gpr_global"],
        ),
        forecast_metric_row(
            "macro_plus_gpr_gdelt",
            forecast_data,
            "spread_fwd_1m",
            ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
            120,
            standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
        ),
        forecast_metric_row(
            "regularized_linear",
            forecast_data,
            "spread_fwd_1m",
            ["sample_global_cycle", "gpr_global", "gdelt_risk_raw"],
            120,
            ridge_alpha=1.0,
            standardize_feature_cols=["gpr_global", "gdelt_risk_raw"],
        ),
    ]
    pd.DataFrame(rows).round(6).to_csv(
        paths.reports_tables / "table_03_forecast_comparison.csv",
        index=False,
    )


def main() -> None:
    run_forecasts()


if __name__ == "__main__":
    main()
