# ruff: noqa: E402, I001
from __future__ import annotations

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.econometrics.local_projection import run_local_projections  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402


def run_regressions() -> None:
    paths = get_project_paths()
    paths.ensure_output_dirs()
    panel = pd.read_csv(
        paths.data_processed / "sample_analysis_panel.csv",
        parse_dates=["date_month"],
    )

    results = run_local_projections(
        panel,
        horizons=[1, 3, 6],
        config={"shock_col": "gpr_global_z", "controls": ["sample_global_cycle"]},
    )
    results.round(6).to_csv(paths.reports_tables / "table_02_baseline_regressions.csv", index=False)


def main() -> None:
    run_regressions()


if __name__ == "__main__":
    main()
