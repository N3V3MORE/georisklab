import pandas as pd

from georisklab.utils.validation import ensure_columns


def standardize_shocks(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    ensure_columns(df, cols)
    result = df.copy()

    for column in cols:
        values = pd.to_numeric(result[column], errors="raise")
        std = values.std(ddof=0)
        if std == 0 or pd.isna(std):
            result[f"{column}_z"] = 0.0
        else:
            result[f"{column}_z"] = (values - values.mean()) / std

    return result


def expanding_standardize_shocks(
    df: pd.DataFrame,
    cols: list[str],
    date_col: str = "date_month",
    group_cols: list[str] | None = None,
    min_periods: int = 24,
) -> pd.DataFrame:
    ensure_columns(df, [date_col, *cols, *(group_cols or [])])
    result = df.copy()
    result["_original_order"] = range(len(result))

    sort_cols = [*(group_cols or []), date_col]
    result = result.sort_values(sort_cols)
    for column in cols:
        if group_cols:
            result[f"{column}_z"] = result.groupby(group_cols, group_keys=False)[column].transform(
                lambda series: _prior_expanding_zscore(series, min_periods)
            )
        else:
            result[f"{column}_z"] = _prior_expanding_zscore(result[column], min_periods)

    return (
        result.sort_values("_original_order")
        .drop(columns=["_original_order"])
        .reset_index(drop=True)
    )


def _prior_expanding_zscore(series: pd.Series, min_periods: int) -> pd.Series:
    values = pd.to_numeric(series, errors="raise")
    prior_count = values.expanding(min_periods=1).count().shift(1)
    has_history = prior_count >= min_periods
    mean = values.expanding(min_periods=min_periods).mean().shift(1)
    std = values.expanding(min_periods=min_periods).std(ddof=0).shift(1)
    zscore = (values - mean) / std
    zscore = zscore.replace([float("inf"), float("-inf")], pd.NA)
    return zscore.where(~(has_history & zscore.isna()), 0.0).where(has_history)
