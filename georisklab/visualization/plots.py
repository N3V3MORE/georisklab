import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def plot_gpr_timeseries(df: pd.DataFrame, shock_col: str = "gpr_change_z"):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(df["date_month"], df[shock_col], color="#1f77b4", linewidth=1.8)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_title("Global geopolitical risk change shock")
    ax.set_ylabel("z-score")
    ax.set_xlabel("")
    fig.tight_layout()
    return fig


def plot_market_spread(df: pd.DataFrame):
    spread = df.drop_duplicates("date_month")[["date_month", "spread_em_dev"]]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(spread["date_month"], spread["spread_em_dev"], color="#2ca02c", linewidth=1.6)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_title("Emerging minus developed excess return spread")
    ax.set_ylabel("percentage points")
    ax.set_xlabel("")
    fig.tight_layout()
    return fig


def plot_local_projection(results: pd.DataFrame):
    shock_term = "gpr_change_z" if "gpr_change_z" in set(results["term"]) else "gpr_global_z"
    data = results[results["term"] == shock_term].sort_values("horizon")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.errorbar(
        data["horizon"],
        data["estimate"],
        yerr=1.96 * data["std_error"],
        marker="o",
        color="#d62728",
        capsize=4,
    )
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_title("Spread response to GPR shock")
    ax.set_xlabel("months ahead")
    ax.set_ylabel("estimate")
    fig.tight_layout()
    return fig


def plot_forecast_comparison(metrics: pd.DataFrame):
    data = metrics.sort_values("rmse")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(data["model"], data["rmse"], color="#9467bd")
    ax.set_title("Forecast comparison")
    ax.set_xlabel("RMSE")
    fig.tight_layout()
    return fig


def plot_gdelt_vs_gpr(df: pd.DataFrame):
    data = df.drop_duplicates("date_month")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(data["date_month"], data["gpr_global_z"], label="GPR", linewidth=1.6)
    ax.plot(data["date_month"], data["gdelt_risk_z"], label="GDELT risk", linewidth=1.6)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_title("GDELT risk index versus benchmark GPR")
    ax.set_ylabel("z-score")
    ax.set_xlabel("")
    ax.legend()
    fig.tight_layout()
    return fig
