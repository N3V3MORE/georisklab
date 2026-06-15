import json
from io import BytesIO

import pandas as pd
import pytest

from georisklab.ingest.gdelt import build_gdelt_country_month
from georisklab.ingest.gpr import load_gpr
from georisklab.ingest.market_returns import load_fama_french_market_returns
from georisklab.ingest.world_bank import load_world_bank_indicator


def test_load_gpr_standardizes_dates_and_numeric_columns(tmp_path):
    path = tmp_path / "gpr.csv"
    path.write_text(
        "date_month,gpr_global,gprt_global,gpra_global\n"
        "2020-01-31,100,70,30\n"
        "2020-02-15,110,80,30\n"
    )

    df = load_gpr(str(path))

    assert df["date_month"].tolist() == [
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-02-01"),
    ]
    assert df["gpr_global"].tolist() == [100.0, 110.0]


def test_load_gpr_rejects_duplicate_month_keys(tmp_path):
    path = tmp_path / "gpr.csv"
    path.write_text(
        "date_month,gpr_global,gprt_global,gpra_global\n"
        "2020-01-01,100,70,30\n"
        "2020-01-15,101,71,30\n"
    )

    with pytest.raises(ValueError, match="duplicate keys"):
        load_gpr(str(path))


def test_load_market_returns_standardizes_required_fields(tmp_path):
    path = tmp_path / "returns.csv"
    path.write_text(
        "date_month,market_id,market_class,return_usd,source\n"
        "2020-01-31,developed,developed,1.25,test\n"
        "2020-01-31,emerging,emerging,-2.5,test\n"
    )

    df = load_fama_french_market_returns(str(path))

    assert df["date_month"].tolist() == [pd.Timestamp("2020-01-01")] * 2
    assert df["return_usd"].tolist() == [1.25, -2.5]


def test_build_gdelt_country_month_counts_documented_event_types():
    events = pd.DataFrame(
        {
            "event_date": ["2020-01-03", "2020-01-15", "2020-02-02", "2020-02-20"],
            "country_iso3": ["USA", "USA", "USA", "USA"],
            "event_type": ["conflict", "protest", "sanction", "diplomatic_conflict"],
            "goldstein_score": [-5.0, -1.0, -3.0, 1.0],
            "tone": [-2.0, -1.0, -3.0, 0.5],
        }
    )

    df = build_gdelt_country_month(events, {"filter_version": "test-v1"})

    jan = df.loc[df["date_month"] == pd.Timestamp("2020-01-01")].iloc[0]
    feb = df.loc[df["date_month"] == pd.Timestamp("2020-02-01")].iloc[0]
    assert jan["event_count"] == 2
    assert jan["conflict_count"] == 1
    assert jan["protest_count"] == 1
    assert feb["sanction_count"] == 1
    assert feb["diplomatic_conflict_count"] == 1
    assert set(df["filter_version"]) == {"test-v1"}


def test_load_world_bank_indicator_parses_country_values(monkeypatch):
    payload = [
        {"page": 1, "pages": 1},
        [
            {
                "date": "2020",
                "countryiso3code": "USA",
                "indicator": {"id": "FP.CPI.TOTL.ZG"},
                "value": 1.2,
            }
        ],
    ]

    class Response(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    def fake_urlopen(url, timeout=30):
        assert "FP.CPI.TOTL.ZG" in url
        return Response(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr("georisklab.ingest.world_bank.urlopen", fake_urlopen)

    df = load_world_bank_indicator("FP.CPI.TOTL.ZG", ["USA"])

    assert df.to_dict("records") == [
        {
            "date": pd.Timestamp("2020-01-01"),
            "country_iso3": "USA",
            "indicator_code": "FP.CPI.TOTL.ZG",
            "value": 1.2,
        }
    ]
