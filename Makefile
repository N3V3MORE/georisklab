DATASET ?= sample

.PHONY: setup data-monthly data-real features regressions forecasts figures report validate-data validate-results pipeline pipeline-real test lint

setup:
	python -m pip install -e .[dev]

data-monthly:
	python scripts/build_monthly_data.py

data-real:
	python scripts/build_real_monthly_data.py --config config/sources.yml

features:
	python scripts/build_features.py --dataset $(DATASET)

regressions:
	python scripts/run_regressions.py --dataset $(DATASET)

forecasts:
	python scripts/run_forecasts.py --dataset $(DATASET)

figures:
	python scripts/make_figures.py --dataset $(DATASET)

report:
	python scripts/build_report.py --dataset $(DATASET)

validate-data:
	python scripts/validate_data.py --dataset $(DATASET)

validate-results:
	python scripts/validate_data.py --dataset $(DATASET) --check-results

pipeline: data-monthly features validate-data regressions forecasts validate-results figures report

pipeline-real: DATASET=real
pipeline-real: data-real features validate-data regressions forecasts validate-results figures report

test:
	pytest

lint:
	ruff check .
