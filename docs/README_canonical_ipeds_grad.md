# Canonical IPEDS Graduation Rates

## Data Lineage and Inputs

- **Raw source folder:** `data/raw/ipeds/` (provider-scoped directory inside repo root).
- **Files in scope:**
  - `2023/grad_rates_2004_2023.csv` (DRV/DFR wide extract)
  - `2023/gradrates.csv` and `2023/pellgradrates.csv` (component + Pell subcohort detail)
  - `2023/institutions.csv` (HD metadata for control, level, sector, geography)
  - `2024/HD2024.csv` (latest HD release for governance cross-checks)
- **Extraction window:** Cohorts 2004–2023 (Winter 2023-24 collection cycle).
- **IPEDS components:** Graduation Rates (GR/GRS), Derived Graduation Rates (DRVGR/DFR), and Institutional Characteristics (HD).
- **Refresh cadence:** Annual (winter) after IPEDS releases provisional DRV files. Re-ingest occurs once per collection, with deltas documented in `out/canonical/ipeds_grad/run-<timestamp>.json`.

Future sections will capture transformation steps, validation checks, and release notes as subsequent phases complete.

## Metadata Enrichment (Phase 03)

- **HD join source:** `data/raw/ipeds/2023/institutions.csv` (fallback to newer HD files for governance spot checks).
- **Mapped fields:** `control` (Public / Private NP / Private FP), `level` (4-year / 2-year / <2-year), `state` (postal), and descriptive `sector` buckets (e.g., "Public, 4-year or above").
- **Implementation:** `python -m src.pipelines.canonical.ipeds_grad.enrich_metadata` reads the Phase 02 long parquet, attaches metadata, and overwrites `data/processed/2023/canonical/ipeds_grad_rates_long.parquet`.
- **Data quality:** One institution (Wesley College, UnitID 131098) lacked HD metadata; see `docs/ipeds_missing_metadata.md` for remediation notes.
- **Rate policy:** Detailed precedence rules for DRV vs DFR sources live in `docs/rate_policy_ipeds_grad.md`; the extractor encodes the source via the `source_flag` column.

## Canonical Outputs (Phase 05)

- `data/processed/2023/canonical/ipeds_grad_rates_latest_by_inst.parquet` — one row per institution with the most recent cohort year.
- `data/processed/2023/canonical/ipeds_grad_rates_summary_by_year.parquet` — aggregated statistics by year and sector (count, avg, median, quartiles).
- `out/canonical/ipeds_grad/run_latest.json` — provenance record with build timestamp, row counts, year span, and git SHA.
- Build command: `python -m src.pipelines.canonical.ipeds_grad.build_outputs` (requires Phase 02/03 inputs).

### Percent Pell Grants (SFA)

- Extraction: `python -m src.pipelines.canonical.ipeds_sfa.extraction` (configured for Pell via CLI `main`).
- Metadata enrichment: `python -m src.pipelines.canonical.ipeds_sfa.enrich_metadata`.
- Build outputs: `python -m src.pipelines.canonical.ipeds_sfa.build_outputs`.
- Resulting artifacts:
  - `data/processed/2023/canonical/ipeds_percent_pell_long.parquet`
  - `data/processed/2023/canonical/ipeds_percent_pell_latest_by_inst.parquet`
  - `data/processed/2023/canonical/ipeds_percent_pell_summary_by_year.parquet`
  - `out/canonical/ipeds_pell/run_latest.json`

## Reproduction Checklist

1. `python -m src.pipelines.canonical.ipeds_grad.extraction`
2. `python -m src.pipelines.canonical.ipeds_grad.enrich_metadata`
3. `python -m src.pipelines.canonical.ipeds_grad.build_outputs`

Each step overwrites the downstream artifacts and refreshes provenance in `out/canonical/ipeds_grad/`.

## Reviewer Guide

- Inspect the long-table schema in `docs/schema_canonical_ipeds_grad.md` and field-level dictionary in `docs/data_dictionary_ipeds_grad.md`.
- Confirm provenance JSON matches the commit under review (git SHA + row counts).
- For any null metadata rows, consult `docs/ipeds_missing_metadata.md`.
- Rate precedence rules are documented in `docs/rate_policy_ipeds_grad.md`; ensure `source_flag` and `is_revised` columns match expectations.

## Gentle App Integration (Phase 07)

- Feature flag: `USE_CANONICAL_GRAD_DATA` (default `true`). When enabled, College Explorer’s summary and graduation tabs display canonical 150% completion rates alongside existing Pell OM trends.
- Loader: `DataManager.canonical_grad_df` loads `data/processed/2023/canonical/ipeds_grad_rates_latest_by_inst.parquet` through `DataLoader.load_parquet`.
- UI hook: `CollegeExplorerSection` surfaces a “Canonical Pipeline Snapshot” card with the most recent cohort year, rate, and DRV/DFR provenance.
- Toggle off the flag to fall back to the legacy Outcome Measures-only experience without touching canonical files.
