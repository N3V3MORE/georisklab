# Methodology

## Current Implementation

The runnable default pipeline uses deterministic sample data. It validates the
software workflow, output schemas, regressions, forecasts, figures, and report
generation. It is not evidence for the research hypotheses until real public
source data are supplied through the documented ingestion contracts.

The V0.1a real-data path uses real Caldara-Iacoviello GPR data and real Kenneth
French developed/emerging aggregate returns. GDELT event intensity and macro
controls remain staged extensions.

The two-market aggregate sample cannot support credible clustered panel inference.
Country-clustered panel inference requires a country-level panel with enough
independent country clusters. Do not interpret the current aggregate sample as a
credible panel-regression design.

## Identification Logic

The project should not claim clean causal identification from a simple return
regression. The honest claim is narrower:

> The project estimates conditional associations and dynamic market responses
> around geopolitical risk shocks, then tests whether those responses differ
> between emerging and developed markets.

Causal language requires a stronger design, such as plausibly exogenous event
timing, narrow event windows, or external instruments.

## Shock Measures

Current main measure:

```text
gpr_change_z
```

This is a standardized monthly change in global GPR.

Other implemented measures:

```text
gpr_level_z               high-risk-regime robustness measure
gpr_log_change_z          log-change version of the GPR shock
gpr_ar1_residual_z        full-sample descriptive residual shock
```

`gpr_ar1_residual_z` is a full-sample descriptive residual shock, not for real-time forecasting.
A future forecasting-safe version should use only information available before
the forecast origin.

The deterministic sample pipeline injects its synthetic return response using
the lagged `gpr_change_z` shock, so the sample regression estimates the same
signal that the sample data-generating process uses.

## Return Construction

Returns in project outputs are monthly percentage points, not decimals.

For Fama-French factor files:

```text
excess_return = Mkt-RF
risk_free_rate = RF
return_usd = excess_return + risk_free_rate
```

Forward cumulative returns are measured after the predictor month:

```text
ret_fwd_3m_t = ret_t+1 + ret_t+2 + ret_t+3
```

Predictors are measured at month `t`; outcomes are future returns.

## GDELT Index Plan

GDELT is a noisy media/event-coding proxy, not ground-truth geopolitical risk.
It should extend the benchmark GPR analysis, not replace it.

Planned simple index:

```text
gdelt_risk_i,t = log(1 + conflict_count_i,t + protest_count_i,t
                       + sanction_count_i,t + diplomatic_conflict_count_i,t)
```

Any weighted version must document the event categories and weights clearly.
Do not use an opaque score unless it can be explained in one paragraph.

## Regressions

Aggregate spread model:

```text
spread_em_dev_t+h = alpha_h + beta_h * gpr_shock_t + gamma_h' controls_t + error_t+h
```

Purpose:

- Simple first benchmark.
- Easy to plot.
- Useful for the dashboard and README.

Weakness:

- Small aggregate sample.
- Hard to separate GPR from broad global risk-off shocks.

Panel interaction model:

```text
r_i,t+h = alpha_i + lambda_t + beta_h * gpr_i,t
          + theta_h * emerging_i * gpr_i,t + gamma_h' X_i,t + error_i,t+h
```

Key coefficient:

```text
theta_h
```

Interpretation: difference in response between emerging and developed markets,
conditional on controls and fixed effects.

## Inference

Minimum standard:

- HAC standard errors for time-series regressions.
- Country-clustered standard errors only after a country-level panel has enough
  independent clusters.

Current safeguard:

- The aggregate `run_panel_interaction` helper rejects clustered inference when
  fewer than three `market_id` clusters are available. This blocks the current
  two-market aggregate sample from producing formal-looking clustered output,
  but it does not make small-cluster inference credible.

Do not report naive ordinary least squares standard errors as the main result.

## Forecasting

Current implemented real-data V0.1a forecast models:

1. Historical mean.
2. GPR-only linear model using `gpr_change`.
3. Ridge-regularized GPR-only linear model.

Current implemented target:

```text
emerging_minus_developed_return_spread
```

Sample-pipeline software checks also exercise macro-only, macro-plus-GPR,
macro-plus-GDELT, and ridge-regularized linear variants using deterministic
sample features. Those are software checks, not real empirical claims.

Rules:

- Use expanding-window or rolling-window validation.
- Do not use random train-test splits for time series.
- Do not use future macro revisions without documenting vintage problems.
- Keep forecast comparisons modest when the feature set is narrow.

Future models include AR, elastic net, tree-based models, and richer event/text
features only after the data pipeline supports them.

## Robustness Checks

Required before claiming the full V0.1 empirical release:

1. Replace GPR level with GPR shock.
2. Use threats and acts separately.
3. Exclude 2008-2009, 2020, and major war-onset months one at a time.
4. Winsorise extreme returns.
5. Change emerging/developed classification.
6. Run placebo dates.
7. Use alternative horizons.
8. Report whether results survive controls.

The current V0.1a findings are an initial real-data milestone, not the full
robustness package.

## Interpretation Rules

Allowed:

- "Associated with".
- "Predicts out of sample within this validation design".
- "Emerging markets exhibit a larger conditional response".

Avoid unless strongly justified:

- "Causes".
- "Proves".
- "Tradeable signal".
- "Markets are inefficient".
