# GeoRiskLab V0.1a Findings

## Data

Sample period: 2000-01-01 to 2026-04-01
Number of months: 316
Return source: Kenneth French Developed Factors and Kenneth French Emerging Factors
GPR source: Caldara-Iacoviello GPR export
Main shock: `gpr_change_z` (standardized monthly change in GPR)
Dependent variable: `spread_em_dev` (emerging minus developed next-month excess-return spread)

## Baseline result

| Horizon | Estimate | Std. Error | p-value | Interpretation |
|---|---:|---:|---:|---|
| 1m | -0.018622 | 0.213225 | 0.930404 | Small negative sign, but economically tiny relative to noise. |
| 3m | -0.125803 | 0.581777 | 0.828801 | Negative sign remains, but the interval is very wide. |
| 6m | 0.398273 | 0.604668 | 0.510112 | Sign flips positive, so the horizon pattern is not stable. |

## Forecast comparison

| Model | RMSE | MAE | OOS R2 | Forecast window |
|---|---:|---:|---:|---|
| Historical mean | 2.939273 | 2.342179 | 0.000000 | 2012-02-01 to 2026-03-01 |
| GPR only | 2.991790 | 2.402845 | -0.036054 | 2012-02-01 to 2026-03-01 |
| Regularized GPR only | 2.989756 | 2.400752 | -0.034645 | 2012-02-01 to 2026-03-01 |

## Interpretation

A one-standard-deviation increase in the GPR change shock is associated with a 0.0186 percentage point lower emerging-minus-developed spread over the next month, a 0.1258 percentage point lower spread over three months, and a 0.3983 percentage point higher spread over six months. The current V0.1a result is fragile because the sign is not stable across horizons and the standard errors are large relative to the point estimates.

## Limitations

- Aggregate developed/emerging returns only.
- No real GDELT yet.
- No macro controls yet.
- Descriptive, not causal.
- Results may be crisis-period sensitive.

## Next checks

- Alternative GPR shock definitions.
- Crisis-period exclusions.
- GPR threats versus acts.
