# Canonical Schema — IPEDS Graduation Rates (Long Format)

## Overview
The canonical pipeline will emit a long-format Parquet table that harmonizes DRV/DFR graduation rates with institutional metadata for cohorts 2004–2023. Each row represents a single institution × year × cohort definition at the 150% completion window.

## Table Definition

| Column | Type | Description |
|--------|------|-------------|
| `unitid` | int64 | IPEDS institution identifier (primary key component). |
| `year` | int16 | Cohort reference year (e.g., `2023` for DRVGR2023). |
| `instnm` | string | Institution name sourced from IPEDS HD. |
| `control` | category {`Public`, `Private NP`, `Private FP`} | Institution control. |
| `level` | category {`4-year`, `2-year`, `<2-year`} | Highest degree level offered. |
| `state` | string (2-letter) | Mailing state/territory abbreviation. |
| `sector` | category | IPEDS sector (1–9) mapped to descriptive bucket. |
| `grad_rate_150` | float32 | Graduation rate (%) at 150% of normal time. Stored as 0–100. |
| `source_flag` | string {`DRV`, `DFR`} | Indicates whether the value originated from the Derived (DRV) or provisional (DFR) file. |
| `is_revised` | bool | `True` when the original column had `_RV` suffix, signaling a revision. |
| `cohort_reference` | string | Human-friendly description (`"2017 cohort, four-year"`). |
| `load_ts` | datetime64[ns] | UTC timestamp captured when the canonical pipeline ingests the row. |

## Field Rules & Validation

- **Uniqueness:** (`unitid`, `year`, `cohort_reference`, `source_flag`) must be unique after normalization.
- **Completeness:** Drop rows missing `unitid` or `year`; null rates remain but are flagged via `source_flag`.
- **Value bounds:** `0 ≤ grad_rate_150 ≤ 100`; reject (or log) out-of-range values.
- **Categorical hygiene:** `control`, `level`, and `sector` are canonicalized enums with definitions documented in `docs/data_dictionary_ipeds_grad.md` (Phase 06).
- **Timestamps:** `load_ts` captured once per run; downstream consumers use it for freshness checks.

## Downstream Outputs

- Primary table stored at `data/processed/<year>/canonical/ipeds_grad_rates_long.parquet`.
- Aggregated variants (latest-by-institution, national summaries) inherit the same column definitions for overlapping fields.
