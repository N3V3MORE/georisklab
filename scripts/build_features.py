# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

from _bootstrap import add_project_root

add_project_root()

from georisklab.features.panel import build_analysis_panel  # noqa: E402
from georisklab.utils.config import get_project_paths  # noqa: E402
from georisklab.utils.outputs import table_path  # noqa: E402


def build_features(dataset: str = "sample", root: Path | None = None) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    files = _dataset_files(dataset)
    input_paths = {
        key: paths.data_processed / files[key]
        for key in ["market_returns", "gpr", "gdelt", "macro"]
    }

    market_returns = pd.read_csv(
        input_paths["market_returns"],
        parse_dates=["date_month"],
    )
    gpr = pd.read_csv(input_paths["gpr"], parse_dates=["date_month"])
    common_sample = None
    if dataset == "real":
        market_returns, gpr, common_sample = _align_real_common_sample(market_returns, gpr)
    gdelt, used_placeholder_gdelt = _read_optional_gdelt(input_paths["gdelt"], gpr)
    macro, used_placeholder_macro = _read_optional_macro(input_paths["macro"], gpr)
    _warn_on_placeholder_inputs(
        dataset,
        used_placeholder_gdelt=used_placeholder_gdelt,
        used_placeholder_macro=used_placeholder_macro,
    )

    panel = build_analysis_panel(market_returns, gpr, gdelt, macro)
    output_path = paths.data_processed / files["analysis_panel"]
    panel.to_csv(output_path, index=False)
    _write_analysis_panel_manifest(
        paths.data_metadata / _analysis_panel_manifest_name(dataset),
        dataset=dataset,
        panel=panel,
        input_paths=input_paths,
        output_path=output_path,
        used_placeholder_gdelt=used_placeholder_gdelt,
        used_placeholder_macro=used_placeholder_macro,
        common_sample=common_sample,
    )

    summary = (
        panel.groupby("market_class", as_index=False)
        .agg(
            observations=("excess_return", "count"),
            mean_excess_return=("excess_return", "mean"),
            mean_next_month_return=("ret_fwd_1m", "mean"),
            negative_next_month_share=("neg_ret_1m", "mean"),
        )
        .round(4)
    )
    summary.to_csv(table_path(paths, "table_01_summary_stats.csv", dataset), index=False)


def _dataset_files(dataset: str) -> dict[str, str]:
    if dataset == "sample":
        return {
            "gpr": "sample_gpr_monthly.csv",
            "market_returns": "sample_market_returns_monthly.csv",
            "gdelt": "sample_gdelt_country_monthly.csv",
            "macro": "sample_macro_controls_monthly.csv",
            "analysis_panel": "sample_analysis_panel.csv",
        }
    if dataset == "real":
        return {
            "gpr": "gpr_monthly.csv",
            "market_returns": "market_returns_monthly.csv",
            "gdelt": "gdelt_country_monthly.csv",
            "macro": "macro_controls_monthly.csv",
            "analysis_panel": "analysis_panel.csv",
        }
    raise ValueError("dataset must be 'sample' or 'real'")


def _read_optional_gdelt(path, gpr: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    if path.exists():
        return pd.read_csv(path, parse_dates=["date_month"]), False
    return (
        pd.DataFrame(
            {
                "date_month": gpr["date_month"],
                "country_iso3": "GLB",
                "risk_index_raw": 0.0,
                "risk_index_zscore": 0.0,
            }
        ),
        True,
    )


def _read_optional_macro(path, gpr: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    if path.exists():
        return pd.read_csv(path, parse_dates=["date_month"]), False
    return (
        pd.DataFrame(
            {
                "date_month": gpr["date_month"],
                "country_iso3": "GLB",
                "indicator_code": "placeholder_macro_zero",
                "value": 0.0,
                "frequency_original": "not_available",
                "frequency_converted": "monthly",
                "source": "real_pipeline_placeholder",
                "source_download_date": "",
            }
        ),
        True,
    )


def _warn_on_placeholder_inputs(
    dataset: str,
    *,
    used_placeholder_gdelt: bool,
    used_placeholder_macro: bool,
) -> None:
    if dataset != "real":
        return
    warnings = []
    if used_placeholder_gdelt:
        warnings.append("GDELT")
    if used_placeholder_macro:
        warnings.append("macro")
    if not warnings:
        return
    joined = " and ".join(warnings)
    print(
        "WARNING: using placeholder "
        f"{joined} inputs for the real feature build. These series are staged and excluded "
        "from real empirical claims until real source files are supplied.",
        file=sys.stderr,
    )


def _align_real_common_sample(
    market_returns: pd.DataFrame,
    gpr: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DatetimeIndex]:
    return_dates = pd.DatetimeIndex(
        pd.to_datetime(market_returns["date_month"]).unique()
    ).sort_values()
    gpr_dates = pd.DatetimeIndex(pd.to_datetime(gpr["date_month"]).unique()).sort_values()
    common_dates = return_dates.intersection(gpr_dates).sort_values()
    if common_dates.empty:
        raise ValueError("real feature build requires at least one common GPR and return month")

    return (
        market_returns[market_returns["date_month"].isin(common_dates)].reset_index(drop=True),
        gpr[gpr["date_month"].isin(common_dates)].reset_index(drop=True),
        common_dates,
    )


def _analysis_panel_manifest_name(dataset: str) -> str:
    if dataset == "sample":
        return "analysis_panel_manifest.json"
    return "analysis_panel_manifest_real.json"


def _write_analysis_panel_manifest(
    path: Path,
    *,
    dataset: str,
    panel: pd.DataFrame,
    input_paths: dict[str, Path],
    output_path: Path,
    used_placeholder_gdelt: bool,
    used_placeholder_macro: bool,
    common_sample: pd.DatetimeIndex | None,
) -> None:
    panel_dates = pd.to_datetime(panel["date_month"]).drop_duplicates().sort_values()
    manifest = {
        "dataset": dataset,
        "sample_start": _date_text(panel_dates.min()),
        "sample_end": _date_text(panel_dates.max()),
        "n_months": int(len(panel_dates)),
        "used_placeholder_gdelt": used_placeholder_gdelt,
        "used_placeholder_macro": used_placeholder_macro,
        "processed_input_hashes": {
            key: _file_sha256(path) for key, path in input_paths.items() if path.exists()
        },
        "analysis_panel_hash_sha256": _file_sha256(output_path),
    }
    if common_sample is not None and len(common_sample) > 0:
        manifest["aligned_to_common_gpr_returns_sample"] = True
        manifest["common_sample_start"] = _date_text(common_sample.min())
        manifest["common_sample_end"] = _date_text(common_sample.max())
        manifest["common_sample_n_months"] = int(len(common_sample))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _date_text(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).date().isoformat()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GeoRiskLab features.")
    parser.add_argument("--dataset", choices=["sample", "real"], default="sample")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    build_features(
        dataset=args.dataset,
        root=Path(args.root) if args.root else None,
    )


if __name__ == "__main__":
    main()
