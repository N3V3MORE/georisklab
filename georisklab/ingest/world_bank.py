import json
from urllib.parse import quote
from urllib.request import urlopen

import pandas as pd

from georisklab.utils.validation import assert_no_duplicate_keys


def load_world_bank_indicator(indicator: str, countries: list[str]) -> pd.DataFrame:
    country_part = ";".join(quote(country, safe="") for country in countries)
    url = (
        "https://api.worldbank.org/v2/country/"
        f"{country_part}/indicator/{quote(indicator, safe='')}?format=json&per_page=20000"
    )

    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    rows = payload[1] if len(payload) > 1 and payload[1] else []
    records = []
    for row in rows:
        if row.get("value") is None:
            continue
        records.append(
            {
                "date_month": pd.Timestamp(f"{row['date']}-01-01"),
                "country_iso3": row.get("countryiso3code", ""),
                "indicator_code": row.get("indicator", {}).get("id", indicator),
                "value": float(row["value"]),
            }
        )

    df = pd.DataFrame(records, columns=["date_month", "country_iso3", "indicator_code", "value"])
    assert_no_duplicate_keys(df, ["date_month", "country_iso3", "indicator_code"])
    return df
