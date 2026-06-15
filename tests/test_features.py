import numpy as np
import pandas as pd

from georisklab.features.returns import make_forward_returns
from georisklab.features.shocks import expanding_standardize_shocks, standardize_shocks


def test_make_forward_returns_uses_only_future_returns():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=4, freq="MS"),
            "market_id": ["developed"] * 4,
            "excess_return": [1.0, 2.0, 3.0, 4.0],
        }
    )

    result = make_forward_returns(df, [1, 3])

    np.testing.assert_allclose(result["ret_fwd_1m"], [2.0, 3.0, 4.0, np.nan])
    np.testing.assert_allclose(result["ret_fwd_3m"], [9.0, np.nan, np.nan, np.nan])


def test_standardize_shocks_adds_zscore_columns():
    df = pd.DataFrame({"gpr_global": [1.0, 2.0, 3.0]})

    result = standardize_shocks(df, ["gpr_global"])

    np.testing.assert_allclose(result["gpr_global_z"], [-1.2247449, 0.0, 1.2247449])


def test_expanding_standardize_shocks_uses_only_prior_history():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=4, freq="MS"),
            "gpr_global": [10.0, 20.0, 30.0, 1000.0],
        }
    )

    result = expanding_standardize_shocks(df, ["gpr_global"])

    assert result["gpr_global_z"].iloc[0] == 0.0
    assert result["gpr_global_z"].iloc[1] == 0.0
    assert result["gpr_global_z"].iloc[2] == 3.0


def test_expanding_standardize_shocks_handles_groups_and_constants():
    df = pd.DataFrame(
        {
            "date_month": pd.to_datetime(
                ["2020-01-01", "2020-02-01", "2020-01-01", "2020-02-01"]
            ),
            "country_iso3": ["A", "A", "B", "B"],
            "gdelt_risk": [5.0, 5.0, 1.0, 3.0],
        }
    )

    result = expanding_standardize_shocks(df, ["gdelt_risk"], group_cols=["country_iso3"])

    np.testing.assert_allclose(result["gdelt_risk_z"], [0.0, 0.0, 0.0, 0.0])
