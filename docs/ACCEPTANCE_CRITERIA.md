# Acceptance Criteria

## Version 0.1: credible public project

The project can be public when all criteria below are satisfied.
The V0.1a real-data milestone is intentionally narrower and should not be
described as satisfying this full checklist until the robustness items are
reported.

### Documentation

- README explains what the project does, why it matters, how to run it, and what the main findings are.
- DATA_SOURCES explains every data source and redistribution constraint.
- METHODOLOGY explains shock construction, regressions, forecasting design, and limitations.
- REPRODUCIBILITY explains how to rebuild outputs.
- LICENSE exists.
- CITATION.cff exists.

### Data

- Data pipeline creates a monthly panel.
- Each raw source has metadata.
- No raw paid or restricted market data are committed.
- All date columns are standardised.
- There are no duplicate panel keys.
- Missing values are reported, not silently dropped.

### Econometrics

- Baseline spread regression implemented.
- Main coefficient has a clear interpretation.
- HAC or clustered standard errors used.
- At least three robustness checks are reported.
- Results are saved to reproducible tables.

### GDELT

- Event filters are documented.
- Country-month aggregation works.
- Index is compared with GPR.
- Limitations are stated clearly.

### Forecasting

- Time-series split is rolling or expanding, not random.
- Historical mean or AR baseline included.
- Metrics are out of sample.
- Leakage check exists.
- ML results are reported even if weak.

### Code quality

- Package imports cleanly.
- `make test` passes.
- `ruff check` or equivalent linting passes.
- Functions are not hidden inside notebooks.
- Config is separated from code.
- Secrets are read from environment variables.

### Public presentation

- Main figure is understandable in 30 seconds.
- Project has a short abstract.
- Results do not overclaim causality.
- Limitations are visible, not buried.
- Repo looks maintained.

## Version 1.0: strong profile project

Additional criteria:

- Country-level panel implemented.
- Local projections implemented.
- Forecasting module has at least three models.
- Dashboard or static project page released.
- Report PDF generated from code.
- GitHub release tagged.
- Optional DOI minted through Zenodo.
