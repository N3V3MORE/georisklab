import numpy as np
import pandas as pd

from georisklab.features.shocks import expanding_standardize_shocks
from georisklab.models.metrics import evaluate_forecasts
from georisklab.models.splits import make_time_splits


def expanding_window_forecast(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    min_train_months: int,
    test_window: int = 1,
    ridge_alpha: float = 0.0,
    standardize_feature_cols: list[str] | None = None,
) -> pd.DataFrame:
    if standardize_feature_cols:
        df = expanding_standardize_shocks(df, standardize_feature_cols)
        feature_cols = [
            f"{column}_z" if column in standardize_feature_cols else column
            for column in feature_cols
        ]

    data = (
        df.dropna(subset=[target_col, *feature_cols])
        .sort_values("date_month")
        .reset_index(drop=True)
    )
    splits = make_time_splits(data["date_month"], min_train_months, test_window)
    rows = []

    for split in splits:
        train = data[data["date_month"].isin(split.train_dates)]
        test = data[data["date_month"].isin(split.test_dates)]
        prediction = _predict_next(train, test, target_col, feature_cols, ridge_alpha)
        benchmark_prediction = np.repeat(train[target_col].mean(), len(test))
        for date, actual, predicted, benchmark in zip(
            test["date_month"],
            test[target_col],
            prediction,
            benchmark_prediction,
            strict=True,
        ):
            rows.append(
                {
                    "date_month": date,
                    "actual": actual,
                    "predicted": predicted,
                    "benchmark_predicted": benchmark,
                }
            )

    return pd.DataFrame(rows)


def forecast_metric_row(
    model: str,
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    min_train_months: int,
    ridge_alpha: float = 0.0,
    standardize_feature_cols: list[str] | None = None,
) -> dict:
    forecasts = expanding_window_forecast(
        df,
        target_col,
        feature_cols,
        min_train_months=min_train_months,
        ridge_alpha=ridge_alpha,
        standardize_feature_cols=standardize_feature_cols,
    )
    metrics = evaluate_forecasts(
        forecasts["actual"],
        forecasts["predicted"],
        task="regression",
        benchmark_pred=forecasts["benchmark_predicted"],
    )
    return {"model": model, **metrics, "n_forecasts": len(forecasts)}


def _predict_next(
    train: pd.DataFrame,
    test: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    ridge_alpha: float,
) -> np.ndarray:
    if not feature_cols:
        return np.repeat(train[target_col].mean(), len(test))

    x_train = _with_intercept(train[feature_cols].to_numpy(dtype=float))
    y_train = train[target_col].to_numpy(dtype=float)
    x_test = _with_intercept(test[feature_cols].to_numpy(dtype=float))

    penalty = np.eye(x_train.shape[1]) * ridge_alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_train.T @ x_train + penalty) @ x_train.T @ y_train
    return x_test @ beta


def _with_intercept(values: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(values)), values])
