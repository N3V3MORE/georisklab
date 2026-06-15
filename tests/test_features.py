import numpy as np
import pandas as pd

from georisklab.features.returns import make_forward_returns
from georisklab.features.shocks import standardize_shocks


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
