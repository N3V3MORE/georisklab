import json
from importlib import import_module
from pathlib import Path

import pandas as pd
import pytest

from georisklab.utils.validation import (
    assert_dates_are_month_start,
    assert_no_future_leakage,
    missingness_report,
)


def test_assert_dates_are_month_start_rejects_mid_month_dates():
    df = pd.DataFrame({"date_month": pd.to_datetime(["2020-01-15"])})

    with pytest.raises(ValueError, match="not month-start"):
        assert_dates_are_month_start(df, "date_month")


def test_assert_no_future_leakage_rejects_overlapping_windows():
    train_dates = pd.Series(pd.to_datetime(["2020-01-01", "2020-02-01"]))
    test_dates = pd.Series(pd.to_datetime(["2020-02-01"]))

    with pytest.raises(ValueError, match="after all training dates"):
        assert_no_future_leakage(train_dates, test_dates)


def test_missingness_report_counts_missing_values():
    df = pd.DataFrame({"a": [1.0, None], "b": [None, None]})

    report = missingness_report(df)

    assert report.to_dict("records") == [
        {"column": "a", "missing_count": 1, "missing_share": 0.5},
        {"column": "b", "missing_count": 2, "missing_share": 1.0},
    ]


def _validate_data_module(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    return import_module("validate_data")


def test_validate_real_source_frames_requires_both_markets_each_month(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    gpr = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "gpr_global": [100.0, 101.0, 102.0],
        }
    )
    returns = pd.DataFrame(
        {
            "date_month": pd.to_datetime(["2020-01-01", "2020-01-01", "2020-02-01"]),
            "market_id": ["developed", "emerging", "developed"],
            "return_usd": [1.0, 2.0, 1.5],
            "risk_free_rate": [0.1, 0.1, 0.1],
            "excess_return": [0.9, 1.9, 1.4],
        }
    )

    with pytest.raises(ValueError, match="developed and emerging"):
        validate_data._validate_real_source_frames(gpr, returns, min_overlap_months=2)


def test_validate_real_source_frames_rejects_implausible_percentage_returns(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    dates = pd.date_range("2020-01-01", periods=2, freq="MS")
    gpr = pd.DataFrame({"date_month": dates, "gpr_global": [100.0, 101.0]})
    returns = pd.DataFrame(
        {
            "date_month": [dates[0], dates[0], dates[1], dates[1]],
            "market_id": ["developed", "emerging", "developed", "emerging"],
            "return_usd": [1.0, 250.0, 1.5, 1.6],
            "risk_free_rate": [0.1, 0.1, 0.1, 0.1],
            "excess_return": [0.9, 249.9, 1.4, 1.5],
        }
    )

    with pytest.raises(ValueError, match="percentage-point range"):
        validate_data._validate_real_source_frames(gpr, returns, min_overlap_months=2)


def test_validate_real_source_frames_rejects_duplicate_gpr_dates(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    date = pd.Timestamp("2020-01-01")
    gpr = pd.DataFrame({"date_month": [date, date], "gpr_global": [100.0, 101.0]})
    returns = pd.DataFrame(
        {
            "date_month": [date, date],
            "market_id": ["developed", "emerging"],
            "return_usd": [1.0, 1.5],
            "risk_free_rate": [0.1, 0.1],
            "excess_return": [0.9, 1.4],
        }
    )

    with pytest.raises(ValueError, match="duplicate"):
        validate_data._validate_real_source_frames(gpr, returns, min_overlap_months=1)


def test_validate_real_source_frames_rejects_duplicate_return_keys(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    date = pd.Timestamp("2020-01-01")
    gpr = pd.DataFrame({"date_month": [date], "gpr_global": [100.0]})
    returns = pd.DataFrame(
        {
            "date_month": [date, date, date],
            "market_id": ["developed", "developed", "emerging"],
            "return_usd": [1.0, 1.1, 1.5],
            "risk_free_rate": [0.1, 0.1, 0.1],
            "excess_return": [0.9, 1.0, 1.4],
        }
    )

    with pytest.raises(ValueError, match="duplicate"):
        validate_data._validate_real_source_frames(gpr, returns, min_overlap_months=1)


def test_validate_real_source_frames_rejects_short_overlap(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    dates = pd.date_range("2020-01-01", periods=2, freq="MS")
    gpr = pd.DataFrame({"date_month": dates, "gpr_global": [100.0, 101.0]})
    returns = pd.DataFrame(
        {
            "date_month": [dates[0], dates[0], dates[1], dates[1]],
            "market_id": ["developed", "emerging", "developed", "emerging"],
            "return_usd": [1.0, 1.5, 1.1, 1.6],
            "risk_free_rate": [0.1, 0.1, 0.1, 0.1],
            "excess_return": [0.9, 1.4, 1.0, 1.5],
        }
    )

    with pytest.raises(ValueError, match="at least 3 months"):
        validate_data._validate_real_source_frames(gpr, returns, min_overlap_months=3)


def test_validate_forward_returns_only_allows_final_missing_rows(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    panel = pd.DataFrame(
        {
            "date_month": list(pd.date_range("2020-01-01", periods=4, freq="MS")) * 2,
            "market_id": ["developed"] * 4 + ["emerging"] * 4,
            "ret_fwd_1m": [1.0, None, 2.0, None, 1.0, 2.0, 3.0, None],
        }
    )

    with pytest.raises(ValueError, match="only final"):
        validate_data._validate_forward_return_missingness(panel, [1])


def test_validate_real_manifest_requires_expected_names_and_local_hashes(
    monkeypatch,
    tmp_path,
):
    validate_data = _validate_data_module(monkeypatch)
    manifest = {
        "sources": [
            {
                "source_name": "Caldara-Iacoviello GPR",
                "raw_file_path": str(tmp_path / "gpr.csv"),
                "file_hash_sha256": "",
            },
            {
                "source_name": "Kenneth French Developed Factors",
                "raw_file_path": str(tmp_path / "dev.zip"),
                "file_hash_sha256": "abc",
            },
            {
                "source_name": "Kenneth French Emerging Factors",
                "raw_file_path": str(tmp_path / "em.zip"),
                "file_hash_sha256": "def",
            },
        ]
    }
    path = tmp_path / "source_manifest_real.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="hash"):
        validate_data._validate_metadata(path, "real")


def test_validate_forecast_windows_requires_same_dates(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    forecasts = pd.DataFrame(
        {
            "model": ["historical_mean", "gpr_only"],
            "n_forecasts": [10, 8],
            "first_forecast_date": ["2020-01-01", "2020-03-01"],
            "last_forecast_date": ["2020-10-01", "2020-10-01"],
        }
    )

    with pytest.raises(ValueError, match="same forecast evaluation"):
        validate_data._validate_forecast_windows(forecasts)


def test_validate_forecast_windows_accepts_aligned_dates(monkeypatch):
    validate_data = _validate_data_module(monkeypatch)
    forecasts = pd.DataFrame(
        {
            "model": ["historical_mean", "gpr_only"],
            "n_forecasts": [10, 10],
            "first_forecast_date": ["2020-01-01", "2020-01-01"],
            "last_forecast_date": ["2020-10-01", "2020-10-01"],
        }
    )

    validate_data._validate_forecast_windows(forecasts)
