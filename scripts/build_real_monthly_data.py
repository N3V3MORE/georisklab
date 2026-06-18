# ruff: noqa: E402, I001
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pandas as pd
import yaml

from _bootstrap import add_project_root

add_project_root()

from georisklab.ingest.gpr import load_caldara_iacoviello_gpr  # noqa: E402
from georisklab.ingest.market_returns import load_fama_french_factor_returns  # noqa: E402
from georisklab.ingest.source_metadata import (  # noqa: E402
    write_source_collection_manifest,
    write_source_manifest,
)
from georisklab.utils.config import get_project_paths  # noqa: E402

SCRIPT_VERSION = "real-monthly-v1"
MAX_URL_SOURCE_BYTES = 100 * 1024 * 1024


def build_real_monthly_data(config_path: Path, root: Path | None = None) -> None:
    paths = get_project_paths(root)
    paths.ensure_output_dirs()
    config = _load_config(config_path)
    period = config.get("sample_period", {})
    source_download_date = pd.Timestamp.today(tz="UTC").date().isoformat()
    download_dir = paths.data_raw / "_downloads"

    if config["gpr"].get("loader") != "caldara_iacoviello":
        raise ValueError("gpr.loader must be 'caldara_iacoviello'")

    gpr_source = _resolve_source(
        config["gpr"]["path_or_url"],
        paths.root,
        expected_sha256=config["gpr"].get("sha256"),
        download_dir=download_dir,
    )
    gpr = load_caldara_iacoviello_gpr(str(gpr_source))
    gpr = _filter_period(gpr, period)
    gpr["source_download_date"] = source_download_date
    gpr.to_csv(paths.data_processed / "gpr_monthly.csv", index=False)
    gpr_manifest = _write_manifest(
        paths.data_metadata / "gpr_manifest.json",
        source_name="Caldara-Iacoviello GPR",
        source_url=_redact_source_url(str(config["gpr"]["path_or_url"])),
        raw_file_path=str(gpr_source),
        license_or_terms_note="Public benchmark index. Do not redistribute raw source files.",
    )

    ff_config = config["fama_french"]
    developed_source = _resolve_source(
        ff_config["developed_zip"],
        paths.root,
        expected_sha256=ff_config.get("developed_sha256"),
        download_dir=download_dir,
    )
    emerging_source = _resolve_source(
        ff_config["emerging_zip"],
        paths.root,
        expected_sha256=ff_config.get("emerging_sha256"),
        download_dir=download_dir,
    )
    developed = load_fama_french_factor_returns(
        str(developed_source),
        market_id="developed",
        market_class="developed",
    )
    emerging = load_fama_french_factor_returns(
        str(emerging_source),
        market_id="emerging",
        market_class="emerging",
    )
    returns = _filter_period(pd.concat([developed, emerging], ignore_index=True), period)
    returns["source_download_date"] = source_download_date
    _validate_spread_market_coverage(returns)
    returns.to_csv(paths.data_processed / "market_returns_monthly.csv", index=False)

    spread = (
        returns.pivot_table(index="date_month", columns="market_id", values="excess_return")
        .assign(spread_em_dev=lambda df: df["emerging"] - df["developed"])
        [["spread_em_dev"]]
        .reset_index()
    )
    spread["spread_em_dev"] = spread["spread_em_dev"].round(10)
    spread.to_csv(paths.data_processed / "market_spread_monthly.csv", index=False)

    developed_manifest = _write_manifest(
        paths.data_metadata / "fama_french_developed_manifest.json",
        source_name="Kenneth French Developed Factors",
        source_url=_redact_source_url(str(ff_config["developed_zip"])),
        raw_file_path=str(developed_source),
        license_or_terms_note=(
            "Kenneth French data library file. Do not redistribute raw source files."
        ),
    )
    emerging_manifest = _write_manifest(
        paths.data_metadata / "fama_french_emerging_manifest.json",
        source_name="Kenneth French Emerging Factors",
        source_url=_redact_source_url(str(ff_config["emerging_zip"])),
        raw_file_path=str(emerging_source),
        license_or_terms_note=(
            "Kenneth French data library file. Do not redistribute raw source files."
        ),
    )
    write_source_collection_manifest(
        paths.data_metadata / "source_manifest_real.json",
        [gpr_manifest, developed_manifest, emerging_manifest],
    )


