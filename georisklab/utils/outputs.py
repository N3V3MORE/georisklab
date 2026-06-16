from pathlib import Path

from georisklab.utils.config import ProjectPaths


def table_path(paths: ProjectPaths, filename: str, dataset: str) -> Path:
    return paths.reports_tables / _dataset_filename(filename, dataset)


def figure_path(paths: ProjectPaths, filename: str, dataset: str) -> Path:
    return paths.reports_figures / _dataset_filename(filename, dataset)


def report_path(paths: ProjectPaths, dataset: str) -> Path:
    if dataset == "sample":
        return paths.root / "reports" / "main_report.pdf"
    if dataset == "real":
        return paths.root / "reports" / "main_report_real.pdf"
    raise ValueError("dataset must be 'sample' or 'real'")


def _dataset_filename(filename: str, dataset: str) -> str:
    if dataset == "sample":
        return filename
    if dataset == "real":
        path = Path(filename)
        return f"{path.stem}_real{path.suffix}"
    raise ValueError("dataset must be 'sample' or 'real'")
