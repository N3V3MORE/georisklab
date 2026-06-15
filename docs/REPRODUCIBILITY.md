# Reproducibility Guide

## Environment

Recommended:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Alternative:

```bash
conda env create -f environment.yml
conda activate georisklab
```

## Configuration

Create `.env` locally:

```text
FRED_API_KEY=your_key_here
DATA_DIR=data
```

Never commit `.env`.

## Full pipeline

```bash
make setup
make data-monthly
make features
make regressions
make forecasts
make figures
make report
```

On systems without GNU Make, run the equivalent Python task runner:

```bash
python scripts/run_task.py setup
python scripts/run_task.py pipeline
```

The current default pipeline is sample mode. It writes deterministic sample
data and reproducible outputs so reviewers can test the software without
downloading restricted data or providing API keys.

## Expected outputs

```text
reports/tables/table_01_summary_stats.csv
reports/tables/table_02_baseline_regressions.csv
reports/tables/table_03_forecast_comparison.csv
reports/figures/fig_01_gpr_timeseries.png
reports/figures/fig_02_em_dev_spread.png
reports/figures/fig_03_local_projection.png
reports/figures/fig_04_gdelt_vs_gpr.png
reports/main_report.pdf
```

## Validation checks

Run:

```bash
make validate-data
make test
```

Without `make`:

```bash
python scripts/run_task.py validate-data
python scripts/run_task.py test
```

Validation must check:

1. No duplicate panel keys.
2. No impossible dates.
3. No future data leakage in forecasting features.
4. No missing source metadata.
5. Expected value ranges for returns and indexes.
6. Stable output filenames.

## Deterministic outputs

Set random seeds for all ML models:

```text
random_state = 42
```

For tree models, store hyperparameters in config files.

## Data versioning

Recommended simple approach:

```text
data/metadata/source_manifest.json
```

Each source entry should include:

```text
source name
source URL
download timestamp
local raw filename
sha256 hash
processing script
notes on terms of use
```

## CI checks

Use GitHub Actions to run:

```text
ruff check
pytest
import smoke test
```

Do not run the full data pipeline in CI. Public CI should not depend on external data availability or private API keys.

## Reproduction levels

### Level 1: Code reproduction

A reviewer can install the package and run tests.

### Level 2: Result reproduction

A reviewer can rebuild the processed data and reproduce tables and figures.

### Level 3: Paper reproduction

A reviewer can rebuild the final PDF/report from raw source downloads.

Version 0.1 should target Level 2. Version 1.0 should target Level 3.
