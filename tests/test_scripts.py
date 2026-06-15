import subprocess
import sys
from pathlib import Path


def test_build_monthly_data_script_runs_from_repo_root():
    root = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [sys.executable, "scripts/build_monthly_data.py"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (root / "data" / "processed" / "sample_market_returns_monthly.csv").exists()


def test_feature_and_validation_scripts_run_from_repo_root():
    root = Path(__file__).resolve().parents[1]

    for script in [
        "scripts/build_monthly_data.py",
        "scripts/build_features.py",
        "scripts/validate_data.py",
    ]:
        result = subprocess.run(
            [sys.executable, script],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    assert (root / "data" / "processed" / "sample_analysis_panel.csv").exists()
    assert (root / "reports" / "tables" / "table_01_summary_stats.csv").exists()
