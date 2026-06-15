# GeoRiskLab Review Items Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the ten review items around metadata, CI reproducibility, forecasting leakage, ingestion contracts, real-source examples, and limitations.

**Architecture:** Keep existing modules and add small helpers where contracts need to become explicit. CI should run the same sample pipeline a reviewer can run locally. Real-source examples must use tiny fixtures and documented URLs, not network-dependent CI downloads.

**Tech Stack:** Python 3.10+, pandas, numpy, statsmodels, matplotlib, pytest, ruff, Makefile, GitHub Actions.

---

## Task 1: Repository Metadata and CI Pipeline

**Files:**
- Modify: `CITATION.cff`
- Modify: `Makefile`
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_public_outputs.py`

- [ ] Add a test that `CITATION.cff` uses `https://github.com/N3V3MORE/georisklab`.
- [ ] Verify the test fails with the current placeholder.
- [ ] Add `pipeline` to `Makefile` and run it in CI before tests.
- [ ] Verify targeted tests and lint pass.
- [ ] Commit as `chore: fix repository metadata and ci pipeline`.

## Task 2: Forecasting Leakage and Metrics

**Files:**
- Modify: `georisklab/features/shocks.py`
- Modify: `georisklab/models/forecasting.py`
- Modify: `georisklab/models/metrics.py`
- Modify: `scripts/run_forecasts.py`
- Modify: `tests/test_features.py`
- Modify: `tests/test_forecasting.py`

- [ ] Add tests for expanding z-scores that do not use current or future rows.
- [ ] Add tests for OOS R2 against a supplied forecast-origin baseline.
- [ ] Verify those tests fail.
- [ ] Implement expanding z-scores and pass baseline predictions through forecast evaluation.
- [ ] Verify targeted tests and lint pass.
- [ ] Commit as `fix: remove forecast leakage`.

## Task 3: Ingestion Contracts and Real-Source Fixtures

**Files:**
- Modify: `georisklab/ingest/gpr.py`
- Modify: `georisklab/ingest/market_returns.py`
- Modify: `georisklab/ingest/world_bank.py`
- Modify: `georisklab/ingest/gdelt.py`
- Modify: `tests/test_ingest.py`

- [ ] Add tests for World Bank `date_month`, Fama-French risk-free/excess return handling, GDELT country z-scoring, and real-format GPR/Fama-French fixtures.
- [ ] Verify tests fail with current contracts.
- [ ] Implement the minimal contract changes.
- [ ] Verify targeted tests and lint pass.
- [ ] Commit as `fix: tighten ingestion contracts`.

## Task 4: Documentation and Limitations

**Files:**
- Modify: `docs/API_CONTRACTS.md`
- Modify: `docs/DATA_SOURCES.md`
- Modify: `docs/METHODOLOGY.md`
- Modify: `README.md`

- [ ] Document updated schemas and real-source fixture examples.
- [ ] Add explicit limitation that two aggregate markets do not provide credible clustered panel inference.
- [ ] Run full sample pipeline, tests, and lint.
- [ ] Commit as `docs: document empirical data limitations`.

