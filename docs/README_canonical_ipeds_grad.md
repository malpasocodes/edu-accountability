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
