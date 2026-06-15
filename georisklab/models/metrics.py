import numpy as np


def evaluate_forecasts(y_true, y_pred, task: str, benchmark_pred=None) -> dict:
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    if len(actual) != len(predicted):
        raise ValueError("y_true and y_pred must have the same length")

    if task == "regression":
        errors = actual - predicted
        if benchmark_pred is None:
            raise ValueError("benchmark_pred is required for regression OOS R2")
        benchmark = np.asarray(benchmark_pred, dtype=float)
        if len(benchmark) != len(actual):
            raise ValueError("benchmark_pred must have the same length as y_true")
        baseline_errors = actual - benchmark
        baseline_sse = float(np.sum(baseline_errors**2))
        model_sse = float(np.sum(errors**2))
        return {
            "rmse": float(np.sqrt(np.mean(errors**2))),
            "mae": float(np.mean(np.abs(errors))),
            "oos_r2": 0.0 if baseline_sse == 0 else float(1 - model_sse / baseline_sse),
        }

    if task == "classification":
        probabilities = np.clip(predicted, 1e-12, 1 - 1e-12)
        labels = (probabilities >= 0.5).astype(int)
        return {
            "brier_score": float(np.mean((probabilities - actual) ** 2)),
            "log_loss": float(
                -np.mean(actual * np.log(probabilities) + (1 - actual) * np.log(1 - probabilities))
            ),
            "directional_accuracy": float(np.mean(labels == actual)),
        }

    raise ValueError("task must be 'regression' or 'classification'")
