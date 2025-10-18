# Data Provenance Summary

This note captures where core dashboard views source their data, the definitions applied to key metrics, and any timing nuances uncovered so far. It supplements the existing data dictionary files and should be kept current as new sections or datasets are added.

---

## College Value Grid

**Purpose:** Scatter plot comparing institutional graduation rates against published in-state tuition; supports four-year and two-year views.

### Source Files

| Input | Dataset | IPEDS survey | Collection year | Key fields used |
| ----- | ------- | ------------ | ---------------- | ---------------- |
| `data/raw/ipeds/2023/cost.csv` | Tuition & fees | IC2023_AY | 2023-24 AY | `UnitID`, `TUITION_FEES_INSTATE2023` |
| `data/raw/ipeds/2023/gradrates.csv` | Graduation rates | GR2023 | 2015 entering cohort measured at 150% of normal time | `UnitID`, `PCT_AWARD_6YRS` |
| `data/raw/ipeds/2023/enrollment.csv` | Enrollment | EF2023A | Fall 2023 | `UnitID`, `ENR_UGD` |
| `data/raw/ipeds/2023/institutions.csv` | Institution metadata | HD2023 | Fall 2023 | `UnitID`, `INSTITUTION`, `STATE`, `SECTOR`, `LEVEL`, `CATEGORY` |

### Pipeline

1. `src/data/build_tuition_vs_graduation.py` joins the four raw IPEDS extracts on `UnitID`.
2. Two outputs are produced:
   - `data/processed/tuition_vs_graduation.csv` for four-year sectors (IPEDS sectors 1–3).
   - `data/processed/tuition_vs_graduation_two_year.csv` for two-year sectors (sectors 4–6).
3. `src/data/datasets.py` normalizes these CSVs (dtype coercion, category mapping) and materializes Parquet companions with Snappy compression.
4. `DataManager._load_value_grid_datasets()` caches the processed frames and surfaces them to the Value Grid section.

### Metric Definitions

- **Cost** – Published in-state tuition plus required fees for the 2023-24 academic year (`IC2023_AY` → `TUITION_FEES_INSTATE2023`). No inflation adjustment or averaging is applied; numbers are nominal 2023-24 USD.
- **Graduation rate** – IPEDS Graduation Rates (GR) survey measure for students entering in 2015, completing within 150% of the program length. For community colleges this is three years; for bachelor’s institutions it is six years. The field used is `PCT_AWARD_6YRS`.
- **Enrollment** – Undergraduate headcount from Fall 2023 (`ENR_UGD`), used for bubble sizing and minimum enrollment filtering.
- **Sector** – Derived from IPEDS `SECTOR` codes (1–6) mapped to readable labels.

### Visual Annotations

- Chart x-axis label specifies “Cost (In-State Tuition, 2023-24 USD)”.
- Caption highlights the IPEDS IC2023_AY and GR2023 sources, noting the cohort definition.

---

## College Explorer – Summary & Graduation Rates Tabs

**Purpose:** Institution-level profile including location, sector, enrollment snapshots, and graduation outcomes with Pell comparisons.

### Source Files

| Input | Dataset | IPEDS survey | Coverage | Key fields |
| ----- | ------- | ------------ | -------- | ---------- |
| `data/raw/ipeds/2023/institutions.csv` | Institutional characteristics | HD2023 | Fall 2023 | `UnitID`, `INSTITUTION`, `CITY`, `STATE`, `ZIP`, `SECTOR` |
| `data/raw/ipeds/2023/distanced.csv` | Distance education enrollment | DE | 2020–2024 | `UnitID`, `TOTAL_ENROLL_2024`, `DE_ENROLL_2024`, `SDE_ENROLL_TOTAL`, historical year columns |
| `data/raw/ipeds/2023/pellgradrates.csv` | Outcome Measures with Pell detail | Outcome Measures/Customized CSV pull | Cohorts entering 2015 (reported through 2023) | `UnitID`, `GR2023`, `PGR2023`, … `GR2016`, `PGR2016` |

