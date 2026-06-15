# Data Sources and Licensing Notes

This project should be built from public or openly accessible data sources. Public access does not automatically mean public domain. The repo should store download scripts, metadata, checksums, and small samples, not raw third-party market data unless the source terms allow redistribution.

## Core data sources

### GDELT

Use case:

- Country-month geopolitical event intensity.
- Event category counts.
- Severity weighting using event category, Goldstein score, and tone where available.

Relevant pages:

- https://www.gdeltproject.org/
- https://www.gdeltproject.org/data.html
- https://data.gdeltproject.org/documentation/

Design note:

GDELT is a media/event-coding dataset, not a clean ground-truth conflict dataset. Treat it as a noisy proxy. Document every filter used.

### Caldara-Iacoviello GPR index

Use case:

- Benchmark geopolitical risk measure.
- Threats versus acts decomposition.
- Country-specific GPR where available.

Relevant pages:

- https://www.policyuncertainty.com/gpr.html
- https://www.matteoiacoviello.com/gpr.htm
- AER article: https://www.aeaweb.org/articles?id=10.1257/aer.20191823

Design note:

The GPR index should be the benchmark measure. The GDELT index should be presented as an extension, not a replacement.

Implementation note:

`load_caldara_iacoviello_gpr` documents the real-source mapping used by fixtures:

```text
month -> date_month
GPR   -> gpr_global
GPRT  -> gprt_global
GPRA  -> gpra_global
```

Raw downloaded files should stay out of git. Commit tiny fixtures and metadata only.

### Economic Policy Uncertainty

Use case:

- Control for broader policy uncertainty.
- Distinguish geopolitical risk from domestic policy uncertainty.

Relevant page:

- https://www.policyuncertainty.com/

### Kenneth French Data Library

Use case:

- Developed and emerging market factor returns.
- Developed versus emerging aggregate return benchmarks.

Relevant page:

- https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

Design note:

Use factor or portfolio returns for the first version because they are clean and easier to cite than ad hoc ETF returns.

Implementation note:

Fama-French monthly factor files report `Mkt-RF` as an excess return and `RF` as
the risk-free rate. The project normalises them as monthly percent values:

```text
excess_return = Mkt-RF
risk_free_rate = RF
return_usd = excess_return + risk_free_rate
```

Use developed and emerging files from the Kenneth French Data Library for the
first empirical aggregate benchmark. The parser is fixture-tested with local
zip files so CI does not depend on live downloads.

### FRED

Use case:

- Macro-financial controls.
- US/global rates, oil proxies, dollar proxies, industrial activity where relevant.

Relevant pages:

- https://fred.stlouisfed.org/docs/api/fred/
- https://fred.stlouisfed.org/docs/api/api_key.html

Design note:

FRED API access requires an API key. The key is not a paid data vendor, but it is still a credential. The repo should use an environment variable, never hard-code keys.

### World Bank Indicators API

Use case:

- Country-level macro vulnerability variables.
- GDP, inflation, current account, external debt, reserves, income classification.

Relevant pages:

- https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
- https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures

Design note:

The World Bank Indicators API does not require API keys. Use it for country-level macro controls.

### IMF Data APIs

Use case:

- Macro series where World Bank coverage is insufficient.
- International Financial Statistics and other datasets where relevant.

Relevant page:

- https://data.imf.org/en/Resource-Pages/IMF-API

Design note:

IMF APIs use SDMX. This is more annoying than CSV but worth learning for an economics profile.

## Optional market data

Daily prices are useful for event studies but create licensing and survivorship issues. If using a public website for daily prices, do not redistribute raw data. If you buy a clean academic or vendor dataset, document the terms and keep it out of the public repo.

## Source metadata standard

Every ingestion script should write metadata:

```json
{
  "source_name": "Caldara-Iacoviello GPR",
  "source_url": "...",
  "download_timestamp_utc": "...",
  "file_hash_sha256": "...",
  "raw_file_path": "data/raw/...",
  "license_or_terms_note": "...",
  "script_version": "..."
}
```

## Data quality checks

Each source must pass:

1. Date range check.
2. Missingness check.
3. Duplicate key check.
4. Frequency check.
5. Unit check.
6. Source metadata check.
7. Known-crisis sanity check where applicable.

## Do not commit

```text
data/raw/
data/interim/
large parquet extracts
paid market data
API keys
credentials
```

## Safe to commit

```text
source metadata
schema files
tiny toy data samples
scripts
figures
tables
derived summary statistics if allowed
```
