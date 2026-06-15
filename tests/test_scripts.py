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
