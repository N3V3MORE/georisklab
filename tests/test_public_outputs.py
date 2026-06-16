from pathlib import Path


def test_citation_repository_points_to_public_repo():
    root = Path(__file__).resolve().parents[1]
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")

    assert "repository-code: https://github.com/N3V3MORE/georisklab" in citation
    assert "your-username" not in citation


def test_docs_state_two_market_panel_limitation():
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    methodology = (root / "docs" / "METHODOLOGY.md").read_text(encoding="utf-8")

    required = "two-market aggregate sample cannot support credible clustered panel inference"
    assert required in readme
    assert required in methodology


def test_dashboard_static_page_links_generated_outputs():
    root = Path(__file__).resolve().parents[1]
    page = root / "dashboard" / "index.html"

    assert page.exists()
    html = page.read_text(encoding="utf-8")
    assert "../reports/figures/fig_01_gpr_timeseries.png" in html
    assert "deterministic sample data" in html


def test_root_page_links_to_dashboard():
    root = Path(__file__).resolve().parents[1]
    page = root / "index.html"

    assert page.exists()
    html = page.read_text(encoding="utf-8")
    assert "dashboard/index.html" in html


def test_methodology_labels_ar1_residual_as_descriptive_full_sample():
    root = Path(__file__).resolve().parents[1]
    methodology = (root / "docs" / "METHODOLOGY.md").read_text(encoding="utf-8")

    assert "gpr_ar1_residual_z" in methodology
    assert "full-sample descriptive residual shock" in methodology
    assert "not for real-time forecasting" in methodology


def test_real_data_report_outputs_are_gitignored():
    root = Path(__file__).resolve().parents[1]
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")

    assert "reports/main_report_real.pdf" in gitignore
    assert "reports/tables/*_real.csv" in gitignore
    assert "reports/figures/*_real.png" in gitignore
