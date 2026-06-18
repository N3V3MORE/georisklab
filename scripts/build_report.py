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
from georisklab.utils.outputs import report_path, table_path  # noqa: E402


def build_report(
    dataset: str = "sample",
    root: Path | None = None,
    shock_col: str | None = None,
) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    panel_name = "sample_analysis_panel.csv" if dataset == "sample" else "analysis_panel.csv"
    panel = pd.read_csv(paths.data_processed / panel_name, parse_dates=["date_month"])
    summary = pd.read_csv(table_path(paths, "table_01_summary_stats.csv", dataset))
    regressions = pd.read_csv(table_path(paths, "table_02_baseline_regressions.csv", dataset))
    forecasts = pd.read_csv(table_path(paths, "table_03_forecast_comparison.csv", dataset))
    text = report_text(dataset)
    metrics = report_metrics(panel, regressions, shock_col or "gpr_change_z")

    with PdfPages(report_path(paths, dataset)) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.1, 0.92, text["title"], fontsize=18, weight="bold")
        fig.text(
            0.1,
            0.86,
            text["note"],
            fontsize=10,
            wrap=True,
        )
        fig.text(0.1, 0.79, "Empirical summary", fontsize=13, weight="bold")
        fig.text(0.1, 0.74, _metrics_block(metrics), fontsize=8, family="monospace")
        fig.text(0.1, 0.57, "Baseline regression", fontsize=13, weight="bold")
        fig.text(0.1, 0.52, _baseline_block(metrics), fontsize=8, family="monospace")
        fig.text(0.1, 0.44, "Horizon response", fontsize=13, weight="bold")
        fig.text(0.1, 0.39, _horizon_block(metrics), fontsize=7, family="monospace")
        fig.text(0.1, 0.31, "Interpretation", fontsize=13, weight="bold")
        fig.text(0.1, 0.27, metrics["interpretation"], fontsize=8, wrap=True)
        fig.text(0.1, 0.21, "Summary statistics", fontsize=13, weight="bold")
        fig.text(0.1, 0.16, summary.to_string(index=False), fontsize=6, family="monospace")
        fig.text(0.1, 0.10, "Forecast comparison", fontsize=13, weight="bold")
        fig.text(
            0.1,
            0.06,
            forecasts[["model", "rmse", "mae", "oos_r2"]].to_string(index=False),
            fontsize=6,
            family="monospace",
        )
        fig.text(
            0.1,
            0.02,
            text["limitations"],
            fontsize=6,
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
                "This report is generated from verified real source data for GPR and "
                "developed/emerging Fama-French return inputs."
            ),
            "limitations": (
                "Limitations: V0.1 uses real GPR and aggregate developed/emerging "
                "returns only. Real GDELT event intensity and macro controls are later "
                "milestones, so causal claims remain out of scope."
            ),
        }
    raise ValueError("dataset must be 'sample' or 'real'")


def report_metrics(panel: pd.DataFrame, regressions: pd.DataFrame, shock_col: str) -> dict:
    dates = _report_sample_dates(panel, shock_col)
    means = panel.groupby("market_id")["excess_return"].mean()
    spread = panel.drop_duplicates("date_month")["spread_em_dev"].mean()
    baseline = _baseline_row(regressions, shock_col)
    estimate = float(baseline["estimate"])
    std_error = float(baseline["std_error"])
    lower = round(estimate - 1.96 * std_error, 3)
    upper = round(estimate + 1.96 * std_error, 3)
    return {
        "sample_period": f"{dates.min().date().isoformat()} to {dates.max().date().isoformat()}",
        "n_months": int(len(dates)),
        "mean_emerging_return": round(float(means["emerging"]), 4),
        "mean_developed_return": round(float(means["developed"]), 4),
        "mean_spread_em_dev": round(float(spread), 4),
        "baseline_coefficient": round(estimate, 4),
        "baseline_std_error": round(std_error, 4),
        "baseline_p_value": round(float(baseline["p_value"]), 4),
        "confidence_interval_95": (lower, upper),
        "horizon_regressions": _horizon_rows(regressions, shock_col),
        "interpretation": _interpret_regression(estimate, shock_col),
    }


def _report_sample_dates(panel: pd.DataFrame, shock_col: str) -> pd.Series:
    target_col = "ret_fwd_1m"
    if {target_col, shock_col}.issubset(panel.columns):
        dates = (
            pd.to_datetime(
                panel.loc[panel[target_col].notna() & panel[shock_col].notna(), "date_month"]
            )
            .drop_duplicates()
            .sort_values()
        )
        if not dates.empty:
            return dates
    return pd.to_datetime(panel["date_month"]).drop_duplicates().sort_values()


def _baseline_row(regressions: pd.DataFrame, shock_col: str) -> pd.Series:
    rows = regressions[(regressions["horizon"] == 1) & (regressions["term"] == shock_col)]
    if rows.empty:
        raise ValueError(f"baseline regression table has no horizon-1 row for {shock_col}")
    return rows.iloc[0]


def _interpret_regression(estimate: float, shock_col: str) -> str:
    direction = "lower" if estimate < 0 else "higher"
    magnitude = abs(round(estimate, 3))
    return (
        f"A one standard deviation increase in {shock_col} is associated with a "
        f"{direction} EM minus developed spread of {magnitude} percentage points "
        "over the next month. This is descriptive, not causal."
    )


def _metrics_block(metrics: dict) -> str:
    rows = [
        ("Sample period", metrics["sample_period"]),
        ("Months", metrics["n_months"]),
        ("Mean EM excess return", metrics["mean_emerging_return"]),
        ("Mean developed excess return", metrics["mean_developed_return"]),
        ("Mean EM-developed spread", metrics["mean_spread_em_dev"]),
    ]
    return "\n".join(f"{label}: {value}" for label, value in rows)


def _baseline_block(metrics: dict) -> str:
    rows = [
        ("Coefficient", metrics["baseline_coefficient"]),
        ("Std. error", metrics["baseline_std_error"]),
        ("p-value", metrics["baseline_p_value"]),
        ("95% CI", metrics["confidence_interval_95"]),
    ]
    return "\n".join(f"{label}: {value}" for label, value in rows)


def _horizon_rows(regressions: pd.DataFrame, shock_col: str) -> list[dict]:
    rows = []
    data = regressions[regressions["term"] == shock_col].sort_values("horizon")
    for _, row in data.iterrows():
        estimate = round(float(row["estimate"]), 4)
        std_error = round(float(row["std_error"]), 4)
        rows.append(
            {
                "horizon": f"{int(row['horizon'])}m",
                "estimate": estimate,
                "std_error": std_error,
                "p_value": round(float(row["p_value"]), 4),
                "confidence_interval_95": (
                    round(estimate - 1.96 * std_error, 3),
                    round(estimate + 1.96 * std_error, 3),
                ),
            }
        )
    return rows


def _horizon_block(metrics: dict) -> str:
    rows = ["Horizon | Estimate | Std. error | p-value | 95% CI"]
    for row in metrics["horizon_regressions"]:
        rows.append(
            f"{row['horizon']:>7} | {row['estimate']:>8} | {row['std_error']:>10} | "
            f"{row['p_value']:>7} | {row['confidence_interval_95']}"
        )
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the GeoRiskLab PDF report.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    parser.add_argument("--shock-col", default=None)
    args = parser.parse_args()
    build_report(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
        shock_col=args.shock_col,
    )


if __name__ == "__main__":
    main()
