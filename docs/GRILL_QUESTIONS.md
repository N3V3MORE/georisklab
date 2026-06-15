# Grill Questions

Use these questions to test whether the project is serious enough to show to professors, RA supervisors, or quant/economics recruiters.

## Project fit

1. What is the exact empirical claim you want a reader to believe?
2. Is the project a research contribution, a software contribution, or a dashboard? Rank these.
3. Why should someone care about emerging versus developed asymmetry?
4. What does this project add beyond your existing paper?
5. What result would make the project unsuccessful?

## Data credibility

1. Why is GDELT a valid proxy for geopolitical risk rather than just media attention?
2. How will you handle the fact that English-language and global media coverage is uneven across countries?
3. Why should GPR be the benchmark index?
4. How do you avoid mixing threats, realised acts, and general political uncertainty?
5. What raw data are you allowed to redistribute?
6. Which variables are revised after release, and does that matter for forecasting?
7. What is the smallest sample that still answers the question?
8. Are you using country-level returns, regional aggregates, or factor returns? Why?

## Econometrics

1. What is the dependent variable in the main table?
2. What is the exact shock variable?
3. What is the identifying variation?
4. What fixed effects are included and why?
5. Why are naive OLS standard errors not enough?
6. Are your horizons overlapping? If yes, how do you handle serial correlation?
7. What controls are bad controls?
8. What would omitted global risk appetite do to your coefficient?
9. How will you separate geopolitical risk from oil shocks, dollar shocks, and financial stress?
10. What is the main coefficient and how do you interpret its units?

## Machine learning

1. Why is ML needed at all?
2. What is the baseline that ML must beat?
3. Are you predicting returns, volatility, or downside risk? Why?
4. How do you prevent leakage in rolling-window validation?
5. What metric decides whether GDELT adds value?
6. What will you say if ML does not improve forecast performance?
7. Are you using too many features for the sample size?
8. How will you explain feature importance without overclaiming?

## Research honesty

1. What result would falsify your preferred story?
2. Which countries or periods drive the result?
3. Does the result survive excluding 2008, 2020, and major war-onset months?
4. Does the result survive alternative emerging-market definitions?
5. Could the effect simply be global risk-off sentiment?
6. Are you measuring economic exposure or only geographic exposure?
7. What are the three biggest limitations?
8. What do you refuse to claim?

## GitHub quality

1. Can a stranger run the main pipeline from the README?
2. Are notebooks optional or required?
3. Is every table generated from code?
4. Is every figure generated from code?
5. Are data-source terms documented?
6. Are raw data excluded from git?
7. Do tests cover at least date alignment, duplicate keys, and leakage?
8. Does the repo look like research software or a school assignment?

## Profile signal

1. Which skill does this project prove: economics, statistics, coding, ML, or research design?
2. What one sentence would you put on your CV?
3. What would a professor ask after seeing the README?
4. What would a quant interviewer attack first?
5. What is the cleanest figure to show in an application email?
