import json
import subprocess
import sys
from importlib import import_module
from pathlib import Path

import pandas as pd


def test_build_monthly_data_script_writes_to_requested_root(tmp_path):
    root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [sys.executable, "scripts/build_monthly_data.py", "--root", str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (
        tmp_path / "data" / "processed" / "sample_market_returns_monthly.csv"
    ).exists()


def test_feature_and_validation_scripts_write_to_requested_root(tmp_path):
    root = Path(__file__).resolve().parents[1]

    for command in [
        ["scripts/build_monthly_data.py", "--root", str(tmp_path)],
        ["scripts/build_features.py", "--root", str(tmp_path)],
        ["scripts/validate_data.py", "--root", str(tmp_path)],
    ]:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    assert (tmp_path / "data" / "processed" / "sample_analysis_panel.csv").exists()
    assert (tmp_path / "reports" / "tables" / "table_01_summary_stats.csv").exists()


def test_analysis_scripts_write_to_requested_root(tmp_path):
    root = Path(__file__).resolve().parents[1]

    for command in [
        ["scripts/build_monthly_data.py", "--root", str(tmp_path)],
        ["scripts/build_features.py", "--root", str(tmp_path)],
        ["scripts/run_regressions.py", "--root", str(tmp_path)],
        ["scripts/run_forecasts.py", "--root", str(tmp_path)],
        ["scripts/make_figures.py", "--root", str(tmp_path)],
        ["scripts/build_report.py", "--root", str(tmp_path)],
    ]:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    assert (
        tmp_path / "reports" / "tables" / "table_02_baseline_regressions.csv"
    ).exists()
    assert (
        tmp_path / "reports" / "tables" / "table_03_forecast_comparison.csv"
    ).exists()
    assert (tmp_path / "reports" / "figures" / "fig_01_gpr_timeseries.png").exists()
    assert (tmp_path / "reports" / "main_report.pdf").exists()


def test_task_runner_runs_data_task_in_requested_root(tmp_path):
    root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [sys.executable, "scripts/run_task.py", "data-monthly", "--root", str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (
        tmp_path / "data" / "processed" / "sample_market_returns_monthly.csv"
    ).exists()


def test_task_runner_real_data_default_config_is_rooted(monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    run_task = import_module("run_task")
    commands = []

    class Result:
        returncode = 0

    def fake_run(command, check):
        commands.append(command)
        return Result()

    monkeypatch.setattr(run_task.subprocess, "run", fake_run)

    assert run_task.run_task("data-real", root=tmp_path) == 0
    assert commands[0][commands[0].index("--config") + 1] == str(
        tmp_path / "config" / "sources.yml"
    )


def test_build_features_real_warns_when_using_placeholder_inputs(tmp_path):
    root = Path(__file__).resolve().parents[1]
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=3, freq="MS"),
            "gpr_global": [100.0, 101.0, 102.0],
            "gprt_global": [60.0, 61.0, 62.0],
            "gpra_global": [40.0, 40.0, 40.0],
        }
    ).to_csv(processed_dir / "gpr_monthly.csv", index=False)
    pd.DataFrame(
        {
            "date_month": list(pd.date_range("2020-01-01", periods=3, freq="MS")) * 2,
            "market_id": ["developed"] * 3 + ["emerging"] * 3,
            "market_class": ["developed"] * 3 + ["emerging"] * 3,
            "return_usd": [1.0, 1.1, 1.2, 1.4, 1.5, 1.6],
            "risk_free_rate": [0.1] * 6,
            "excess_return": [0.9, 1.0, 1.1, 1.3, 1.4, 1.5],
        }
    ).to_csv(processed_dir / "market_returns_monthly.csv", index=False)

    result = subprocess.run(
        [sys.executable, "scripts/build_features.py", "--dataset", "real", "--root", str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "placeholder" in result.stderr.lower()
    assert "gdelt" in result.stderr.lower()
    assert "macro" in result.stderr.lower()

    manifest = json.loads(
        (tmp_path / "data" / "metadata" / "analysis_panel_manifest_real.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["used_placeholder_gdelt"] is True
    assert manifest["used_placeholder_macro"] is True
    panel = pd.read_csv(tmp_path / "data" / "processed" / "analysis_panel.csv")
    assert "placeholder_macro_zero" in panel.columns
    assert "sample_global_cycle" not in panel.columns


def test_build_features_real_restricts_panel_to_common_gpr_return_months(tmp_path):
    root = Path(__file__).resolve().parents[1]
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)

    pd.DataFrame(
        {
            "date_month": pd.date_range("2020-01-01", periods=2, freq="MS"),
            "gpr_global": [100.0, 101.0],
            "gprt_global": [60.0, 61.0],
            "gpra_global": [40.0, 40.0],
        }
    ).to_csv(processed_dir / "gpr_monthly.csv", index=False)
    pd.DataFrame(
        {
            "date_month": list(pd.date_range("2020-01-01", periods=3, freq="MS")) * 2,
            "market_id": ["developed"] * 3 + ["emerging"] * 3,
            "market_class": ["developed"] * 3 + ["emerging"] * 3,
            "return_usd": [1.0, 1.1, 1.2, 1.4, 1.5, 1.6],
            "risk_free_rate": [0.1] * 6,
            "excess_return": [0.9, 1.0, 1.1, 1.3, 1.4, 1.5],
        }
    ).to_csv(processed_dir / "market_returns_monthly.csv", index=False)

    result = subprocess.run(
        [sys.executable, "scripts/build_features.py", "--dataset", "real", "--root", str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    panel = pd.read_csv(tmp_path / "data" / "processed" / "analysis_panel.csv")
    assert panel["date_month"].drop_duplicates().tolist() == ["2020-01-01", "2020-02-01"]
