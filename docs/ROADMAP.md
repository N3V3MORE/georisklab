# Project Status and Roadmap

This is the single tracker for what GeoRiskLab does now and what comes next.

## Current State

GeoRiskLab is at the V0.1a real-data milestone.

What works now:

- Deterministic sample pipeline for public CI and reproducible testing.
- Real-data pipeline for user-supplied Caldara-Iacoviello GPR and Kenneth French
  developed/emerging factor files.
- Monthly developed versus emerging analysis panel.
- Missingness, summary-statistics, regression, and forecast-comparison tables.
- GPR, spread, local-projection, GDELT comparison, and forecast figures.
- Static dashboard and local PDF report generation.
- Validation checks for duplicate keys, month-start dates, source metadata,
  common real-data samples, forecast windows, placeholder inputs, and generated
  result schemas.

What V0.1a does not claim:

- No causal proof.
- No tradeable signal.
- No credible clustered panel inference from the two-market aggregate sample.
- No real GDELT or real macro-control findings yet.

## Research Target

Main question:

> Are emerging equity markets more sensitive than developed equity markets to
> geopolitical risk shocks?

V0.1a answers this only as an initial aggregate benchmark. A stronger empirical
release needs real event and macro controls, robustness checks, and, eventually,
a country-level panel with enough independent clusters.

## Done

- Repo skeleton, package structure, license, citation file, tests, and linting.
- Sample monthly data and real aggregate GPR/Fama-French ingestion.
- Monthly feature construction and analysis-panel validation.
- Baseline local-projection style regressions.
- Expanding-window forecast comparison.
- Generated public tables, figures, dashboard, and PDF report.
- Raw-data policy and real-data artifact ignore rules.

## Next

### V0.1b: Real GDELT Extension

Build real country-month event intensity from GDELT.

Acceptance:

- Documented country universe.
- Documented event filters and weighting.
- Country-month aggregation with explicit zero handling where appropriate.
- GDELT index comparison against benchmark GPR.
- Updated methodology and limitations.

### V0.1c: Real Macro Controls

Add public macro controls without hiding aggregation problems.

Acceptance:

- Real public macro sources loaded with metadata.
- Country-month controls merged without silently collapsing country-level values
  into aggregate rows.
- Baseline results rerun with controls.
- Limitations updated wherever controls remain incomplete.

### V0.1 Full Empirical Release

Move beyond the initial benchmark.

Acceptance:

- At least three robustness checks reported.
- Results language remains conditional, not causal.
- Main figure and table are understandable without reading the code.
- README and dashboard show findings without overstating sample or real-data
  coverage.
- Release tag created only after outputs are rebuilt and checked.

## Later

Version 1.0 should add a country-level panel, enough clusters for credible
clustered inference, richer forecasting comparisons, and a stronger public
presentation. Do not expand into intraday trading, firm-level stock prediction,
or black-box market prediction before the research pipeline is solid.

## Guardrails

- Keep sample mode for CI and reproducibility.
- Keep real raw files, local source config, real-data tables, real-data figures,
  and real-data PDFs out of git unless publishing an explicit release artifact.
- Keep placeholder GDELT and macro inputs visible and excluded from real empirical
  claims.
- Keep common-sample alignment for real GPR and return data.
- Keep the weak-cluster inference guard.
- Keep docs narrower than the implementation whenever the code cannot support a
  stronger claim.
