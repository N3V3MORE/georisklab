# Internal API Contracts

This file defines function-level contracts before implementation. It prevents the project from becoming a pile of notebooks.

## Ingestion

### `load_gpr(path_or_url: str) -> pd.DataFrame`

Returns:

```text
date_month
gpr_global
gprt_global
gpra_global
country_iso3 optional
gpr_country optional
```

Rules:

- `date_month` must be first day of month.
- Numeric columns must be floats.
- No duplicate date-country keys.

### `load_fama_french_factor_returns(source: str, market_id: str, market_class: str) -> pd.DataFrame`

Returns:

```text
date_month
market_id
market_class
return_usd
risk_free_rate
excess_return
source
source_download_date
```

Rules:

- Returns are monthly percent values, not decimals.
- For Fama-French factor files, `Mkt-RF` maps to `excess_return`, `RF` maps to `risk_free_rate`, and `return_usd = excess_return + risk_free_rate`.
- Local files and HTTPS zip sources with expected SHA-256 hashes must both be supported for Fama-French factor ingestion.
- `load_fama_french_market_returns(source: str)` is a normalized CSV loader for already tabular project-shaped returns.
- Developed and emerging market identifiers must be standardised as `developed` and `emerging`.
- Missing-value sentinels such as `-99.99` must fail validation rather than enter outputs.

### `load_world_bank_indicator(indicator: str, countries: list[str]) -> pd.DataFrame`

Returns:

```text
date_month
country_iso3
indicator_code
value
```

Rules:

- Preserve annual frequency as January month-start dates.
- Aggregate country rows and forward-fill annual values to monthly aggregate panels in the feature step.

### `build_gdelt_country_month(events: pd.DataFrame, filters: dict) -> pd.DataFrame`

Returns:

```text
date_month
country_iso3
event_count
conflict_count
protest_count
sanction_count
diplomatic_conflict_count
avg_goldstein
avg_tone
risk_index_raw
risk_index_zscore
source_download_date
filter_version
```

Rules:

- All filters must be saved to metadata.
- Empty country-months should be explicit zeros where appropriate.
- `risk_index_zscore` is standardised within `country_iso3`, not globally across all countries.
- Aggregate panels convert country-month GDELT rows to one row per `date_month` before merging.

## Features

### `make_forward_returns(df: pd.DataFrame, horizons: list[int]) -> pd.DataFrame`

Rules:

- Predictors at month t must map only to outcomes after t.
- No future data in features.

### `standardize_shocks(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame`

Rules:

- Standardisation parameters must be computed inside training windows for forecasting.
- Full-sample standardisation is allowed only for descriptive regressions and must be documented.
- Forecast features should use prior-only expanding standardisation, not full-sample z-scores.

## Econometrics

### `run_spread_regression(panel: pd.DataFrame, horizon: int, config: dict) -> RegressionResult`

Outputs:

```text
coefficient table
model metadata
sample size
adjusted r2
standard error type
```

### `run_panel_interaction(panel: pd.DataFrame, horizon: int, config: dict) -> RegressionResult`

Rules:

- Must support market fixed effects.
- Must support time fixed effects.
- Must support clustered standard errors.
- Must reject clustered inference when the available cluster count is too small for the configured guardrail.

## Forecasting

### `make_time_splits(dates: pd.Series, min_train_months: int, test_window: int) -> list[Split]`

Rules:

- Dates must be increasing.
- Test dates must always be after train dates.

### `evaluate_forecasts(y_true, y_pred, task: str, benchmark_pred=None) -> dict`

For regression:

```text
rmse
mae
oos_r2
```

Regression `oos_r2` requires `benchmark_pred` and must use a benchmark forecast produced at the forecast origin, such as the historical training-window mean.

For classification:

```text
brier_score
log_loss
directional_accuracy
```

## Visualisation

### `plot_gpr_timeseries(df) -> matplotlib.figure.Figure`

### `plot_local_projection(results) -> matplotlib.figure.Figure`

### `plot_forecast_comparison(metrics) -> matplotlib.figure.Figure`

Rules:

- Plots must be generated from saved outputs.
- No manual editing of final figures.
