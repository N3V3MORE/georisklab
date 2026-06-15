import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_real_monthly_pipeline_runs_on_fixture_sources(tmp_path):
    root = Path(__file__).resolve().parents[1]
    fixtures = root / "tests" / "fixtures"
    config = tmp_path / "sources.yml"
    config.write_text(
        "\n".join(
            [
                "gpr:",
                f"  path_or_url: {fixtures / 'gpr_tiny.csv'}",
                "  loader: caldara_iacoviello",
                "",
                "fama_french:",
                f"  developed_zip: {fixtures / 'fama_french_developed_tiny.zip'}",
                f"  emerging_zip: {fixtures / 'fama_french_emerging_tiny.zip'}",
                "",
                "sample_period:",
                '  start: "2000-01-01"',
                "  end: null",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_monthly_data.py",
            "--config",
            str(config),
            "--root",
            str(tmp_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    gpr = pd.read_csv(tmp_path / "data" / "processed" / "gpr_monthly.csv")
    returns = pd.read_csv(tmp_path / "data" / "processed" / "market_returns_monthly.csv")
    spread = pd.read_csv(tmp_path / "data" / "processed" / "market_spread_monthly.csv")

    assert list(gpr.columns) == [
        "date_month",
        "gpr_global",
        "gprt_global",
        "gpra_global",
        "source_download_date",
    ]
    assert list(returns.columns) == [
        "date_month",
        "market_id",
        "market_class",
        "return_usd",
        "risk_free_rate",
        "excess_return",
        "source",
    ]
    assert spread.to_dict("records") == [
        {"date_month": "2000-01-01", "spread_em_dev": 1.0},
        {"date_month": "2000-02-01", "spread_em_dev": -1.5},
    ]
    assert (tmp_path / "data" / "metadata" / "gpr_manifest.json").exists()