def _write_manifest(
    path: Path,
    source_name: str,
    source_url: str,
    raw_file_path: str,
    license_or_terms_note: str,
) -> dict:
    return write_source_manifest(
        path,
        source_name=source_name,
        source_url=source_url,
        raw_file_path=raw_file_path,
        license_or_terms_note=license_or_terms_note,
        script_version=SCRIPT_VERSION,
    )


def _load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict):
        raise ValueError("source config must be a mapping")
    return config


def _redact_source_url(value: str) -> str:
    if "://" not in value:
        return value
    parsed = urlparse(value)
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunparse((parsed.scheme, host, parsed.path, "", "", ""))


def _resolve_source(
    path_or_url: str,
    root: Path,
    *,
    expected_sha256: str | None = None,
    download_dir: Path | None = None,
) -> Path:
    if "://" in path_or_url:
        scheme = urlparse(path_or_url).scheme.lower()
        if scheme != "https":
            raise ValueError(f"unsupported source URL scheme: {scheme}")
        if not expected_sha256:
            raise ValueError("HTTPS real-data sources must include an expected SHA-256 hash")
        return _download_url_source(
            path_or_url,
            download_dir or root / "data" / "raw" / "_downloads",
            expected_sha256,
        )
    path = Path(path_or_url)
    resolved = path if path.is_absolute() else root / path
    if expected_sha256 and _file_sha256(resolved).lower() != expected_sha256.lower():
        raise ValueError("real-data local source SHA-256 does not match the source config")
    return resolved


def _download_url_source(url: str, download_dir: Path, expected_sha256: str) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    chunks = []
    total = 0
    with pd.io.common.get_handle(url, mode="rb", is_text=False) as handle:
        while True:
            chunk = handle.handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_URL_SOURCE_BYTES:
                raise ValueError("real-data URL source is too large")
            digest.update(chunk)
            chunks.append(chunk)

    actual_sha256 = digest.hexdigest()
    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError("real-data URL source SHA-256 does not match the source config")

    source_name = Path(urlparse(url).path).name or "source.bin"
    output_path = download_dir / f"{actual_sha256[:12]}_{source_name}"
    output_path.write_bytes(b"".join(chunks))
    return output_path


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _filter_period(df: pd.DataFrame, period: dict) -> pd.DataFrame:
    result = df.copy()
    if period.get("start"):
        result = result[result["date_month"] >= pd.Timestamp(period["start"])]
    if period.get("end"):
        result = result[result["date_month"] <= pd.Timestamp(period["end"])]
    return result.reset_index(drop=True)


def _validate_spread_market_coverage(returns: pd.DataFrame) -> None:
    required_markets = ["developed", "emerging"]
    coverage = (
        returns.assign(_present=1)
        .pivot_table(
            index="date_month",
            columns="market_id",
            values="_present",
            aggfunc="max",
        )
        .reindex(columns=required_markets)
    )
    incomplete_months = coverage.isna().any(axis=1)
    if coverage.empty or incomplete_months.any():
        missing_months = [
            pd.Timestamp(date_month).strftime("%Y-%m-%d")
            for date_month in coverage.index[incomplete_months]
        ]
        detail = f" Incomplete months: {', '.join(missing_months[:5])}." if missing_months else ""
        raise ValueError(
            "filtered real returns must contain both developed and emerging markets "
            f"for every retained month.{detail}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build real monthly GPR and return data.")
    parser.add_argument("--config", default="config/sources.yml")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    build_real_monthly_data(
        config_path=Path(args.config),
        root=Path(args.root) if args.root else None,
    )


if __name__ == "__main__":
    main()
