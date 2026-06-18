# GeoRiskLab

GeoRiskLab is a reproducible research project for studying how geopolitical risk
relates to developed and emerging equity-market returns.

The project has two modes:

- **Sample mode:** uses deterministic toy data so anyone can test the code.
- **Real mode:** uses user-supplied GPR and Fama-French files, with provenance
  checks before results are treated as real-data outputs.

If you are new to the repo, start here:

- [Start Here](START_HERE.md)
- [Project status and roadmap](docs/ROADMAP.md)
- [Methodology](docs/METHODOLOGY.md)
- [Reproducibility guide](docs/REPRODUCIBILITY.md)
- [Data sources](docs/DATA_SOURCES.md)

## What It Builds

The default pipeline rebuilds:

- a monthly analysis panel,
- missingness and summary-statistics tables,
- baseline regression and forecast-comparison tables,
- figures for GPR, return spreads, local projections, GDELT comparison, and forecasts,
- a static dashboard at `dashboard/index.html`,
- a local PDF report.

The default outputs use sample data. They prove the workflow runs, but they do
not claim empirical findings.

## Quick Run

Install the project:

```bash
python scripts/run_task.py setup
```

Run the sample pipeline:

```bash
python scripts/run_task.py pipeline
```

Run checks:

```bash
python scripts/run_task.py test
python scripts/run_task.py lint
```

If you have `make`, the matching command is:

```bash
make pipeline
```

## Real Data

Real-data runs are separate from sample runs.

1. Copy `config/sources.sample.yml` to `config/sources.yml`.
2. Point it at local raw source files under `data/raw/`.
3. Run:

```bash
python scripts/run_task.py pipeline-real
```

Raw files, local source config, real-data figures, real-data tables, and real-data
PDF reports are local artifacts by default. They should not be committed unless
the project intentionally publishes a release artifact.

## Important Limits

The two-market aggregate sample cannot support credible clustered panel inference.
Country-clustered panel inference requires a country-level panel with enough
independent country clusters.

Current real-data forecasts are intentionally narrow: historical mean, GPR-only
linear, and ridge-regularized GPR-only models. AR, elastic net, and tree-based
models remain future extensions until they are actually implemented.

## Repo Map

```text
georisklab/      reusable Python package
scripts/         commands that build data, tables, figures, and reports
data/            ignored raw/interim files plus small reproducible samples
reports/         generated tables, figures, and local reports
dashboard/       static HTML dashboard
docs/            method, data, reproducibility, and project notes
tests/           checks that protect the workflow
```

## Data Policy

Do not commit raw third-party market data. Commit only scripts, metadata, small
toy samples, and derived results that comply with the relevant source terms.
