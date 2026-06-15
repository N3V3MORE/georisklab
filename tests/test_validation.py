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