### Data Flow

1. `DataManager._load_institutions_raw()` ingests the HD2023 extract.
2. `DataManager._load_distance_raw()` loads the distance education table (optional; falls back to empty if missing).
3. `DataManager._load_pellgradrates_raw()` ingests `pellgradrates.csv` for Outcome Measures reporting.
4. `CollegeExplorerSection` holds references to these DataFrames and merges them in the Summary tab when an institution is selected.

### Metric Definitions

- **Enrollment metrics** – Pulled from the 2024 columns in `distanced.csv`. If a value is missing, the UI shows “N/A”. Metrics represent the latest Fall headcount for total enrollment, exclusively online enrollment, and students taking some distance education.
- **Overall Graduation Rate** – Derived from `GR2023` (or earlier year if needed) in `pellgradrates.csv`. This is the Outcome Measures statistic: all entering students (full-time, part-time, Pell, non-Pell) completing any credential within eight years of entry. The 2023 value reflects students who started in 2015.
- **Pell Graduation Rate** – `PGR2023` (and historical peers) capturing the same eight-year completion window for Pell recipients only.
- **Sector Medians & Z-scores** – Computed on the fly by filtering the Outcome Measures table by sector (IPEDS sectors 1–3 considered four-year, 4–6 considered two-year). Means, medians, and standard deviations enable contextual metrics for the selected institution.

### UI Callouts

- The Summary tab now contains a caption clarifying that “Overall Graduation Rate” comes from Outcome Measures and covers the eight-year window.
- Overview page Data Notes clarify the data files and definitions so users understand the mismatch relative to Value Grid graduation rates.

---

## Earnings Premium & ROI (California Institutions)

**Purpose:** Evaluate return on investment for California community and technical colleges using dual earnings baselines (statewide vs. county). Both the Earnings Premium section and the ROI section depend on the same processed dataset.

### Source Files (imported from the *epanalysis* repository)

| Input | Description | Original provenance | Key fields |
| ----- | ----------- | ------------------- | ---------- |
| `data/raw/epanalysis/roi-metrics.csv` | Pre-computed ROI metrics for California institutions | Combines U.S. Department of Education College Scorecard earnings (`md_earn_wne_p10`), IPEDS net price, and U.S. Census ACS 5-year county earnings baselines | `OPEID6`, `Institution`, `County`, `Sector`, `median_earnings_10yr`, `total_net_price`, `premium_statewide`, `premium_regional`, `roi_statewide_years`, `roi_regional_years`, `rank_*`, `hs_median_income` |
| `data/raw/epanalysis/opeid_unitid_mapping.csv` | Mapping between 4-digit OPEID codes (used by epanalysis) and IPEDS `UnitID` | Derived via `src/data/build_roi_opeid_mapping.py`, which matches California institutions in `data/raw/ipeds/2023/institutions.csv` by truncated OPEID and name similarity | `OPEID6`, `UnitID`, `Institution`, `County` |
| `data/raw/epanalysis/gr-institutions.csv` | Supplemental institutional context (region, program type, enrollment) | Direct export from epanalysis; not currently pulled into the dashboard but documents original attributes | `Institution`, `Region`, `Predominant Award`, `Sector`, `Undergraduate degree-seeking students` |
| `data/raw/epanalysis/hs_median_county_25_34.csv` | County-level earnings baselines for high school grads aged 25–34 | ACS 5-year estimates; already baked into `roi-metrics.csv` but retained for audit purposes | `COUNTYFIP`, `hs_median_income` |

### Processing Pipeline

1. **Mapping step** – `src/data/build_roi_opeid_mapping.py` (optional helper) creates `opeid_unitid_mapping.csv` by:
   - Filtering the IPEDS institutions table to California.
   - Aligning four-digit OPEID prefixes with the epanalysis dataset.
   - Resolving ambiguous matches via string similarity on institution names.
