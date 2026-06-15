# Project Specification

## Working title

GeoRiskLab: Measuring and Forecasting Asymmetric Equity Market Responses to Geopolitical Risk Using Open Data

## User story

As an economics and quantitative methods student, I want a reproducible research system that downloads public geopolitical, macroeconomic, and market data, constructs risk measures, estimates market responses, and reports whether emerging markets respond differently from developed markets.

## Research question

Main question:

> Are emerging equity markets more sensitive than developed equity markets to geopolitical risk shocks?

Secondary questions:

1. Are effects stronger for realised geopolitical acts than for geopolitical threats?
2. Are effects visible in returns, volatility, downside risk, or all three?
3. Do GDELT-derived event measures add information beyond the Caldara-Iacoviello GPR index?
4. Do macro-financial vulnerabilities, such as inflation, external debt, FX pressure, or current-account weakness, amplify the response?
5. Does geopolitical risk improve out-of-sample forecasts relative to simple macro-financial baselines?

## Version 0.1 target

Version 0.1 should be a monthly aggregate study, not a full global daily event-study platform.

### Unit of observation

Preferred first design:

```text
region_or_country x month
```

Start with:

- Developed market aggregate return.
- Emerging market aggregate return.
- Optional country-level extension for 10 to 20 countries after the aggregate result works.

### Time coverage

Recommended start:

```text
2000-01 to latest available month
```

Possible extended start:

```text
1990-01 to latest available month
```

Use the longer sample only if all major variables are available and consistently defined.

## Hypotheses

### H1: Risk shock effect

A positive geopolitical risk shock is associated with lower subsequent equity returns.

### H2: Asymmetry by market classification

The negative return response is larger for emerging markets than for developed markets.

### H3: Volatility channel

Geopolitical risk shocks increase realised or forecast volatility, with a stronger effect in emerging markets.

### H4: Downside-risk channel

Geopolitical risk shocks increase left-tail risk more than they affect mean returns.

### H5: Threats versus acts

Realised geopolitical acts have larger immediate equity-market effects than geopolitical threats.

### H6: Incremental information

GDELT-based event-intensity features add predictive or explanatory power beyond the benchmark GPR index.

## Key dependent variables

### Return targets

```text
ret_1m              monthly excess return
ret_fwd_1m          one-month forward excess return
ret_fwd_3m          three-month cumulative forward excess return
ret_fwd_6m          six-month cumulative forward excess return
spread_em_dev       emerging minus developed market return
```

### Risk targets

```text
vol_1m              monthly realised volatility from daily returns if daily data are available
neg_ret_1m          indicator equal to 1 if next-month return is negative
left_tail_1m        indicator equal to 1 if next-month return is below the 10th percentile
max_drawdown_1m     monthly maximum drawdown if daily data are available
```

## Key explanatory variables

### Benchmark geopolitical risk

```text
gpr_global          global benchmark GPR index
gprt_global         geopolitical threats subindex
gpra_global         geopolitical acts subindex
gpr_country         country-specific GPR index if available
```

### GDELT event-intensity features

```text
gdelt_event_count               event count by country-month
gdelt_conflict_count            conflict-coded event count
gdelt_protest_count             protest-coded event count
gdelt_sanction_count            sanction-coded event count
gdelt_diplomatic_conflict_count diplomatic conflict event count
gdelt_avg_tone                  average event/news tone where available
gdelt_avg_goldstein             average Goldstein score where available
gdelt_risk_index                weighted index built from selected event categories
```

### Controls

```text
epu_global_or_country     economic policy uncertainty
vix_or_global_vol_proxy   global risk appetite proxy, if available from a permissible source
oil_return                oil price return
usd_index_return          dollar movement proxy
policy_rate               short-term rate or policy-rate proxy
inflation_yoy             inflation
industrial_production     growth or cycle proxy
current_account_gdp       external balance vulnerability
external_debt_gni         external debt vulnerability
fx_return                 local currency depreciation proxy
```

## Data model

### Table: calendar

```text
date_month        YYYY-MM-01
month_end         month-end date
quarter           calendar quarter
year              calendar year
```

### Table: market_returns_monthly

```text
date_month
market_id         developed, emerging, or country ISO3
market_class      developed or emerging
return_usd
risk_free_rate
excess_return
source
source_download_date
```

### Table: gpr_monthly

```text
date_month
gpr_global
gprt_global
gpra_global
gpr_country
country_iso3
source_download_date
```

### Table: gdelt_country_monthly

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

### Table: macro_controls_monthly

```text
date_month
country_iso3
indicator_code
value
frequency_original
frequency_converted
source
source_download_date
```

### Table: analysis_panel

```text
date_month
market_id
market_class
excess_return
ret_fwd_1m
ret_fwd_3m
ret_fwd_6m
gpr_global_z
gpra_global_z
gprt_global_z
gdelt_risk_z
controls...
```

## Minimum methods

### Baseline time-series regression

```text
spread_em_dev_t+h = alpha_h + beta_h * gpr_shock_t + gamma_h' controls_t + error_t+h
```

### Panel regression

```text
r_i,t+h = alpha_i + lambda_t + beta_h * gpr_i,t + theta_h * emerging_i * gpr_i,t + gamma_h' X_i,t + error_i,t+h
```

### Local projections

For horizons h in 0, 1, 3, 6:

```text
cum_return_i,t,t+h = alpha_i,h + lambda_t,h + beta_h * shock_t + theta_h * emerging_i * shock_t + gamma_h' X_i,t + error_i,t+h
```

### Forecast comparison

Compare:

1. Historical mean or AR baseline.
2. Macro-only model.
3. Macro plus GPR model.
4. Macro plus GPR plus GDELT model.
5. One ML model with regularisation or tree-based nonlinearities.

## Forecast metrics

```text
rmse
mae
out_of_sample_r2
directional_accuracy
brier_score for binary downside target
auc only as secondary diagnostic
```

## Non-goals for version 0.1

- No claim of tradeable alpha.
- No intraday strategy.
- No black-box LLM market predictor.
- No scraped proprietary news corpus.
- No redistribution of raw third-party market data.
- No over-large country universe before the pipeline is correct.

## Final public outputs

1. GitHub repository.
2. Reproducible pipeline.
3. Main table and figure outputs.
4. Short methodology note.
5. Short report PDF generated from the repo.
6. Dashboard or static project page.
7. Honest limitations section.
