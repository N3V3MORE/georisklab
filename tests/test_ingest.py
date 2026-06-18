import json
import zipfile
from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from georisklab.ingest import market_returns
from georisklab.ingest.gdelt import build_gdelt_country_month
from georisklab.ingest.gpr import load_caldara_iacoviello_gpr, load_gpr
from georisklab.ingest.market_returns import (
    load_fama_french_factor_returns,
    load_fama_french_market_returns,
)
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
        "date_month,market_id,market_class,return_usd,risk_free_rate,excess_return,source,"
        "source_download_date\n"
        "2020-01-31,developed,developed,1.25,0.05,1.20,test,2026-06-15\n"
        "2020-01-31,emerging,emerging,-2.5,0.05,-2.55,test,2026-06-15\n"
    )

    df = load_fama_french_market_returns(str(path))

    assert df["date_month"].tolist() == [pd.Timestamp("2020-01-01")] * 2
    assert df["return_usd"].tolist() == [1.25, -2.5]
    assert df["excess_return"].tolist() == [1.2, -2.55]


def test_load_market_returns_rejects_formula_mismatch(tmp_path):
    path = tmp_path / "returns.csv"
    path.write_text(
        "date_month,market_id,market_class,return_usd,risk_free_rate,excess_return,source,"
        "source_download_date\n"
        "2020-01-31,developed,developed,1.25,0.05,2.00,test,2026-06-15\n"
    )

    with pytest.raises(ValueError, match="return_usd must equal"):
        load_fama_french_market_returns(str(path))


def test_load_caldara_iacoviello_gpr_maps_real_columns(tmp_path):
    path = tmp_path / "gpr_export.csv"
    path.write_text("month,GPR,GPRT,GPRA\n2020-01,100,70,30\n2020-02,110,75,35\n")

    df = load_caldara_iacoviello_gpr(str(path))

    assert df.to_dict("records") == [
        {
            "date_month": pd.Timestamp("2020-01-01"),
            "gpr_global": 100.0,
            "gprt_global": 70.0,
            "gpra_global": 30.0,
        },
        {
            "date_month": pd.Timestamp("2020-02-01"),
            "gpr_global": 110.0,
            "gprt_global": 75.0,
            "gpra_global": 35.0,
        },
    ]


def _fama_french_csv_text() -> str:
    return (
        "This file has a preamble\n"
        ",Mkt-RF,SMB,HML,RF\n"
        "202001,1.20,0.00,0.00,0.05\n"
        "202002,-2.55,0.00,0.00,0.05\n"
        "Annual Factors: January-December\n"
    )


def test_load_fama_french_factor_returns_parses_zip_fixture(tmp_path):
    path = tmp_path / "developed.zip"
    csv_text = _fama_french_csv_text()
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("developed.csv", csv_text)

    df = load_fama_french_factor_returns(
        str(path),
        market_id="developed",
        market_class="developed",
    )

    assert df["date_month"].tolist() == [
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-02-01"),
    ]
    assert df["excess_return"].tolist() == [1.2, -2.55]
    assert df["risk_free_rate"].tolist() == [0.05, 0.05]
    assert df["return_usd"].tolist() == [1.25, -2.5]


def test_load_fama_french_factor_returns_rejects_zip_with_multiple_csvs(tmp_path):
    path = tmp_path / "developed.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("developed.csv", _fama_french_csv_text())
        archive.writestr("extra.csv", _fama_french_csv_text())

    with pytest.raises(ValueError, match="exactly one CSV"):
        load_fama_french_factor_returns(
            str(path),
            market_id="developed",
            market_class="developed",
        )


