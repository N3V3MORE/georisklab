# Roadmap

This file is the durable milestone tracker. Historical implementation plans have
been folded into this roadmap and the reproducibility guide so there is one
place for project direction and one place for run instructions.

## Current V0.1 release track

### V0.1a: Aggregate real-data benchmark

Acceptance:

- Real Caldara-Iacoviello GPR is loaded from a local user-supplied source.
- Real developed/emerging Fama-French returns are loaded from local zip files.
- Baseline spread regressions, forecast comparisons, figures, and a short PDF
  report are generated.
- GDELT and macro controls are explicit placeholders and excluded from real
  empirical claims.

### V0.1b: Real GDELT extension

Acceptance:

- Real GDELT country-month event intensity is built for a documented country
  universe.
- Event filters and weighting are documented.
- The GDELT index is compared with benchmark GPR.

### V0.1c: Real macro controls

Acceptance:

- Real country-month macro controls are loaded from public sources.
- Controls are merged without silently collapsing country-level values into
  aggregate rows.
- Baseline results are rerun with controls and limitations updated.

## Milestone 0: Repo skeleton

Acceptance:

- README exists.
- Docs folder exists.
- Package imports successfully.
- Makefile or task runner exists.
- CI runs tests and linting.

Issues:

1. Create repo structure.
2. Add pyproject.toml.
3. Add Makefile.
4. Add README.
5. Add docs.
6. Add basic test.
7. Add GitHub Actions CI.

## Milestone 1: Monthly benchmark panel

Acceptance:

- GPR data downloaded or manually placed with documented source.
- Developed and emerging returns loaded.
- Monthly panel constructed.
- Summary statistics generated.

Issues:

1. Implement GPR ingestion.
2. Implement Fama-French ingestion.
3. Align monthly dates.
4. Construct return spread.
5. Add data validation checks.
6. Produce first summary table.

## Milestone 2: Baseline econometrics

Acceptance:

- Baseline spread regression works.
- Panel interaction model works if country-level data are available.
- HAC or clustered standard errors implemented.
- Results saved as CSV and LaTeX.

Issues:

1. Build `econometrics/baseline.py`.
2. Build `econometrics/local_projection.py`.
3. Add regression config.
4. Save model outputs.
5. Add tests on synthetic data.

## Milestone 3: GDELT event index

Acceptance:

- GDELT country-month index created for selected countries.
- Filters are documented.
- GDELT index compared with GPR.
- At least one validation figure produced.

Issues:

1. Define event categories.
2. Implement GDELT downloader or parser.
3. Aggregate to country-month.
4. Create weighted risk index.
5. Compare with GPR.
6. Add caveats to methodology.

## Milestone 4: Forecasting module

Acceptance:

- Expanding-window validation implemented.
- Baseline, macro-only, GPR, and GPR plus GDELT models compared.
- Metrics saved consistently.
- Leakage tests included.

Issues:

1. Implement time-series split.
2. Build baseline forecast model.
3. Build elastic net model.
4. Build tree model.
5. Add forecast metrics.
6. Add result table.

## Milestone 5: Dashboard or project page

Acceptance:

- Dashboard launches locally.
- Shows GPR time series, return spread, GDELT comparison, and main results.
- Does not require raw paid data.

Issues:

1. Create dashboard skeleton.
2. Add overview page.
3. Add risk-index page.
4. Add market-response page.
5. Add forecast page.
6. Add methodology page.

## Milestone 6: Public release

Acceptance:

- Report PDF generated.
- README has result screenshots.
- License added.
- Citation file added.
- Release tagged.
- Raw data policy clear.

Issues:

1. Write short paper.
2. Add limitations section.
3. Add final figures.
4. Add LICENSE.
5. Add CITATION.cff.
6. Create v0.1.0 release.
