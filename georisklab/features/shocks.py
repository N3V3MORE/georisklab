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
