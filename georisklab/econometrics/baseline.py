import pandas as pd
import statsmodels.api as sm

from georisklab.econometrics.results import RegressionResult
from georisklab.utils.validation import ensure_columns


def run_spread_regression(panel: pd.DataFrame, horizon: int, config: dict) -> RegressionResult:
    shock_col = config.get("shock_col", "gpr_global_z")
    controls = config.get("controls", [])
    target_col = f"ret_fwd_{horizon}m"
    ensure_columns(panel, ["date_month", "market_id", target_col, shock_col, *controls])

    spread = (
        panel.pivot_table(index="date_month", columns="market_id", values=target_col)
        .assign(spread_fwd=lambda df: df["emerging"] - df["developed"])
        [["spread_fwd"]]
        .reset_index()
    )
    predictors = panel.drop_duplicates("date_month")[["date_month", shock_col, *controls]]
    data = spread.merge(predictors, on="date_month").dropna()

    x = sm.add_constant(data[[shock_col, *controls]], has_constant="add")
    y = data["spread_fwd"]
    fitted = sm.OLS(y, x).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": int(config.get("maxlags", max(1, horizon)))},
    )

    return _to_result(fitted, {"horizon": horizon, "model": "spread"}, "HAC")


def run_panel_interaction(panel: pd.DataFrame, horizon: int, config: dict) -> RegressionResult:
    shock_col = config.get("shock_col", "gpr_global_z")
    controls = config.get("controls", [])
    target_col = f"ret_fwd_{horizon}m"
    ensure_columns(
        panel,
        ["date_month", "market_id", "market_class", target_col, shock_col, *controls],
    )

    data = panel.dropna(subset=[target_col, shock_col, *controls]).copy()
    data["emerging"] = (data["market_class"] == "emerging").astype(float)
    interaction_col = f"emerging_x_{shock_col}"
    data[interaction_col] = data["emerging"] * data[shock_col]

    x_parts = [data[[shock_col, interaction_col, *controls]]]
    if config.get("market_fixed_effects", False):
        x_parts.append(pd.get_dummies(data["market_id"], prefix="market", drop_first=True))
    if config.get("time_fixed_effects", False):
        x_parts.append(
            pd.get_dummies(data["date_month"].astype(str), prefix="month", drop_first=True)
        )

    x = sm.add_constant(pd.concat(x_parts, axis=1).astype(float), has_constant="add")
    y = data[target_col]
    fitted = sm.OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": data["market_id"]})

    return _to_result(fitted, {"horizon": horizon, "model": "panel_interaction"}, "clustered")


def _to_result(fitted, metadata: dict, se_type: str) -> RegressionResult:
    coefficients = pd.DataFrame(
        {
            "term": fitted.params.index,
            "estimate": fitted.params.to_numpy(),
            "std_error": fitted.bse.to_numpy(),
            "t_value": fitted.tvalues.to_numpy(),
            "p_value": fitted.pvalues.to_numpy(),
        }
    )
    return RegressionResult(
        coefficients=coefficients,
        metadata=metadata,
        nobs=int(fitted.nobs),
        adjusted_r2=float(fitted.rsquared_adj),
        se_type=se_type,
    )
