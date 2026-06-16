import subprocess
import sys
from pathlib import Path


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
