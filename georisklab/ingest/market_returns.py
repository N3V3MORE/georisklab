import pandas as pd

from georisklab.utils.validation import (
    assert_no_duplicate_keys,
    ensure_columns,
    standardize_month_start,
)

REQUIRED_COLUMNS = ["date_month", "market_id", "market_class", "return_usd", "source"]


def load_fama_french_market_returns(source: str) -> pd.DataFrame:
    df = pd.read_csv(source)
    ensure_columns(df, REQUIRED_COLUMNS)

    df = df.copy()
    df["date_month"] = standardize_month_start(df["date_month"])
    df["return_usd"] = pd.to_numeric(df["return_usd"], errors="raise").astype(float)
    assert_no_duplicate_keys(df, ["date_month", "market_id"])

    return df[REQUIRED_COLUMNS].sort_values(["date_month", "market_id"]).reset_index(drop=True)
