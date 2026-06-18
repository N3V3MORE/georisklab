# Start Here

This file is the plain-English guide to the project.

## The Short Version

GeoRiskLab asks one main question:

> Do emerging equity markets respond differently from developed markets after
> geopolitical risk shocks?

The repo is set up like a small research factory:

1. Build monthly data.
2. Build the analysis panel.
3. Check that the data are usable.
4. Run regressions and forecasts.
5. Make tables, figures, dashboard, and report.
6. Run tests so changes do not quietly break the workflow.

## The One Command To Try First

```bash
python scripts/run_task.py pipeline
```

This runs the sample pipeline. It uses deterministic toy data, so it is safe to
run without private files or API keys.

If setup has not been done yet, run this first:

```bash
python scripts/run_task.py setup
```

## What To Open After Running

- `dashboard/index.html` - quick visual summary.
- `reports/tables/` - generated CSV tables.
- `reports/figures/` - generated PNG figures.
- `reports/main_report.pdf` - local report build.

## Which Files Matter Most

For understanding the project:

- `README.md` - short public overview.
- `docs/ROADMAP.md` - what is done, what is next, and what not to claim.
- `docs/METHODOLOGY.md` - research design and interpretation rules.
- `docs/DATA_SOURCES.md` - source notes, schemas, and data policy.
- `docs/REPRODUCIBILITY.md` - how to rebuild and check outputs.

For normal project use:

- `scripts/run_task.py` - the simple command runner.
- `scripts/build_monthly_data.py` - creates sample monthly data.
- `scripts/build_real_monthly_data.py` - reads user-supplied real source files.
- `scripts/build_features.py` - builds the analysis panel.
- `scripts/validate_data.py` - checks that data and outputs are not misleading.
- `scripts/run_regressions.py` - builds regression results.
- `scripts/run_forecasts.py` - builds forecast-comparison results.
- `scripts/make_figures.py` - builds figures.
- `scripts/build_report.py` - builds the PDF report.

For code reuse:

- `georisklab/ingest/` - source-data readers.
- `georisklab/features/` - panel, returns, and shock features.
- `georisklab/econometrics/` - regressions and local projections.
- `georisklab/models/` - forecasting helpers.
- `georisklab/utils/` - shared project helpers.

## Sample Mode Versus Real Mode

Sample mode is for checking that the project works:

```bash
python scripts/run_task.py pipeline
```

Real mode is for user-supplied source data:

```bash
python scripts/run_task.py pipeline-real
```

Real mode expects `config/sources.yml` to point at the raw files. The sample
config file is `config/sources.sample.yml`.

## Rules I Should Not Break

These checks may look strict, but they protect the research:

- Do not remove manifest checks. They prove which files were used.
- Do not remove placeholder warnings. They stop staged inputs from looking real.
- Do not remove common-sample alignment. It keeps GPR and returns on matching dates.
- Do not remove the clustered-inference guard. The current aggregate sample is
  too small for credible country-clustered panel inference.
- Do not headline sample outputs as empirical findings.

## How To Check The Repo

Run:

```bash
python scripts/run_task.py pipeline
python scripts/run_task.py test
python scripts/run_task.py lint
```

If all three pass, the sample workflow, tests, and code style are in good shape.
