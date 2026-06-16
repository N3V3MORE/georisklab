from importlib import import_module
from pathlib import Path


def test_makefile_has_full_pipeline_target():
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert (
        ".PHONY: setup data-monthly data-real features regressions forecasts figures "
        "report validate-data validate-results pipeline pipeline-real test lint"
    ) in makefile
    assert "pipeline:" in makefile
    assert (
        "data-monthly features validate-data regressions forecasts validate-results figures report"
        in makefile
    )


def test_makefile_has_real_pipeline_targets():
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "data-real:" in makefile
    assert "python scripts/build_real_monthly_data.py --config config/sources.yml" in makefile
    assert "python scripts/build_report.py --dataset $(DATASET)" in makefile
    assert "validate-results:" in makefile
    assert "pipeline-real:" in makefile
    assert (
        "data-real features validate-data regressions forecasts validate-results figures report"
        in makefile
    )


def test_validation_targets_distinguish_data_from_results(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "validate-data:\n\tpython scripts/validate_data.py --dataset $(DATASET)\n" in makefile
    assert (
        "validate-results:\n\tpython scripts/validate_data.py "
        "--dataset $(DATASET) --check-results\n"
    ) in makefile

    monkeypatch.syspath_prepend(str(root / "scripts"))
    run_task = import_module("run_task")

    assert "--check-results" not in run_task.TASKS["validate-data"][0]
    assert "--check-results" in run_task.TASKS["validate-results"][0]
    assert "--check-results" not in run_task.TASKS["validate-data-real"][0]
    assert "--check-results" in run_task.TASKS["validate-results-real"][0]


def test_ci_runs_sample_pipeline_before_tests():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "run: make pipeline" in workflow
    assert workflow.index("run: make pipeline") < workflow.index("run: pytest")


def test_ci_runs_declared_python_versions():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: ["3.10", "3.11"]' in workflow
    assert "python-version: ${{ matrix.python-version }}" in workflow
