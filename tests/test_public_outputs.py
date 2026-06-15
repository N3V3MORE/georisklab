from pathlib import Path


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
