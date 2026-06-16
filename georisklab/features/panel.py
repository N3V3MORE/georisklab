import pandas as pd

from georisklab.features.returns import make_forward_returns
from georisklab.features.shocks import make_gpr_shock_features
from georisklab.utils.validation import ensure_columns


def build_analysis_panel(
    market_returns: pd.DataFrame,
    gpr: pd.DataFrame,
    gdelt: pd.DataFrame,
    macro_controls: pd.DataFrame,
) -> pd.DataFrame:
    ensure_columns(market_returns, ["date_month", "market_id", "market_class", "excess_return"])
    ensure_columns(gpr, ["date_month", "gpr_global", "gprt_global", "gpra_global"])
    ensure_columns(gdelt, ["date_month", "risk_index_zscore"])
    ensure_columns(macro_controls, ["date_month", "indicator_code", "value"])

    panel = make_forward_returns(market_returns, [1, 3, 6])
    gpr_features = make_gpr_shock_features(gpr)
    gdelt_features = gdelt[["date_month", "risk_index_raw", "risk_index_zscore"]].rename(
        columns={"risk_index_raw": "gdelt_risk_raw", "risk_index_zscore": "gdelt_risk_z"}
    )
    macro_wide = (
        macro_controls.pivot_table(
            index="date_month",
            columns="indicator_code",
            values="value",
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(columns=None)
    )

    spread = (
        panel.pivot_table(index="date_month", columns="market_id", values="excess_return")
        .assign(spread_em_dev=lambda df: df["emerging"] - df["developed"])
        [["spread_em_dev"]]
        .reset_index()
    )

    panel = (
        panel.merge(
            gpr_features[
                [
                    "date_month",
                    "gpr_global",
                    "gprt_global",
                    "gpra_global",
                    "gpr_level_z",
                    "gpr_global_z",
                    "gpr_change",
                    "gpr_change_z",
                    "gpr_log_change",
                    "gpr_log_change_z",
                    "gpr_ar1_residual",
                    "gpr_ar1_residual_z",
                    "gprt_global_z",
                    "gpra_global_z",
                ]
            ],
            on="date_month",
            how="left",
        )
        .merge(gdelt_features, on="date_month", how="left")
        .merge(macro_wide, on="date_month", how="left")
        .merge(spread, on="date_month", how="left")
    )
    panel["neg_ret_1m"] = (panel["ret_fwd_1m"] < 0).astype(int)
    tail_cutoff = panel["ret_fwd_1m"].quantile(0.1)
    panel["left_tail_1m"] = (panel["ret_fwd_1m"] < tail_cutoff).astype(int)

    return panel.sort_values(["date_month", "market_id"]).reset_index(drop=True)
