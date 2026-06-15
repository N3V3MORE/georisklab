import pandas as pd
import pytest

from georisklab.utils.config import ProjectPaths
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
