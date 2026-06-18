import pandas as pd
import pytest

from georisklab.utils.config import ProjectPaths
from georisklab.utils.datasets import dataset_files, dataset_output_filename
from georisklab.utils.validation import ensure_columns, standardize_month_start


def test_project_paths_use_supplied_root(tmp_path):
    paths = ProjectPaths(tmp_path)

    assert paths.data_processed == tmp_path / "data" / "processed"
    assert paths.reports_tables == tmp_path / "reports" / "tables"


def test_ensure_columns_reports_missing_names():
    df = pd.DataFrame({"date_month": ["2020-01-01"]})

    with pytest.raises(ValueError, match="missing required columns: value"):
        ensure_columns(df, ["date_month", "value"])


def test_standardize_month_start_uses_first_day_of_month():
    series = pd.Series(["2020-01-31", "2020-02-15"])

    result = standardize_month_start(series)

    assert result.tolist() == [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-02-01")]


def test_dataset_files_name_sample_and_real_inputs():
    sample = dataset_files("sample")
    real = dataset_files("real")

    assert sample.analysis_panel == "sample_analysis_panel.csv"
    assert sample.source_manifest == "source_manifest.json"
    assert sample.analysis_manifest == "analysis_panel_manifest.json"
    assert real.analysis_panel == "analysis_panel.csv"
    assert real.source_manifest == "source_manifest_real.json"
    assert real.analysis_manifest == "analysis_panel_manifest_real.json"


def test_dataset_output_filename_keeps_sample_and_suffixes_real():
    assert dataset_output_filename("table_01_summary_stats.csv", "sample") == (
        "table_01_summary_stats.csv"
    )
    assert dataset_output_filename("table_01_summary_stats.csv", "real") == (
        "table_01_summary_stats_real.csv"
    )


def test_dataset_helpers_reject_unknown_dataset():
    with pytest.raises(ValueError, match="dataset must be 'sample' or 'real'"):
        dataset_files("demo")
