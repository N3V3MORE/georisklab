# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.utils.config import get_project_paths  # noqa: E402

SAMPLE_SOURCE_DATE = "2026-06-15"
SAMPLE_TIMESTAMP_UTC = "2026-06-15T00:00:00+00:00"


def build_sample_monthly_data(root: Path | None = None) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()

    dates = pd.date_range("2000-01-01", "2024-12-01", freq="MS")
    step = np.arange(len(dates))
    gpr = 100 + 18 * np.sin(step / 9) + np.where((step % 53) == 0, 35, 0)
    gprt = gpr * 0.62
    gpra = gpr * 0.38
    gpr_change = pd.Series(gpr).diff()
    gpr_change_z = ((gpr_change - gpr_change.mean()) / gpr_change.std(ddof=0)).to_numpy()
    predictive_gpr_shock = pd.Series(gpr_change_z).shift(1).fillna(0.0).to_numpy()

    gpr_monthly = pd.DataFrame(
        {
            "date_month": dates,
            "gpr_global": gpr.round(4),
            "gprt_global": gprt.round(4),
            "gpra_global": gpra.round(4),
            "source_download_date": SAMPLE_SOURCE_DATE,
        }
    )

    markets = []
    for market_id, market_class, sensitivity in [
        ("developed", "developed", -0.15),
        ("emerging", "emerging", -0.34),
    ]:
        cycle = 1.2 * np.sin(step / 6 + (0.4 if market_id == "emerging" else 0))
        returns = 0.55 + cycle + sensitivity * predictive_gpr_shock
        for date, value in zip(dates, returns, strict=True):
            markets.append(
                {
                    "date_month": date,
                    "market_id": market_id,
                    "market_class": market_class,
                    "return_usd": round(float(value), 4),
                    "risk_free_rate": 0.15,
                    "excess_return": round(float(value - 0.15), 4),
                    "source": "deterministic_sample",
                    "source_download_date": SAMPLE_SOURCE_DATE,
                }
            )
    market_returns = pd.DataFrame(markets)

    gpr_change_z_for_events = np.nan_to_num(gpr_change_z, nan=0.0)
    conflict_count = (10 + np.maximum(gpr_change_z_for_events, 0) * 6).round().astype(int)
    protest_count = (8 + np.maximum(np.sin(step / 5), 0) * 4).round().astype(int)
    sanction_count = (3 + (step % 17 == 0) * 2).astype(int)
    diplomatic_conflict_count = (5 + np.maximum(gpr_change_z_for_events, 0) * 3).round().astype(int)
    gdelt = pd.DataFrame(
        {
            "date_month": dates,
            "country_iso3": "GLB",
            "event_count": (80 + 15 * np.sin(step / 8)).round().astype(int),
            "conflict_count": conflict_count,
            "protest_count": protest_count,
            "sanction_count": sanction_count,
            "diplomatic_conflict_count": diplomatic_conflict_count,
            "avg_goldstein": (-1.5 - np.maximum(gpr_change_z_for_events, 0)).round(4),
            "avg_tone": (-2.0 - np.maximum(gpr_change_z_for_events, 0) * 0.8).round(4),
            "risk_index_raw": np.log1p(
                conflict_count + protest_count + sanction_count + diplomatic_conflict_count
            ).round(4),
            "filter_version": "sample-v1",
            "source_download_date": SAMPLE_SOURCE_DATE,
        }
    )
    gdelt["risk_index_zscore"] = (
        (gdelt["risk_index_raw"] - gdelt["risk_index_raw"].mean())
        / gdelt["risk_index_raw"].std(ddof=0)
    ).round(4)

    macro = pd.DataFrame(
        {
            "date_month": dates,
            "country_iso3": "GLB",
            "indicator_code": "sample_global_cycle",
            "value": np.sin(step / 12).round(4),
            "frequency_original": "monthly",
            "frequency_converted": "monthly",
            "source": "deterministic_sample",
            "source_download_date": SAMPLE_SOURCE_DATE,
        }
    )

    outputs = {
        "sample_gpr_monthly.csv": gpr_monthly,
        "sample_market_returns_monthly.csv": market_returns,
        "sample_gdelt_country_monthly.csv": gdelt,
        "sample_macro_controls_monthly.csv": macro,
    }
    for filename, df in outputs.items():
        df.to_csv(paths.data_processed / filename, index=False)

    metadata = {
        "source_name": "GeoRiskLab deterministic sample",
        "source_url": "generated locally from scripts/build_monthly_data.py",
        "download_timestamp_utc": SAMPLE_TIMESTAMP_UTC,
        "license_or_terms_note": "Synthetic sample data. Not empirical market data.",
        "script_version": "sample-v1",
        "files": list(outputs),
    }
    (paths.data_metadata / "source_manifest.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build sample monthly GeoRiskLab data.")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    build_sample_monthly_data(root=Path(args.root) if args.root else None)


if __name__ == "__main__":
    main()
