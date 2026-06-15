import pandas as pd

from georisklab.utils.validation import ensure_columns


def make_forward_returns(
    df: pd.DataFrame,
    horizons: list[int],
    return_col: str = "excess_return",
    group_col: str = "market_id",
) -> pd.DataFrame:
    ensure_columns(df, ["date_month", group_col, return_col])
    result = df.sort_values([group_col, "date_month"]).copy()

    for horizon in horizons:
        column = f"ret_fwd_{horizon}m"
        result[column] = result.groupby(group_col, group_keys=False)[return_col].transform(
            lambda series, h=horizon: _future_cumulative_return(series, h)
        )

    return result.sort_values(["date_month", group_col]).reset_index(drop=True)


def _future_cumulative_return(series: pd.Series, horizon: int) -> pd.Series:
    future = series.shift(-1)
    return future.rolling(horizon, min_periods=horizon).sum().shift(-(horizon - 1))
