# Canonical Schema — IPEDS Percent Federal Loans

## Overview
Transforms the IPEDS SFA percent-of-undergraduates-with-federal-loans table into long format (2008-09 through 2022-23), mirroring the Pell pipeline so canonical charts can compare aid uptake alongside graduation metrics.

## Table Definition

| Column | Type | Description |
|--------|------|-------------|
| `unitid` | int64 | IPEDS UnitID. |
| `year` | int16 | Aid year (e.g., `2023` from SFA2223). |
| `instnm` | string | Institution name from the SFA file. |
| `control` | category | Filled via Phase 03 metadata enrichment. |
| `level` | category | Filled via Phase 03. |
| `state` | string | Two-letter postal abbreviation. |
| `sector` | category | IPEDS sector bucket. |
| `percent_loans` | float32 | Percent (0–100) of undergraduates receiving federal loans. |
| `source_flag` | string {SFA} | Component/tag. |
| `is_revised` | bool | Indicates `_RV` columns. |
| `cohort_reference` | string | e.g., `"2022-23 Loans"`. |
| `load_ts` | datetime64[ns] | UTC timestamp during ingestion. |

## Rules
- `_RV` columns supersede non-revised siblings (same logic as DL-004/DL-006).
- Value bounds: `0 ≤ percent_loans ≤ 100`.
- Unique `unitid + year` once revisions collapse.
- Metadata enrichment reuses `src/pipelines/canonical/ipeds_sfa/enrich_metadata.py`.

## Outputs
- Long: `data/processed/2023/canonical/ipeds_percent_loans_long.parquet`
- Latest: `data/processed/2023/canonical/ipeds_percent_loans_latest_by_inst.parquet`
- Summary: `data/processed/2023/canonical/ipeds_percent_loans_summary_by_year.parquet`
- Metadata: `out/canonical/ipeds_loans/run-<timestamp>.json`

## Source
- `data/raw/ipeds/percent_federal_loans.csv`