2. **Metrics assembly** – `src/data/build_roi_metrics.py`:
   - Loads `roi-metrics.csv` and the OPEID↔UnitID mapping (327 rows after the mapping expansion logged on 2025-10-07).
   - Joins to append IPEDS `UnitID` so dashboard components can link back to other datasets.
   - Casts columns to memory-efficient dtypes (e.g., `float32`, categorical `Sector`).
   - Derives helper columns:
     - `roi_statewide_months` / `roi_regional_months` – ROI converted to months.
     - `has_positive_premium_state` / `has_positive_premium_regional` – boolean flags for positive earnings premiums.
   - Persists the result as `data/processed/roi_metrics.parquet` (Snappy compression) for fast loading.
3. **Runtime access** – `DataManager.load_roi_metrics()` caches the Parquet file via `st.cache_data` and is shared by `EarningsPremiumSection` and `ROISection`.

### Metric Definitions

- **median_earnings_10yr** – Median earnings 10 years after entry, sourced from College Scorecard (typically cohorts circa 2010–2012).
- **total_net_price** – Total program cost used in ROI calculations. For associate institutions this is the annual net price multiplied by two years; values originate from IPEDS net price data as curated in epanalysis.
- **premium_statewide** – `median_earnings_10yr - statewide_baseline`, where the baseline is California’s median earnings for high school graduates aged 25–34 ($24,939 per the epanalysis methodology notes).
- **premium_regional** – Same calculation but using county-specific baseline earnings from the ACS (`hs_median_income` column).
- **roi_statewide_years / roi_regional_years** – Years required to recoup the investment (`total_net_price / premium_*`). A sentinel value of `999` indicates non-positive premiums (i.e., graduates earn less than the baseline).
- **roi_statewide_months / roi_regional_months** – Convenience conversion for UI display.
- **rank_statewide / rank_regional** – Precomputed rankings (1 = fastest payback) provided by epanalysis.
- **Sector** – Categorical label (Public / Private nonprofit / Private for-profit). Dataset coverage is limited to California community and technical colleges and select private career schools (327 institutions after the October 2025 mapping update).

### Dashboard Usage

- **Earnings Premium section** – Displays statewide vs. county earnings premiums, rankings, and deltas using the `premium_*` fields. The overview warns that only California institutions are included.
- **ROI section** – Renders cost-vs-earnings quadrants, top/bottom ROI rankings, and sector distributions. Charts drop rows where `roi_*_years >= 999` to remove negative-premium cases.
- **College Explorer (future work)** – `DataManager.get_institution_roi()` enables institution-level ROI lookups for California colleges when integrating ROI details into the Explorer tabs.

### Caveats & Notes

- **Geographic limitation** – No institutions outside California are represented; ROI visualizations should always reiterate this scope.
- **Time horizon** – Earnings data are vintage (~10 years post entry), so they reflect historical cohorts. Net price data correspond to the period used by epanalysis (likely 2019-20 IPEDS cycle).
- **Baseline sensitivity** – Switching between statewide and regional baselines meaningfully alters premiums and ROI; the dataset includes both perspectives for transparency.
- **Negative premiums** – Institutions with non-positive premiums are flagged via `999` ROI values and should be handled explicitly in downstream analyses.

---

## Open Items & Next Steps

- **Documentation integration:** Decide where this provenance summary should live for end users (e.g., README, in-app “Data Sources” modal, or documentation site).
- **Outcome Measures vs Graduation Rates:** Currently Value Grid and Explorer use different graduation definitions (150% of normal time vs eight-year Outcome Measures). If convergence is desired, adjust one or both pipelines; otherwise continue documenting the distinction prominently.
- **Additional sections:** Pell Grants, Federal Loans, Distance Education, and any future College Explorer ROI integration still need comparable provenance notes once their pipelines are reviewed.
- **Testing hooks:** No automated tests exist for the data pipelines; adding regression tests for the builder scripts would harden provenance guarantees.