def test_load_fama_french_factor_returns_rejects_oversized_csv_member(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "developed.zip"
    csv_text = _fama_french_csv_text()
    monkeypatch.setattr(
        market_returns,
        "FAMA_FRENCH_MAX_CSV_BYTES",
        len(csv_text.encode("utf-8")) - 1,
        raising=False,
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("developed.csv", csv_text)

    with pytest.raises(ValueError, match="too large"):
        load_fama_french_factor_returns(
            str(path),
            market_id="developed",
            market_class="developed",
        )


def test_load_fama_french_factor_returns_rejects_oversized_archive(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "developed.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("developed.csv", _fama_french_csv_text())
    monkeypatch.setattr(
        market_returns,
        "FAMA_FRENCH_MAX_ARCHIVE_BYTES",
        path.stat().st_size - 1,
        raising=False,
    )

    with pytest.raises(ValueError, match="archive is too large"):
        load_fama_french_factor_returns(
            str(path),
            market_id="developed",
            market_class="developed",
        )


def test_load_fama_french_factor_returns_supports_remote_zip_urls(monkeypatch):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("developed.csv", _fama_french_csv_text())
    zip_bytes = buffer.getvalue()

    class FakeHandle:
        def __init__(self, data: bytes):
            self.handle = BytesIO(data)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            self.handle.close()
            return False

    def fake_get_handle(source, mode="r", *args, **kwargs):
        assert source == "https://example.test/developed.zip"
        assert mode == "rb"
        return FakeHandle(zip_bytes)

    monkeypatch.setattr(market_returns.pd.io.common, "get_handle", fake_get_handle)

    df = load_fama_french_factor_returns(
        "https://example.test/developed.zip",
        market_id="developed",
        market_class="developed",
    )

    assert df["date_month"].tolist() == [
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-02-01"),
    ]
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


def test_build_gdelt_country_month_zscore_is_country_specific():
    rows = []
    for country, monthly_counts in {"AAA": [1, 2], "BBB": [10, 20]}.items():
        for month, count in zip(["2020-01-01", "2020-02-01"], monthly_counts, strict=True):
            rows.extend(
                {
                    "event_date": month,
                    "country_iso3": country,
                    "event_type": "conflict",
                    "goldstein_score": -1.0,
                    "tone": -1.0,
                }
                for _ in range(count)
            )
    events = pd.DataFrame(rows)

    df = build_gdelt_country_month(events, {"filter_version": "test-v1"})

    for country in ["AAA", "BBB"]:
        values = df.loc[df["country_iso3"] == country, "risk_index_zscore"]
        assert values.mean() == pytest.approx(0.0)


def test_build_gdelt_country_month_constant_country_zscore_is_zero():
    events = pd.DataFrame(
        {
            "event_date": ["2020-01-01", "2020-02-01"],
            "country_iso3": ["AAA", "AAA"],
            "event_type": ["conflict", "conflict"],
        }
    )

    df = build_gdelt_country_month(events, {"filter_version": "test-v1"})

    np.testing.assert_allclose(df["risk_index_zscore"], [0.0, 0.0])


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
            "date_month": pd.Timestamp("2020-01-01"),
            "country_iso3": "USA",
            "indicator_code": "FP.CPI.TOTL.ZG",
            "value": 1.2,
        }
    ]


def test_load_world_bank_indicator_rejects_duplicate_keys(monkeypatch):
    payload = [
        {"page": 1, "pages": 1},
        [
            {
                "date": "2020",
                "countryiso3code": "USA",
                "indicator": {"id": "FP.CPI.TOTL.ZG"},
                "value": 1.2,
            },
            {
                "date": "2020",
                "countryiso3code": "USA",
                "indicator": {"id": "FP.CPI.TOTL.ZG"},
                "value": 1.3,
            },
        ],
    ]

    class Response(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    def fake_urlopen(url, timeout=30):
        return Response(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr("georisklab.ingest.world_bank.urlopen", fake_urlopen)

    with pytest.raises(ValueError, match="duplicate keys"):
        load_world_bank_indicator("FP.CPI.TOTL.ZG", ["USA"])


def test_load_world_bank_indicator_preserves_multi_country_separator(monkeypatch):
    payload = [
        {"page": 1, "pages": 1},
        [
            {
                "date": "2020",
                "countryiso3code": "USA",
                "indicator": {"id": "FP.CPI.TOTL.ZG"},
                "value": 1.2,
            },
            {
                "date": "2020",
                "countryiso3code": "CAN",
                "indicator": {"id": "FP.CPI.TOTL.ZG"},
                "value": 1.4,
            },
        ],
    ]

    class Response(BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    def fake_urlopen(url, timeout=30):
        assert "/country/USA;CAN/indicator/FP.CPI.TOTL.ZG" in url
        assert "%3B" not in url
        return Response(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr("georisklab.ingest.world_bank.urlopen", fake_urlopen)

    df = load_world_bank_indicator("FP.CPI.TOTL.ZG", ["USA", "CAN"])

    assert set(df["country_iso3"]) == {"USA", "CAN"}
