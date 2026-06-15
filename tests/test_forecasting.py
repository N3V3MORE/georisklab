import numpy as np
import pandas as pd
import pytest

from georisklab.models.metrics import evaluate_forecasts
from georisklab.models.splits import make_time_splits


def test_make_time_splits_uses_future_test_windows():
    dates = pd.Series(pd.date_range("2020-01-01", periods=6, freq="MS"))

    splits = make_time_splits(dates, min_train_months=3, test_window=2)

    assert len(splits) == 2
    assert splits[0].train_dates[-1] == pd.Timestamp("2020-03-01")
    assert splits[0].test_dates == [
        pd.Timestamp("2020-04-01"),
        pd.Timestamp("2020-05-01"),
    ]


def test_make_time_splits_rejects_unsorted_dates():
    dates = pd.Series(pd.to_datetime(["2020-02-01", "2020-01-01"]))

    with pytest.raises(ValueError, match="increasing"):
        make_time_splits(dates, min_train_months=1, test_window=1)


def test_evaluate_forecasts_regression_metrics():
    metrics = evaluate_forecasts([1.0, 2.0, 3.0], [1.0, 2.5, 2.5], task="regression")

    assert metrics["rmse"] == pytest.approx(np.sqrt(0.5 / 3))
    assert metrics["mae"] == pytest.approx(1 / 3)
    assert "oos_r2" in metrics


def test_evaluate_forecasts_classification_metrics():
    metrics = evaluate_forecasts([0, 1, 1], [0.2, 0.8, 0.6], task="classification")

    assert metrics["brier_score"] == pytest.approx(0.08)
    assert metrics["directional_accuracy"] == 1.0
    assert "log_loss" in metrics
