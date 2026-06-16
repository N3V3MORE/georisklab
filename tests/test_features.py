import numpy as np
import pandas as pd
import pytest

from georisklab.features.panel import build_analysis_panel
from georisklab.features.returns import make_forward_returns
from georisklab.features.shocks import (
    expanding_standardize_shocks,
    make_gpr_shock_features,
    standardize_shocks,
)


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


def test_make_forward_returns_rejects_missing_calendar_months():
    df = pd.DataFrame(
        {
            "date_month": pd.to_datetime(["2020-01-01", "2020-03-01", "2020-04-01"]),
            "market_id": ["developed"] * 3,
            "excess_return": [1.0, 3.0, 4.0],
        }
    )

    with pytest.raises(ValueError, match="monthly sequence"):
        make_forward_returns(df, [1])


def test_build_analysis_panel_rejects_multi_country_gdelt_rows():
    market_returns = pd.DataFrame(
        {
            "date_month": list(pd.date_range("2020-01-01", periods=2, freq="MS")) * 2,
            "market_id": ["developed", "developed", "emerging", "emerging"],
            "market_class": ["developed", "developed", "emerging", "emerging"],
            "excess_return": [1.0, 2.0, 1.5, 2.5],
        }
    )
    gpr = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "gpr_global": [100.0, 105.0],
            "gprt_global": [60.0, 62.0],
            "gpra_global": [40.0, 43.0],
        }
    )
    gdelt = pd.DataFrame(
        {
            "date_month": pd.to_datetime(
                ["2020-01-01", "2020-01-01", "2020-02-01", "2020-02-01"]
            ),
            "country_iso3": ["ARG", "BRA", "ARG", "BRA"],
            "risk_index_raw": [1.0, 2.0, 1.5, 2.5],
            "risk_index_zscore": [-1.0, 1.0, -1.0, 1.0],
        }
    )
    macro = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "indicator_code": ["sample_global_cycle", "sample_global_cycle"],
            "value": [0.0, 0.1],
        }
    )

    with pytest.raises(ValueError, match="GDELT.*unique by date_month"):
        build_analysis_panel(market_returns, gpr, gdelt, macro)


def test_build_analysis_panel_requires_gdelt_raw_risk_index():
    market_returns = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "market_id": ["developed", "developed"],
            "market_class": ["developed", "developed"],
            "excess_return": [1.0, 2.0],
        }
    )
    gpr = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "gpr_global": [100.0, 105.0],
            "gprt_global": [60.0, 62.0],
            "gpra_global": [40.0, 43.0],
        }
    )
    gdelt = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "risk_index_zscore": [0.0, 0.5],
        }
    )
    macro = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "indicator_code": ["sample_global_cycle", "sample_global_cycle"],
            "value": [0.0, 0.1],
        }
    )

    with pytest.raises(ValueError, match="missing required columns: risk_index_raw"):
        build_analysis_panel(market_returns, gpr, gdelt, macro)


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

    result = expanding_standardize_shocks(df, ["gpr_global"], min_periods=2)

    assert result["gpr_global_z"].iloc[:2].isna().all()
    assert result["gpr_global_z"].iloc[2] == 3.0


def test_expanding_standardize_shocks_handles_groups_and_constants():
    df = pd.DataFrame(
        {
            "date_month": pd.to_datetime(
                [
                    "2020-01-01",
                    "2020-02-01",
                    "2020-03-01",
                    "2020-01-01",
                    "2020-02-01",
                    "2020-03-01",
                ]
            ),
            "country_iso3": ["A", "A", "A", "B", "B", "B"],
            "gdelt_risk": [5.0, 5.0, 5.0, 1.0, 1.0, 1.0],
        }
    )

    result = expanding_standardize_shocks(
        df,
        ["gdelt_risk"],
        group_cols=["country_iso3"],
        min_periods=2,
    )

    assert result["gdelt_risk_z"].iloc[[0, 1, 3, 4]].isna().all()
    np.testing.assert_allclose(result["gdelt_risk_z"].iloc[[2, 5]], [0.0, 0.0])


def test_expanding_standardize_shocks_defaults_to_missing_until_min_history():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=24, freq="MS"),
            "gpr_global": [float(value) for value in range(24)],
        }
    )

    result = expanding_standardize_shocks(df, ["gpr_global"])

    assert result["gpr_global_z"].iloc[:24].isna().all()


def test_make_gpr_shock_features_adds_level_change_log_change_and_ar1_residual():
    df = pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=5, freq="MS"),
            "gpr_global": [100.0, 105.0, 111.0, 118.0, 126.0],
            "gprt_global": [60.0, 63.0, 67.0, 70.0, 75.0],
            "gpra_global": [40.0, 42.0, 44.0, 48.0, 51.0],
        }
    )

    result = make_gpr_shock_features(df)

    for column in [
        "gpr_level_z",
        "gpr_change",
        "gpr_change_z",
        "gpr_log_change",
        "gpr_log_change_z",
        "gpr_ar1_residual",
        "gpr_ar1_residual_z",
    ]:
        assert column in result.columns
    assert result["gpr_global_z"].equals(result["gpr_level_z"])
    assert pd.isna(result["gpr_change"].iloc[0])
    assert result["gpr_change"].iloc[1] == 5.0
    assert pd.isna(result["gpr_ar1_residual"].iloc[0])
