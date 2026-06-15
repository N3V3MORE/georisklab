# ruff: noqa: E402, I001
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402


def build_report() -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    summary = pd.read_csv(paths.reports_tables / "table_01_summary_stats.csv")
    forecasts = pd.read_csv(paths.reports_tables / "table_03_forecast_comparison.csv")

    with PdfPages(paths.root / "reports" / "main_report.pdf") as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.1, 0.92, "GeoRiskLab Sample Report", fontsize=18, weight="bold")
        fig.text(
            0.1,
            0.86,
            "This report is generated from deterministic sample data. It verifies the "
            "pipeline and does not claim empirical findings.",
            fontsize=10,
            wrap=True,
        )
        fig.text(0.1, 0.78, "Summary statistics", fontsize=13, weight="bold")
        fig.text(0.1, 0.73, summary.to_string(index=False), fontsize=8, family="monospace")
        fig.text(0.1, 0.55, "Forecast comparison", fontsize=13, weight="bold")
        fig.text(
            0.1,
            0.5,
            forecasts[["model", "rmse", "mae", "oos_r2"]].to_string(index=False),
            fontsize=8,
            family="monospace",
        )
        fig.text(
            0.1,
            0.25,
            "Limitations: sample data are synthetic, source APIs are not queried by "
            "default, and causal claims require stronger identification than this "
            "sample pipeline provides.",
            fontsize=10,
            wrap=True,
        )
        pdf.savefig(fig)
        plt.close(fig)


def main() -> None:
    build_report()


if __name__ == "__main__":
    main()
