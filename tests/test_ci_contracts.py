from pathlib import Path


def test_makefile_has_full_pipeline_target():
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert (
        ".PHONY: setup data-monthly data-real features regressions forecasts figures "
        "report validate-data pipeline pipeline-real test lint"
    ) in makefile
    assert "pipeline:" in makefile
    assert "data-monthly features validate-data regressions forecasts figures report" in makefile


def test_makefile_has_real_pipeline_targets():
    root = Path(__file__).resolve().parents[1]
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "data-real:" in makefile
    assert "python scripts/build_real_monthly_data.py --config config/sources.yml" in makefile
    assert "pipeline-real:" in makefile
    assert "data-real features validate-data regressions forecasts figures report" in makefile


def test_ci_runs_sample_pipeline_before_tests():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "run: make pipeline" in workflow
    assert workflow.index("run: make pipeline") < workflow.index("run: pytest")
