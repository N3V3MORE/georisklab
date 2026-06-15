import zipfile
from io import StringIO

import numpy as np
import pandas as pd

from georisklab.utils.validation import (
    assert_no_duplicate_keys,
    ensure_columns,
    standardize_month_start,
)

RETURN_COLUMNS = ["return_usd", "risk_free_rate", "excess_return"]
REQUIRED_COLUMNS = [
    "date_month",
    "market_id",
    "market_class",
    *RETURN_COLUMNS,
    "source",
]


def load_fama_french_market_returns(source: str) -> pd.DataFrame:
    df = pd.read_csv(source)
    return _normalize_market_returns(df)


def load_fama_french_factor_returns(
    source: str,
    market_id: str,
    market_class: str,
    source_name: str = "kenneth_french",
) -> pd.DataFrame:
    text = _read_text_source(source)
    rows = _extract_fama_french_monthly_rows(text)
    df = pd.DataFrame(rows, columns=["date_month", "excess_return", "risk_free_rate"])
    df["market_id"] = market_id
    df["market_class"] = market_class
    df["return_usd"] = df["excess_return"] + df["risk_free_rate"]
    df["source"] = source_name
    return _normalize_market_returns(df)


def _normalize_market_returns(df: pd.DataFrame) -> pd.DataFrame:
    ensure_columns(df, REQUIRED_COLUMNS)

    df = df.copy()
    df["date_month"] = standardize_month_start(df["date_month"])
    for column in RETURN_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise").astype(float)

    for column in RETURN_COLUMNS:
        if (df[column] <= -99).any():
            raise ValueError(f"{column} contains Fama-French missing-value sentinel")

    expected_return = df["excess_return"] + df["risk_free_rate"]
    if not np.allclose(df["return_usd"], expected_return, atol=1e-8):
        raise ValueError("return_usd must equal excess_return + risk_free_rate")

    assert_no_duplicate_keys(df, ["date_month", "market_id"])

    return df[REQUIRED_COLUMNS].sort_values(["date_month", "market_id"]).reset_index(drop=True)


def _read_text_source(source: str) -> str:
    if source.lower().endswith(".zip"):
        with zipfile.ZipFile(source) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise ValueError("Fama-French zip file contains no CSV file")
            return archive.read(csv_names[0]).decode("utf-8-sig")
    return pd.io.common.get_handle(source, mode="r").handle.read()


def _extract_fama_french_monthly_rows(text: str) -> list[tuple[pd.Timestamp, float, float]]:
    lines = text.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if "Mkt-RF" in line and "RF" in line.split(",")
        ),
        None,
    )
    if header_index is None:
        raise ValueError("Fama-French file does not contain Mkt-RF and RF columns")

    table = pd.read_csv(StringIO("\n".join(lines[header_index:])))
    first_column = table.columns[0]
    rows = []
    for _, row in table.iterrows():
        raw_date = str(row[first_column]).strip()
        if not raw_date.isdigit() or len(raw_date) != 6:
            break
        excess_return = float(row["Mkt-RF"])
        risk_free_rate = float(row["RF"])
        if excess_return <= -99 or risk_free_rate <= -99:
            raise ValueError("Fama-French file contains missing-value sentinel")
        rows.append(
            (
                pd.Timestamp(f"{raw_date[:4]}-{raw_date[4:]}-01"),
                excess_return,
                risk_free_rate,
            )
        )
    return rows
