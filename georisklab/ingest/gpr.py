import pandas as pd

from georisklab.utils.validation import (
    assert_no_duplicate_keys,
    ensure_columns,
    standardize_month_start,
)

GPR_COLUMNS = ["gpr_global", "gprt_global", "gpra_global"]


def load_gpr(path_or_url: str) -> pd.DataFrame:
    df = pd.read_csv(path_or_url)
    ensure_columns(df, ["date_month", *GPR_COLUMNS])

    df = df.copy()
    df["date_month"] = standardize_month_start(df["date_month"])
    for column in [*GPR_COLUMNS, "gpr_country"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="raise").astype(float)

    key_columns = ["date_month"]
    if "country_iso3" in df.columns:
        key_columns.append("country_iso3")
    assert_no_duplicate_keys(df, key_columns)

    ordered = ["date_month", *[column for column in df.columns if column != "date_month"]]
    return df[ordered].sort_values(key_columns).reset_index(drop=True)
