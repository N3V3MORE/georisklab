import pandas as pd

from georisklab.econometrics.baseline import run_panel_interaction, run_spread_regression


def sample_panel() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=8, freq="MS")
    rows = []
    for idx, date in enumerate(dates):
        shock = float(idx - 3)
        for market_id, market_class, multiplier in [
            ("developed", "developed", -0.2),
            ("emerging", "emerging", -0.5),
        ]:
            rows.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "ret_fwd_1m": multiplier * shock,
                    "spread_em_dev": -0.3 * shock,
                    "gpr_global_z": shock,
                    "sample_global_cycle": idx / 10,
                }
            )
    return pd.DataFrame(rows)


def test_run_spread_regression_returns_hac_metadata():
    result = run_spread_regression(
        sample_panel(),
        horizon=1,
        config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
    )

    table = result.to_frame()

    assert result.se_type == "HAC"
    assert result.nobs == 8
    assert "gpr_global_z" in table["term"].tolist()


def test_run_panel_interaction_includes_emerging_interaction():
    result = run_panel_interaction(
        sample_panel(),
        horizon=1,
        config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
    )

    assert "emerging_x_gpr_global_z" in result.to_frame()["term"].tolist()


def test_run_panel_interaction_absorbs_fixed_effects_without_dense_dummies(monkeypatch):
    dates = pd.date_range("2020-01-01", periods=6, freq="MS")
    rows = []
    for date_idx, date in enumerate(dates):
        for market_idx, (market_id, market_class) in enumerate(
            [
                ("developed_a", "developed"),
                ("developed_b", "developed"),
                ("emerging_a", "emerging"),
                ("emerging_b", "emerging"),
            ]
        ):
            shock = float(date_idx + market_idx / 10)
            emerging = market_class == "emerging"
            rows.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "ret_fwd_1m": 1.0 + date_idx + market_idx + shock * (0.3 if emerging else 0.1),
                    "gpr_global_z": shock,
                }
            )
    panel = pd.DataFrame(rows)

    def fail_get_dummies(*args, **kwargs):
        raise AssertionError("dense fixed-effect dummies should not be built")

    monkeypatch.setattr(pd, "get_dummies", fail_get_dummies)

    result = run_panel_interaction(
        panel,
        horizon=1,
        config={
            "shock_col": "gpr_global_z",
            "market_fixed_effects": True,
            "time_fixed_effects": True,
        },
    )

    table = result.to_frame()
    assert result.se_type == "clustered"
    assert "emerging_x_gpr_global_z" in table["term"].tolist()
