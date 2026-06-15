# Methodology

## Identification logic

The project should not claim clean causal identification from a simple return regression. The honest claim is narrower:

> The project estimates conditional associations and dynamic market responses around geopolitical risk shocks, then tests whether those responses differ between emerging and developed markets.

Any causal language must be limited unless the design includes stronger identification, such as plausibly exogenous event timing, narrow event windows, or external instruments.

## Shock construction

### Option A: Standardised GPR innovation

1. Take log GPR if the distribution is highly skewed.
2. Remove predictable components using an AR model or lagged controls.
3. Standardise residuals.

```text
gpr_shock_t = residual from log_gpr_t ~ log_gpr_t-1 + controls_t-1
```

### Option B: High-risk event month

```text
high_gpr_t = 1 if gpr_t is above its rolling 90th percentile
```

This is easier to explain but loses information.

### Option C: Threats versus acts

Estimate separate responses to:

```text
gprt_shock_t     geopolitical threats
gpra_shock_t     realised geopolitical acts
```

## GDELT index construction

### Basic version

For country i and month t:

```text
gdelt_risk_i,t = log(1 + conflict_count_i,t + protest_count_i,t + sanction_count_i,t + diplomatic_conflict_count_i,t)
```

### Weighted version

```text
gdelt_risk_i,t = log(1 + sum_events weight_event)
```

Candidate weights:

```text
abs(min(goldstein_score, 0))
negative_tone_intensity
category_severity_weight
```

Keep the weighting transparent. Do not use an opaque score unless you can explain it in one paragraph.

## Return construction

### Monthly returns

```text
ret_t = 100 * log(price_t / price_t-1)
```

### Excess returns

```text
excess_ret_t = ret_t - risk_free_t
```

If risk-free alignment is messy, use raw USD returns in version 0.1 and document the limitation.

### Forward cumulative returns

```text
ret_fwd_3m_t = ret_t+1 + ret_t+2 + ret_t+3
```

Be explicit that predictors are measured at t and outcomes are future returns.

## Baseline regressions

### Aggregate spread model

```text
spread_em_dev_t+h = alpha_h + beta_h * gpr_shock_t + gamma_h' controls_t + error_t+h
```

Purpose:

- Simple first test.
- Easy to plot.
- Good for README and dashboard.

Weakness:

- Low sample size.
- Hard to separate global shocks.

### Panel interaction model

```text
r_i,t+h = alpha_i + lambda_t + beta_h * gpr_i,t + theta_h * emerging_i * gpr_i,t + gamma_h' X_i,t + error_i,t+h
```

Key coefficient:

```text
theta_h
```

Interpretation:

- Difference in response between emerging and developed markets, conditional on controls and fixed effects.

## Inference

Minimum:

- HAC standard errors for time-series regressions.
- Country-clustered standard errors for panel regressions.
- Driscoll-Kraay as robustness if cross-sectional dependence is serious.

Do not report naive ordinary least squares standard errors as the main result.

## Forecasting design

### Train-test split

Use expanding-window or rolling-window validation.

Forbidden:

- Random train-test split for time series.
- Using future macro revisions without acknowledging vintage problems.

### Models

Version 0.1:

1. Historical mean.
2. AR model.
3. Elastic net.
4. Random forest or gradient boosting.

Stretch:

1. Small neural network.
2. Text embeddings from public GDELT text fields, if legally and technically feasible.

### Forecast targets

Start with:

```text
next_month_negative_return
next_month_volatility
emerging_minus_developed_return_spread
```

Volatility and downside risk are more plausible than point return prediction.

## Robustness checks

Required:

1. Replace GPR level with GPR shock.
2. Use threats and acts separately.
3. Exclude 2008-2009, 2020, and major war-onset months one at a time.
4. Winsorise extreme returns.
5. Change emerging/developed classification.
6. Run placebo dates.
7. Use alternative horizons.
8. Report whether results survive controls.

## Interpretation rules

Allowed:

- “Associated with”.
- “Predicts out of sample within this validation design”.
- “Emerging markets exhibit a larger conditional response”.

Avoid unless strongly justified:

- “Causes”.
- “Proves”.
- “Tradeable signal”.
- “Markets are inefficient”.
