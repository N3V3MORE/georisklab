# ruff: noqa: E402, I001
from __future__ import annotations

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.features.panel import build_analysis_panel  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402


def build_features() -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()

    market_returns = pd.read_csv(
        paths.data_processed / "sample_market_returns_monthly.csv",
        parse_dates=["date_month"],
    )
    gpr = pd.read_csv(paths.data_processed / "sample_gpr_monthly.csv", parse_dates=["date_month"])
    gdelt = pd.read_csv(
        paths.data_processed / "sample_gdelt_country_monthly.csv",
        parse_dates=["date_month"],
    )
    macro = pd.read_csv(
        paths.data_processed / "sample_macro_controls_monthly.csv",
        parse_dates=["date_month"],
    )

    panel = build_analysis_panel(market_returns, gpr, gdelt, macro)
    panel.to_csv(paths.data_processed / "sample_analysis_panel.csv", index=False)

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


def main() -> None:
    build_features()


if __name__ == "__main__":
    main()
