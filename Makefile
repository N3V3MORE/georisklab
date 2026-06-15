.PHONY: setup data-monthly features regressions forecasts figures report validate-data pipeline test lint

setup:
	python -m pip install -e .[dev]

data-monthly:
	python scripts/build_monthly_data.py

features:
	python scripts/build_features.py

regressions:
	python scripts/run_regressions.py

forecasts:
	python scripts/run_forecasts.py

figures:
	python scripts/make_figures.py

report:
	python scripts/build_report.py

validate-data:
	python scripts/validate_data.py

pipeline: data-monthly features validate-data regressions forecasts figures report

test:
	pytest

lint:
	ruff check .
