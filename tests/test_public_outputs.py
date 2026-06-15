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
