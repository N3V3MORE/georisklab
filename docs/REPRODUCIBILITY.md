# Reproducibility Guide

This guide explains how to rebuild the project outputs from the current repo.

## Environment

Recommended:

```bash
python -m venv .venv
python -m pip install -c constraints.txt -e .[dev]
```

Conda alternative:

```bash
conda env create -f environment.yml
conda activate georisklab
```

The current sample pipeline does not require API keys. Future FRED-based
extensions may require credentials, but they are not part of the current
runnable workflow.

## Sample Pipeline

Run:

```bash
python scripts/run_task.py setup
python scripts/run_task.py pipeline
```

The sample pipeline writes deterministic sample data and reproducible outputs so
reviewers can test the software without raw third-party data.

Equivalent `make` command:

```bash
make pipeline
```

## Real-Data Pipeline

Copy the sample source config and edit local paths:

```bash
cp config/sources.sample.yml config/sources.yml
```

Then run:

```bash
python scripts/run_task.py pipeline-real
```

The real pipeline reads local raw files from `data/raw/` and writes:

```text
data/processed/gpr_monthly.csv
data/processed/market_returns_monthly.csv
data/processed/market_spread_monthly.csv
data/metadata/gpr_manifest.json
data/metadata/fama_french_developed_manifest.json
data/metadata/fama_french_emerging_manifest.json
data/metadata/source_manifest_real.json
```

HTTPS raw-source URLs are allowed only with expected SHA-256 hashes in the source
configuration. URL sources are downloaded to the ignored raw-data cache and the
cached local file hash is written to the manifest.

Do not commit raw files or local `config/sources.yml`.

## Expected Public Outputs

Sample runs rebuild:

```text
reports/tables/table_00_missingness.csv
reports/tables/table_01_summary_stats.csv
reports/tables/table_02_baseline_regressions.csv
reports/tables/table_03_forecast_comparison.csv
reports/figures/fig_01_gpr_timeseries.png
reports/figures/fig_02_em_dev_spread.png
reports/figures/fig_03_local_projection.png
reports/figures/fig_04_gdelt_vs_gpr.png
reports/figures/fig_05_forecast_comparison.png
dashboard/index.html
reports/main_report.pdf
```

Real runs write `*_real` tables and figures where available. The real GDELT
comparison figure is skipped when the feature build records placeholder GDELT
inputs. Real-data tables, figures, and PDFs are local artifacts by default.

The V0.1a real-data snapshot keeps the narrative findings note in git:

```text
reports/v0_1a_findings.md
```

## Validation

Run:

```bash
python scripts/run_task.py validate-data
python scripts/run_task.py validate-results
python scripts/run_task.py test
python scripts/run_task.py lint
```

Validation checks:

1. No duplicate panel keys.
2. Month-start dates.
3. No future data leakage in forecasting features.
4. Required source metadata.
5. Plausible value ranges for returns and indexes.
6. Stable output filenames.
7. Result-table schemas and aligned forecast evaluation windows.
8. Real-data common-sample alignment and placeholder metadata.

## Determinism

The sample pipeline is deterministic. Forecast models that need randomness must
set and document a fixed seed before they are added to the real-data workflow.

## CI

Public CI should run the deterministic sample pipeline, tests, linting, and an
import smoke test. CI should not run live external-data ingestion because public
CI should not depend on external data availability or private local files.

## Reproduction Levels

Level 1: install the package and run tests.

Level 2: rebuild processed data, tables, figures, dashboard, and report.

Level 3: rebuild real outputs from raw source files and document the exact source
versions.

V0.1a targets Level 2 for sample outputs and Level 3 locally for user-supplied
GPR/Fama-French source files.
