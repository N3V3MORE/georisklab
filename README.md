# GeoRiskLab

Open-source empirical finance toolkit for measuring geopolitical risk and estimating asymmetric equity-market responses across emerging and developed markets.

## Purpose

GeoRiskLab turns a research question into a reproducible data product:

> Do geopolitical risk shocks affect emerging and developed equity markets differently, and can public event or news data improve forecasts of returns, volatility, and downside risk?

The first version is intentionally narrow. It focuses on monthly developed versus emerging equity returns, the Caldara-Iacoviello GPR index, a GDELT-based geopolitical event-intensity measure, and a small set of macro-financial controls.

## Minimum viable research product

The project is successful when a reviewer can clone the repo, run a documented pipeline, and reproduce:

1. A clean monthly panel from 1990 or 2000 onward.
2. A GPR shock series and a GDELT event-intensity series.
3. Baseline developed versus emerging market return results.
4. At least one panel regression table.
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
make test
```

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

Add `CITATION.cff` before the first public release and archive the release through Zenodo if you want a DOI.
