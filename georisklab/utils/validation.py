import pandas as pd


def ensure_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"missing required columns: {names}")


def standardize_month_start(values: pd.Series) -> pd.Series:
    dates = pd.to_datetime(values, errors="raise")
    return dates.dt.to_period("M").dt.to_timestamp()
