import json
from urllib.parse import quote
from urllib.request import urlopen

import pandas as pd


def load_world_bank_indicator(indicator: str, countries: list[str]) -> pd.DataFrame:
    country_part = ";".join(countries)
    url = (
        "https://api.worldbank.org/v2/country/"
        f"{quote(country_part)}/indicator/{quote(indicator)}?format=json&per_page=20000"
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
                "date": pd.Timestamp(f"{row['date']}-01-01"),
                "country_iso3": row.get("countryiso3code", ""),
                "indicator_code": row.get("indicator", {}).get("id", indicator),
                "value": float(row["value"]),
            }
        )

    return pd.DataFrame(records, columns=["date", "country_iso3", "indicator_code", "value"])
