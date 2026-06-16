import json
import subprocess
import sys
import zipfile
from importlib import import_module
from pathlib import Path

import pandas as pd


def _write_fixture_config(tmp_path: Path) -> Path:
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
    return config


def _run_script(root: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _write_fama_french_zip(path: Path, rows: list[str]) -> Path:
    text = "\n".join(
        [
            "This file has a preamble",
            ",Mkt-RF,SMB,HML,RF",
            *rows,
            "Annual Factors: January-December",
            "",
        ]
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(path.with_suffix(".csv").name, text)
    return path


def test_real_monthly_pipeline_rejects_incomplete_market_month_pairs(tmp_path):
    root = Path(__file__).resolve().parents[1]
    fixtures = root / "tests" / "fixtures"
    emerging_zip = _write_fama_french_zip(
        tmp_path / "fama_french_emerging_missing_month.zip",
        ["200001,1.60,0.00,0.00,0.05"],
    )
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
                f"  emerging_zip: {emerging_zip}",
                "",
                "sample_period:",
                '  start: "2000-01-01"',
                '  end: "2000-02-01"',
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

    assert result.returncode != 0
    assert "ValueError" in result.stderr
    assert "both developed and emerging markets for every retained month" in result.stderr


def test_real_monthly_pipeline_runs_on_fixture_sources(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = _write_fixture_config(tmp_path)

    _run_script(
        root,
        "scripts/build_real_monthly_data.py",
        "--config",
        str(config),
        "--root",
        str(tmp_path),
    )

    gpr = pd.read_csv(tmp_path / "data" / "processed" / "gpr_monthly.csv")
    returns = pd.read_csv(tmp_path / "data" / "processed" / "market_returns_monthly.csv")
    spread = pd.read_csv(tmp_path / "data" / "processed" / "market_spread_monthly.csv")
    manifest = json.loads(
        (tmp_path / "data" / "metadata" / "source_manifest_real.json").read_text(
            encoding="utf-8"
        )
    )

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
    assert spread.head(2).to_dict("records") == [
        {"date_month": "2000-01-01", "spread_em_dev": 1.0},
        {"date_month": "2000-02-01", "spread_em_dev": -1.5},
    ]
    assert (tmp_path / "data" / "metadata" / "gpr_manifest.json").exists()
    assert (tmp_path / "data" / "metadata" / "fama_french_developed_manifest.json").exists()
    assert (tmp_path / "data" / "metadata" / "fama_french_emerging_manifest.json").exists()
    assert [source["source_name"] for source in manifest["sources"]] == [
        "Caldara-Iacoviello GPR",
        "Kenneth French Developed Factors",
        "Kenneth French Emerging Factors",
    ]


def test_real_pipeline_runs_end_to_end_on_fixture_sources(tmp_path):
    root = Path(__file__).resolve().parents[1]
    config = _write_fixture_config(tmp_path)

    _run_script(
        root,
        "scripts/build_real_monthly_data.py",
        "--config",
        str(config),
        "--root",
        str(tmp_path),
    )
    for args in [
        ["scripts/build_features.py", "--dataset", "real", "--root", str(tmp_path)],
        [
            "scripts/validate_data.py",
            "--dataset",
            "real",
            "--root",
            str(tmp_path),
            "--min-overlap-months",
            "24",
        ],
        ["scripts/run_regressions.py", "--dataset", "real", "--root", str(tmp_path)],
        [
            "scripts/run_forecasts.py",
            "--dataset",
            "real",
            "--root",
            str(tmp_path),
            "--min-train-months",
            "6",
        ],
        ["scripts/make_figures.py", "--dataset", "real", "--root", str(tmp_path)],
        ["scripts/build_report.py", "--dataset", "real", "--root", str(tmp_path)],
    ]:
        _run_script(root, *args)

    tables = tmp_path / "reports" / "tables"
    figures = tmp_path / "reports" / "figures"
    regressions = pd.read_csv(tables / "table_02_baseline_regressions_real.csv")
    forecasts = pd.read_csv(tables / "table_03_forecast_comparison_real.csv")

    assert "sample_global_cycle" not in set(regressions["term"])
    assert "gpr_change_z" in set(regressions["term"])
    assert forecasts["model"].tolist() == [
        "historical_mean",
        "gpr_only",
        "regularized_gpr_only",
    ]
    assert (tables / "table_00_missingness_real.csv").exists()
    assert (tables / "table_01_summary_stats_real.csv").exists()
    assert (figures / "fig_05_forecast_comparison_real.png").exists()
    assert not (figures / "fig_04_gdelt_vs_gpr_real.png").exists()
    assert not (tables / "table_02_baseline_regressions.csv").exists()
    assert (tmp_path / "reports" / "main_report_real.pdf").exists()
    assert not (tmp_path / "reports" / "main_report.pdf").exists()


def test_real_report_text_identifies_user_supplied_data():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; sys.path.insert(0, 'scripts'); "
                "from build_report import report_text; "
                "text = report_text('real'); "
                "print(text['title']); print(text['note'])"
            ),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "GeoRiskLab Real-Data V0.1 Report" in result.stdout
    assert "user-supplied local raw data" in result.stdout
    assert "deterministic sample data" not in result.stdout


def test_real_report_metrics_include_baseline_regression_summary(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    build_report = import_module("build_report")

    panel = pd.DataFrame(
        {
            "date_month": pd.to_datetime(
                ["2000-01-01", "2000-01-01", "2000-02-01", "2000-02-01"]
            ),
            "market_id": ["developed", "emerging", "developed", "emerging"],
            "excess_return": [1.0, 2.0, 3.0, 1.0],
            "spread_em_dev": [1.0, 1.0, -2.0, -2.0],
        }
    )
    regressions = pd.DataFrame(
        {
            "horizon": [1, 3, 6],
            "term": ["gpr_global_z", "gpr_global_z", "gpr_global_z"],
            "estimate": [-0.25, -0.50, -0.75],
            "std_error": [0.10, 0.20, 0.30],
            "p_value": [0.04, 0.03, 0.02],
        }
    )

    metrics = build_report.report_metrics(panel, regressions, "gpr_global_z")

    assert metrics["sample_period"] == "2000-01-01 to 2000-02-01"
    assert metrics["n_months"] == 2
    assert metrics["mean_emerging_return"] == 1.5
    assert metrics["mean_developed_return"] == 2.0
    assert metrics["mean_spread_em_dev"] == -0.5
    assert metrics["baseline_coefficient"] == -0.25
    assert metrics["baseline_std_error"] == 0.10
    assert metrics["baseline_p_value"] == 0.04
    assert metrics["confidence_interval_95"] == (-0.446, -0.054)
    assert metrics["horizon_regressions"] == [
        {
            "horizon": "1m",
            "estimate": -0.25,
            "std_error": 0.1,
            "p_value": 0.04,
            "confidence_interval_95": (-0.446, -0.054),
        },
        {
            "horizon": "3m",
            "estimate": -0.5,
            "std_error": 0.2,
            "p_value": 0.03,
            "confidence_interval_95": (-0.892, -0.108),
        },
        {
            "horizon": "6m",
            "estimate": -0.75,
            "std_error": 0.3,
            "p_value": 0.02,
            "confidence_interval_95": (-1.338, -0.162),
        },
    ]
    assert "lower EM minus developed spread" in metrics["interpretation"]
