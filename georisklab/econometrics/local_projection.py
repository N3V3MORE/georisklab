import pandas as pd

from georisklab.econometrics.baseline import run_spread_regression


def run_local_projections(panel: pd.DataFrame, horizons: list[int], config: dict) -> pd.DataFrame:
    rows = []
    for horizon in horizons:
        result = run_spread_regression(panel, horizon, config)
        frame = result.to_frame()
        frame.insert(0, "horizon", horizon)
        rows.append(frame)
    return pd.concat(rows, ignore_index=True)
