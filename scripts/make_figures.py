# ruff: noqa: E402, I001
from __future__ import annotations

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.visualization.plots import (  # noqa: E402
    plot_forecast_comparison,
    plot_gdelt_vs_gpr,
    plot_gpr_timeseries,
    plot_local_projection,
    plot_market_spread,
)


def make_figures() -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    panel = pd.read_csv(
        paths.data_processed / "sample_analysis_panel.csv",
        parse_dates=["date_month"],
    )
    regressions = pd.read_csv(paths.reports_tables / "table_02_baseline_regressions.csv")
    forecasts = pd.read_csv(paths.reports_tables / "table_03_forecast_comparison.csv")

    figures = {
        "fig_01_gpr_timeseries.png": plot_gpr_timeseries(panel),
        "fig_02_em_dev_spread.png": plot_market_spread(panel),
        "fig_03_local_projection.png": plot_local_projection(regressions),
        "fig_04_gdelt_vs_gpr.png": plot_gdelt_vs_gpr(panel),
        "fig_05_forecast_comparison.png": plot_forecast_comparison(forecasts),
    }
    for filename, figure in figures.items():
        figure.savefig(paths.reports_figures / filename, dpi=160)


def main() -> None:
    make_figures()


if __name__ == "__main__":
    main()
