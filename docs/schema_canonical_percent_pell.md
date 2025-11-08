# Canonical Schema — IPEDS Percent Pell Grants

## Overview
This dataset transforms the IPEDS SFA component (percentage of undergraduate students awarded Pell grants) from wide annual columns into a normalized long table covering cohorts 2008-09 through 2022-23. It mirrors the graduation-rate pipeline structure so downstream charts can mix-and-match canonical datasets.

## Table Definition

| Column | Type | Description |
|--------|------|-------------|
| `unitid` | int64 | IPEDS institution identifier. |
| `year` | int16 | Aid year inferred from the source column (e.g., `2023` from `SFA2223`). |
| `instnm` | string | Institution name as supplied in the source file. |
| `control` | category {Public, Private NP, Private FP} | Filled during metadata enrichment. |
| `level` | category {4-year, 2-year, <2-year} | Filled during metadata enrichment. |
| `state` | string | Two-letter postal abbreviation. |
| `sector` | category | Descriptive IPEDS sector bucket. |
| `percent_pell` | float32 | Percentage (0–100) of undergraduates awarded Pell grants. |
| `source_flag` | string {SFA} | Component identifier (future-proofing if additional components join). |
| `is_revised` | bool | Indicates `_RV` columns. |
| `cohort_reference` | string | Human-friendly label (`"2022-23 Pell"`). |
| `load_ts` | datetime64[ns] | Ingestion timestamp. |

## Rules & Validation

- Precedence: `_RV` columns supersede non-revised siblings for the same year, analogous to DL-004.
- Value bounds: `0 ≤ percent_pell ≤ 100`; nulls stay null with warnings captured in validation tests.
- Uniqueness: (`unitid`, `year`) unique once revisions collapse.
- Metadata enrichment replicates the grad pipeline (Phase 03) so canonical charts share dimensions.

## Outputs

- Long table: `data/processed/2023/canonical/ipeds_percent_pell_long.parquet`
- Latest by institution: `.../ipeds_percent_pell_latest_by_inst.parquet`
- Summary by year/sector: `.../ipeds_percent_pell_summary_by_year.parquet`
- Provenance: `out/canonical/ipeds_pell/run-<timestamp>.json`

## Notes
- Raw source: `data/raw/ipeds/percent_pell_grants.csv`
- First phase focuses on Pell; percent-loan pipeline will reuse the same module with a different column prefix.
