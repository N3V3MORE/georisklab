DATASET ?= sample
CONFIG ?= config/sources.yml
HORIZONS ?= 1,3,6
MIN_TRAIN_MONTHS ?= 120
MIN_OVERLAP_MONTHS ?= 120
MIN_FORECAST_TRAIN_MONTHS ?= 120

.PHONY: setup data-monthly data-real features regressions forecasts figures report validate-data validate-results check-generated pipeline pipeline-real test lint

setup:
	python -m pip install -c constraints.txt -e .[dev]

data-monthly:
	python scripts/build_monthly_data.py

data-real:
	python scripts/build_real_monthly_data.py --config $(CONFIG)

features:
	python scripts/build_features.py --dataset $(DATASET)

regressions:
	python scripts/run_regressions.py --dataset $(DATASET) --horizons $(HORIZONS)

forecasts:
	python scripts/run_forecasts.py --dataset $(DATASET) --min-train-months $(MIN_TRAIN_MONTHS)

figures:
	python scripts/make_figures.py --dataset $(DATASET)

report:
	python scripts/build_report.py --dataset $(DATASET)

validate-data:
	python scripts/validate_data.py --dataset $(DATASET) --min-overlap-months $(MIN_OVERLAP_MONTHS) --min-forecast-train-months $(MIN_FORECAST_TRAIN_MONTHS)

validate-results:
	python scripts/validate_data.py --dataset $(DATASET) --min-overlap-months $(MIN_OVERLAP_MONTHS) --min-forecast-train-months $(MIN_FORECAST_TRAIN_MONTHS) --check-results

check-generated:
	git ls-files --error-unmatch data/metadata/analysis_panel_manifest.json
	git diff --exit-code -- data/processed/sample_*.csv data/metadata/source_manifest.json data/metadata/analysis_panel_manifest.json reports/tables/*.csv reports/figures/*.png dashboard/index.html

pipeline: data-monthly features validate-data regressions forecasts validate-results figures report

pipeline-real: DATASET=real
pipeline-real: data-real features validate-data regressions forecasts validate-results figures report

test:
	pytest

lint:
	ruff check .
