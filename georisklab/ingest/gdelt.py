import numpy as np
import pandas as pd

from georisklab.utils.validation import (
    assert_no_duplicate_keys,
    ensure_columns,
    standardize_month_start,
)

EVENT_TYPES = {
    "conflict": "conflict_count",
    "protest": "protest_count",
    "sanction": "sanction_count",
    "diplomatic_conflict": "diplomatic_conflict_count",
}

OUTPUT_COLUMNS = [
    "date_month",
    "country_iso3",
    "event_count",
    "conflict_count",
    "protest_count",
    "sanction_count",
    "diplomatic_conflict_count",
    "avg_goldstein",
    "avg_tone",
    "risk_index_raw",
    "risk_index_zscore",
    "source_download_date",
    "filter_version",
]


def build_gdelt_country_month(events: pd.DataFrame, filters: dict) -> pd.DataFrame:
    ensure_columns(events, ["event_date", "country_iso3", "event_type"])
    if events.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    df = events.copy()
    df["date_month"] = standardize_month_start(df["event_date"])
    if "goldstein_score" not in df.columns:
        df["goldstein_score"] = np.nan
    if "tone" not in df.columns:
        df["tone"] = np.nan

    keys = ["date_month", "country_iso3"]
    monthly = (
        df.groupby(keys, as_index=False)
        .agg(
            event_count=("event_type", "size"),
            avg_goldstein=("goldstein_score", "mean"),
            avg_tone=("tone", "mean"),
        )
        .sort_values(keys)
    )

    for event_type, output_column in EVENT_TYPES.items():
        counts = (
            df.loc[df["event_type"] == event_type]
            .groupby(keys)
            .size()
            .rename(output_column)
            .reset_index()
        )
        monthly = monthly.merge(counts, on=keys, how="left")
        monthly[output_column] = monthly[output_column].fillna(0).astype(int)

    risk_columns = list(EVENT_TYPES.values())
    monthly["risk_index_raw"] = np.log1p(monthly[risk_columns].sum(axis=1))
    risk_std = monthly["risk_index_raw"].std(ddof=0)
    if risk_std == 0 or pd.isna(risk_std):
        monthly["risk_index_zscore"] = 0.0
    else:
        monthly["risk_index_zscore"] = (
            monthly["risk_index_raw"] - monthly["risk_index_raw"].mean()
        ) / risk_std

    monthly["source_download_date"] = filters.get("source_download_date", "")
    monthly["filter_version"] = filters.get("filter_version", "default")
    assert_no_duplicate_keys(monthly, keys)

    return monthly[OUTPUT_COLUMNS].reset_index(drop=True)
