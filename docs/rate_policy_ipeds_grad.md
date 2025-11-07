# IPEDS Graduation Rate Policy (Canonical Pipeline)

## Overview
The canonical pipeline combines Derived (DRVGR) and provisional (DFR) graduation-rate tables delivered in the IPEDS Winter 2023-24 collection. This document records the precedence rules and governance decisions that determine which source feeds the `grad_rate_150` field and how revisions are handled.

## Source Precedence

1. **DRVGR columns (preferred)**
   - Use `DRVGRYYYY` values for all cohorts where IPEDS ships a derived column.
   - If a `_RV` suffix exists (e.g., `DRVGR2018_RV`), the revised column supersedes the original. The canonical extractor stores this fact via `is_revised = True`.
2. **DFR fallback**
   - When a year lacks a DRV column (e.g., earliest cohorts 2004–2005), fall back to the matching `DFRYYYY` column.
   - Revised provisional columns (`DFRYYYY_RV`) take precedence over unrevised ones.
3. **Explicit provenance**
   - Every melted row captures `source_flag` (`DRVGR` or `DFR`) so downstream dashboards can expose the origin or filter to “official only.”

## Revision Handling

- `_RV` columns always replace non-`_RV` siblings for the same cohort.
- The pipeline retains both versions in the raw melt but filters the canonical output to the latest column per cohort, preventing duplicate `unitid × year` records.
- `is_revised` stays `True` when the final value descended from an `_RV` column; analysts can audit how many institutions benefited from revisions.

## Missing Data / Special Cases

- If both DRV and DFR values are null for a cohort, the canonical table preserves the null and flags it during validations rather than fabricating a value.
- Institutions missing HD metadata (currently only Wesley College, UnitID 131098) keep nulls in control/level/state/sector but still follow the same rate precedence rules.

## Implementation Notes

- Extraction logic lives in `src/pipelines/canonical/ipeds_grad/extraction.py` and enforces the above precedence automatically.
- Future phases (e.g., comparisons vs legacy dashboards) should link back to this policy to explain any discrepancies between historical and canonical numbers.

## Review & Updates

- Policy last reviewed: 2025-11-07 during Phase 04.
- Updates require a new decision-log entry (DL-00X) and a rerun of the extraction pipeline with `source_flag` checks added to regression tests.
