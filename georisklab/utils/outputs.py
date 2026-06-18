from pathlib import Path

from georisklab.utils.config import ProjectPaths
from georisklab.utils.datasets import dataset_output_filename


def table_path(paths: ProjectPaths, filename: str, dataset: str) -> Path:
    return paths.reports_tables / dataset_output_filename(filename, dataset)


def figure_path(paths: ProjectPaths, filename: str, dataset: str) -> Path:
    return paths.reports_figures / dataset_output_filename(filename, dataset)


def report_path(paths: ProjectPaths, dataset: str) -> Path:
    filename = dataset_output_filename("main_report.pdf", dataset)
    return paths.root / "reports" / filename
