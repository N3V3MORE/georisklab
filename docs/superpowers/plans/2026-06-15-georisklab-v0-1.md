# GeoRiskLab V0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the documented GeoRiskLab research toolkit skeleton so package imports, pipeline commands, validation, tests, linting, and reproducible sample outputs work.

**Architecture:** Keep the project as a small Python package with separate modules for ingestion, feature construction, econometrics, forecasting, plotting, validation, and scripts. The default pipeline uses deterministic sample data so the repo is runnable without private data or API keys, while ingestion contracts accept local files or URLs for real data later.

**Tech Stack:** Python 3.10+, pandas, numpy, statsmodels, matplotlib, pytest, ruff.

---

## Spec Coverage

- README and docs define a monthly empirical finance toolkit, not a notebook project.
- Roadmap Milestone 0 requires package structure, `pyproject.toml`, Makefile targets, basic test, and CI.
- API contracts require named functions for GPR loading, market returns, GDELT aggregation, forward returns, shocks, regressions, time splits, metrics, and plots.
- Acceptance criteria require clean imports, `make test`, linting, config separated from code, no secrets, no raw restricted data, standard dates, duplicate checks, leakage checks, and visible limitations.

## File Map

- Create `pyproject.toml` for install, dependencies, pytest, and ruff.
- Create `LICENSE` because acceptance criteria require it and `CITATION.cff` declares MIT.
- Create `.github/workflows/ci.yml` for import, tests, and linting.
- Create `georisklab/` package modules matching the documented repo map.
- Create `scripts/` commands matching the Makefile.
- Create `tests/` with focused tests for dates, duplicate keys, forward returns, leakage, regressions, splits, metrics, and imports.
- Update `README.md`, `docs/REPRODUCIBILITY.md`, and `docs/METHODOLOGY.md` only where needed to explain sample-mode outputs and honest limitations.

## Tasks

### Task 1: Project Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `LICENSE`
- Create: `georisklab/__init__.py`
- Create: `georisklab/utils/config.py`
- Create: `georisklab/utils/validation.py`
- Create: `.github/workflows/ci.yml`
- Test: `tests/test_imports.py`

- [ ] **Step 1: Write failing import and validation tests**

```python
def test_package_imports():
    import georisklab

    assert georisklab.__version__ == "0.1.0"
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `pytest tests/test_imports.py -q`

Expected: FAIL because the package does not exist yet.

- [ ] **Step 3: Implement package skeleton and config**

Create the package files, path helpers, and validation helpers with one clear responsibility per file.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_imports.py -q`

Expected: PASS.

Commit: `chore: add python package skeleton`

### Task 2: Data Contracts and Sample Monthly Data

**Files:**
- Create: `georisklab/ingest/gpr.py`
- Create: `georisklab/ingest/market_returns.py`
- Create: `georisklab/ingest/gdelt.py`
- Create: `georisklab/ingest/world_bank.py`
- Create: `scripts/build_monthly_data.py`
- Test: `tests/test_ingest.py`

- [ ] **Step 1: Write failing ingestion tests**

Test that loaders standardise `date_month`, numeric columns, duplicate keys, and GDELT country-month aggregation.

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_ingest.py -q`

Expected: FAIL because ingestion modules do not exist yet.

- [ ] **Step 3: Implement ingestion and deterministic sample data**

Implement local file/URL loaders and a sample data builder that writes only `sample_*.csv` processed outputs plus source metadata.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_ingest.py -q`

Expected: PASS.

Commit: `feat: add monthly data ingestion contracts`

### Task 3: Features and Validation

**Files:**
- Create: `georisklab/features/returns.py`
- Create: `georisklab/features/shocks.py`
- Create: `scripts/build_features.py`
- Create: `scripts/validate_data.py`
- Test: `tests/test_features.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Write failing tests for forward returns and leakage checks**

Test that `ret_fwd_3m` uses future returns only and that train/test windows never overlap.

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_features.py tests/test_validation.py -q`

Expected: FAIL because feature modules do not exist yet.

- [ ] **Step 3: Implement features and data validation**

Implement forward returns, shock standardisation, duplicate checks, missingness reports, metadata checks, and sample `analysis_panel`.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_features.py tests/test_validation.py -q`

Expected: PASS.

Commit: `feat: build analysis panel features`

### Task 4: Econometrics, Forecasts, Figures, and Report

**Files:**
- Create: `georisklab/econometrics/results.py`
- Create: `georisklab/econometrics/baseline.py`
- Create: `georisklab/econometrics/local_projection.py`
- Create: `georisklab/models/splits.py`
- Create: `georisklab/models/metrics.py`
- Create: `georisklab/models/forecasting.py`
- Create: `georisklab/visualization/plots.py`
- Create: `scripts/run_regressions.py`
- Create: `scripts/run_forecasts.py`
- Create: `scripts/make_figures.py`
- Create: `scripts/build_report.py`
- Test: `tests/test_econometrics.py`
- Test: `tests/test_forecasting.py`

- [ ] **Step 1: Write failing tests for regressions, splits, and metrics**

Test HAC regression metadata, increasing time splits, regression metrics, and classification metrics.

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_econometrics.py tests/test_forecasting.py -q`

Expected: FAIL because modules do not exist yet.

- [ ] **Step 3: Implement analysis modules and scripts**

Implement reproducible CSV tables, plots, and a simple PDF report generated from saved outputs.

- [ ] **Step 4: Verify and commit**

Run: `pytest tests/test_econometrics.py tests/test_forecasting.py -q`

Expected: PASS.

Commit: `feat: add econometrics and forecasting pipeline`

### Task 5: Full Pipeline, Docs, and Final Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/REPRODUCIBILITY.md`
- Modify: `docs/METHODOLOGY.md`
- Modify: `.gitignore` if generated local outputs need to remain untracked.

- [ ] **Step 1: Run the full documented workflow**

Run:

```bash
make data-monthly
make features
make validate-data
make regressions
make forecasts
make figures
make report
make test
make lint
```

- [ ] **Step 2: Update docs with exact sample workflow**

Document that the default runnable pipeline uses deterministic sample data and does not claim empirical findings until real source data are supplied.

- [ ] **Step 3: Final verification and commit**

Run:

```bash
make test
make lint
```

Expected: both commands exit successfully.

Commit: `docs: document reproducible sample workflow`

