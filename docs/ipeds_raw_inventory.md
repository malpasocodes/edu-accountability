# IPEDS Raw Inventory — Graduation Rates Inputs

| File | Description | Year Range | Approx. Rows | Key Columns | Notes |
|------|-------------|------------|--------------|-------------|-------|
| `data/raw/ipeds/2023/grad_rates_2004_2023.csv` | Derived graduation-rate wide table (DRV/DFR blend) | 2004–2023 | ~6,049 | `UnitID`, `Institution Name`, `Graduation rate total cohort (DRVGRYYYY/DFRYYYY)` | UTF-8 CSV, comma-delimited; contains `_RV` revised suffix fields for earlier years |
| `data/raw/ipeds/2023/gradrates.csv` | Core GR component snapshot with cohort counts and 6/4-year rates | 2015 cohort | ~6,049 | `UnitID`, `TOTAL_COHORT_2015`, `PCT_AWARD_6YRS`, `PCT_AWARD_4YEARS` | Standard UTF-8 CSV; limited year scope but authoritative for 2015 baseline |
| `data/raw/ipeds/2023/pellgradrates.csv` | Pell vs overall grad rates by cohort | 2016–2023 | ~6,049 | `UnitID`, `PGRYYYY`, `GRYYYY` | UTF-8 CSV; alternating Pell/general columns per year |
| `data/raw/ipeds/2023/institutions.csv` | Institutional characteristics (HD extract) | Point-in-time 2023 | ~6,049 | `UnitID`, `INSTITUTION`, `STATE`, `SECTOR`, `LEVEL`, `CONTROL` | UTF-8 CSV; used for metadata joins |
| `data/raw/ipeds/2024/HD2024.csv` | Latest HD file for governance cross-checks | 2024 collection | ~6,072 | `UNITID`, `INSTNM`, `SECTOR`, `ICLEVEL`, `CONTROL`, `STABBR` | UTF-8 with BOM; comma-delimited; keep BOM handling in mind during ingestion |

Row counts were derived via `wc -l` (subtracting the header row). All files reside under the `data/raw/ipeds/` provider folder to preserve the repository’s data-first convention.
