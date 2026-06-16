# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402


def build_report(dataset: str = "sample", root: Path | None = None) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    summary = pd.read_csv(paths.reports_tables / "table_01_summary_stats.csv")
    forecasts = pd.read_csv(paths.reports_tables / "table_03_forecast_comparison.csv")
    text = report_text(dataset)

    with PdfPages(paths.root / "reports" / "main_report.pdf") as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.1, 0.92, text["title"], fontsize=18, weight="bold")
        fig.text(
            0.1,
            0.86,
            text["note"],
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
            text["limitations"],
            fontsize=10,
            wrap=True,
        )
        pdf.savefig(fig)
        plt.close(fig)


def report_text(dataset: str) -> dict[str, str]:
    if dataset == "sample":
        return {
            "title": "GeoRiskLab Sample Report",
            "note": (
                "This report is generated from deterministic sample data. It verifies "
                "the pipeline and does not claim empirical findings."
            ),
            "limitations": (
                "Limitations: sample data are synthetic, source APIs are not queried by "
                "default, and causal claims require stronger identification than this "
                "sample pipeline provides."
            ),
        }
    if dataset == "real":
        return {
            "title": "GeoRiskLab Real-Data V0.1 Report",
            "note": (
                "This report is generated from user-supplied local raw data for real "
                "GPR and developed/emerging Fama-French return inputs."
            ),
            "limitations": (
                "Limitations: V0.1 uses real GPR and aggregate developed/emerging "
                "returns only. Real GDELT event intensity and macro controls are later "
                "milestones, so causal claims remain out of scope."
            ),
        }
    raise ValueError("dataset must be 'sample' or 'real'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the GeoRiskLab PDF report.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    build_report(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
    )


if __name__ == "__main__":
    main()
