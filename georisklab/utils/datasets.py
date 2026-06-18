from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetFiles:
    gpr: str
    market_returns: str
    gdelt: str
    macro: str
    analysis_panel: str
    source_manifest: str
    analysis_manifest: str


SAMPLE_FILES = DatasetFiles(
    gpr="sample_gpr_monthly.csv",
    market_returns="sample_market_returns_monthly.csv",
    gdelt="sample_gdelt_country_monthly.csv",
    macro="sample_macro_controls_monthly.csv",
    analysis_panel="sample_analysis_panel.csv",
    source_manifest="source_manifest.json",
    analysis_manifest="analysis_panel_manifest.json",
)

REAL_FILES = DatasetFiles(
    gpr="gpr_monthly.csv",
    market_returns="market_returns_monthly.csv",
    gdelt="gdelt_country_monthly.csv",
    macro="macro_controls_monthly.csv",
    analysis_panel="analysis_panel.csv",
    source_manifest="source_manifest_real.json",
    analysis_manifest="analysis_panel_manifest_real.json",
)


def dataset_files(dataset: str) -> DatasetFiles:
    if dataset == "sample":
        return SAMPLE_FILES
    if dataset == "real":
        return REAL_FILES
    raise ValueError("dataset must be 'sample' or 'real'")


def dataset_output_filename(filename: str, dataset: str) -> str:
    if dataset == "sample":
        return filename
    if dataset == "real":
        path = Path(filename)
        return f"{path.stem}_real{path.suffix}"
    raise ValueError("dataset must be 'sample' or 'real'")
