import numpy as np
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

    x = data[[shock_col, interaction_col, *controls]].astype(float)
    y = data[target_col].astype(float)
    fixed_effect_groups = []
    if config.get("market_fixed_effects", False):
        fixed_effect_groups.append(data["market_id"])
    if config.get("time_fixed_effects", False):
        fixed_effect_groups.append(data["date_month"])

    if fixed_effect_groups:
        x = _absorb_fixed_effects(x, fixed_effect_groups)
        y = _absorb_fixed_effects(y.to_frame(target_col), fixed_effect_groups)[target_col]
    else:
        x = sm.add_constant(x, has_constant="add")

    fitted = sm.OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": data["market_id"]})

    return _to_result(fitted, {"horizon": horizon, "model": "panel_interaction"}, "clustered")


def _absorb_fixed_effects(
    values: pd.DataFrame,
    groups: list[pd.Series],
    max_iter: int = 100,
    tolerance: float = 1e-10,
) -> pd.DataFrame:
    residual = values.copy()
    for _ in range(max_iter):
        previous = residual.to_numpy(copy=True)
        for group in groups:
            residual = residual - residual.groupby(group, sort=False).transform("mean")
        change = np.max(np.abs(residual.to_numpy() - previous))
        if change < tolerance:
            break
    return residual


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
