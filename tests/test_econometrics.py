import pandas as pd
import pytest

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


def test_run_spread_regression_rejects_nonunique_month_predictors():
    panel = sample_panel()
    panel.loc[panel["market_id"] == "emerging", "gpr_global_z"] += 1.0

    with pytest.raises(ValueError, match="unique within date_month"):
        run_spread_regression(panel, horizon=1, config={"shock_col": "gpr_global_z"})


def test_run_spread_regression_rejects_incomplete_market_month_pairs():
    panel = sample_panel()
    bad_panel = panel[
        ~(
            (panel["date_month"] == pd.Timestamp("2020-01-01"))
            & (panel["market_id"] == "emerging")
        )
    ]

    with pytest.raises(ValueError, match="developed and emerging"):
        run_spread_regression(
            bad_panel,
            horizon=1,
            config={"shock_col": "gpr_global_z"},
        )


def test_run_panel_interaction_includes_emerging_interaction():
    dates = pd.date_range("2020-01-01", periods=8, freq="MS")
    rows = []
    for idx, date in enumerate(dates):
        shock = float(idx - 3)
        for market_id, market_class, multiplier in [
            ("developed_a", "developed", -0.2),
            ("developed_b", "developed", -0.1),
            ("emerging_a", "emerging", -0.5),
            ("emerging_b", "emerging", -0.4),
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
    panel = pd.DataFrame(rows)

    result = run_panel_interaction(
        panel,
        horizon=1,
        config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
    )

    assert "emerging_x_gpr_global_z" in result.to_frame()["term"].tolist()


def test_run_panel_interaction_rejects_unknown_market_class():
    dates = pd.date_range("2020-01-01", periods=8, freq="MS")
    rows = []
    for idx, date in enumerate(dates):
        shock = float(idx - 3)
        for market_id, market_class in [
            ("developed_a", "developed"),
            ("developed_b", "developed"),
            ("emerging_a", "emerging"),
            ("bad_label", "frontier"),
        ]:
            rows.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "ret_fwd_1m": shock,
                    "gpr_global_z": shock,
                }
            )
    panel = pd.DataFrame(rows)

    with pytest.raises(ValueError, match="market_class"):
        run_panel_interaction(
            panel,
            horizon=1,
            config={"shock_col": "gpr_global_z"},
        )


def test_run_panel_interaction_rejects_too_few_clusters():
    with pytest.raises(ValueError, match="at least 3 unique market_id clusters"):
        run_panel_interaction(
            sample_panel(),
            horizon=1,
            config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
        )


def test_run_panel_interaction_does_not_allow_lowering_cluster_guardrail():
    with pytest.raises(ValueError, match="at least 3 unique market_id clusters"):
        run_panel_interaction(
            sample_panel(),
            horizon=1,
            config={
                "shock_col": "gpr_global_z",
                "controls": ["sample_global_cycle"],
                "cluster_min_groups": 1,
            },
        )


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
