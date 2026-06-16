# GeoRiskLab

Open-source empirical finance toolkit for measuring geopolitical risk and estimating asymmetric equity-market responses across emerging and developed markets.

## Purpose

GeoRiskLab turns a research question into a reproducible data product:

> Do geopolitical risk shocks affect emerging and developed equity markets differently, and can public event or news data improve forecasts of returns, volatility, and downside risk?

The first real-data milestone, V0.1a, focuses on monthly developed versus emerging equity returns and the Caldara-Iacoviello GPR index. GDELT event intensity and macro-financial controls are staged extensions.

## Minimum viable research product

The project is successful when a reviewer can clone the repo, run a documented pipeline, and reproduce:

1. A clean monthly panel from 1990 or 2000 onward.
2. A GPR shock series and a GDELT event-intensity series.
3. Baseline developed versus emerging market return results.
4. At least one panel regression table once country-level data are added.
5. At least one local-projection or event-study figure.
6. One forecasting comparison showing whether geopolitical features add out-of-sample value.
7. A short limitations section that explains what the project does not prove.

## Repo map

```text
georisklab/
  georisklab/
    ingest/              # download and parse public data
    features/            # risk index, controls, target construction
    econometrics/        # regressions, local projections, event studies
    models/              # forecasting baselines and ML models
    visualization/       # reusable plot functions
    utils/               # config, logging, validation helpers
  scripts/               # command-line entry points
  notebooks/             # exploration only, not final results
  data/
    raw/                 # gitignored
    interim/             # gitignored
    processed/           # gitignored except tiny sample files
  reports/
    figures/
    tables/
  dashboard/
  docs/
  tests/
  .github/
```

## Core commands

```bash
make setup
make data-monthly
make features
make regressions
make forecasts
make figures
make report
make pipeline
make data-real
make pipeline-real
make test
```

If `make` is not installed, use the cross-platform runner:

```bash
python scripts/run_task.py setup
python scripts/run_task.py pipeline
python scripts/run_task.py pipeline-real
python scripts/run_task.py test
python scripts/run_task.py lint
```

The default pipeline uses deterministic sample data. It proves that the code,
tables, figures, and report can be rebuilt without private data or API keys. It
does not claim empirical findings until real source data are supplied.

The real-data pipeline is separate. Copy `config/sources.sample.yml` to
`config/sources.yml`, point it at local raw GPR and Fama-French files, then run
`make data-real` or `make pipeline-real`. Raw source files under `data/raw/`
must stay out of git.

Real-data milestones are staged:

- V0.1a: real GPR plus real developed/emerging Fama-French returns.
- V0.1b: add a real GDELT event-intensity index.
- V0.1c: add real macro controls.

Return columns are monthly percentage points, not decimals. For Fama-French
factor files, `Mkt-RF` becomes `excess_return`, `RF` becomes `risk_free_rate`,
and `return_usd = excess_return + risk_free_rate`.

Important limitation: the two-market aggregate sample cannot support credible clustered panel inference. Country-clustered panel inference requires a country-level panel with enough independent country clusters.

Generated public outputs:

- `reports/tables/table_01_summary_stats.csv`
- `reports/tables/table_02_baseline_regressions.csv`
- `reports/tables/table_03_forecast_comparison.csv`
- `reports/figures/fig_01_gpr_timeseries.png`
- `reports/figures/fig_02_em_dev_spread.png`
- `reports/figures/fig_03_local_projection.png`
- `reports/figures/fig_04_gdelt_vs_gpr.png`
- `reports/main_report.pdf`
- `dashboard/index.html`

## Main documentation

- [Project specification](docs/PROJECT_SPEC.md)
- [Data sources and licensing notes](docs/DATA_SOURCES.md)
- [Methodology](docs/METHODOLOGY.md)
- [Reproducibility guide](docs/REPRODUCIBILITY.md)
- [Roadmap](docs/ROADMAP.md)
- [Grill questions](docs/GRILL_QUESTIONS.md)
- [Acceptance criteria](docs/ACCEPTANCE_CRITERIA.md)

## Scope discipline

Do not start with firm-level stock prediction, intraday trading, or deep learning. The first version should be econometrics-first, with a small forecasting module added only after the baseline data and inference pipeline are stable.

## Data policy

Do not commit raw third-party market data. Commit only scripts, metadata, small toy samples, and derived results that comply with the relevant source terms.

## Suggested citation

Use `CITATION.cff` for repository citation metadata. Archive a tagged release through Zenodo only if you need a DOI.
