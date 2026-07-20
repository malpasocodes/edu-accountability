# Data Provenance Summary

This note captures where core dashboard views source their data, the definitions applied to key metrics, and any timing nuances uncovered so far. It supplements the existing data dictionary files and should be kept current as new sections or datasets are added.

---

## College Value Grid

**Purpose:** Scatter plot comparing institutional graduation rates against published in-state tuition; supports four-year and two-year views.

### Source Files

| Input | Dataset | IPEDS survey | Collection year | Key fields used |
| ----- | ------- | ------------ | ---------------- | ---------------- |
| `data/raw/ipeds/2023/cost.csv` | Tuition & fees | IC2023_AY | 2023-24 AY | `UnitID`, `TUITION_FEES_INSTATE2023` |
| `data/raw/ipeds/2023/pellgradrates.csv` | Graduation rates | Graduation Rate Survey (GRS) | Survey years 2016–2023; latest non-null year per institution | `UnitID`, `GR2023` … `GR2016` |
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
- **Graduation rate** – IPEDS Graduation Rate Survey (GRS) 150%-of-normal-time completion rate for first-time, full-time, degree-seeking students. Each institution's most recent non-null `GR{year}` is used (coalesced `GR2023` → `GR2016` in `_load_latest_grad_rates()`). For bachelor's institutions `GR2023` corresponds to the 2017 entering cohort (six years); for community colleges, three years. This replaced the broader Outcome Measures `PCT_AWARD_6YRS` cut (June 2026) so every dashboard surface reports the same measure.
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
| `data/raw/ipeds/2023/pellgradrates.csv` | Graduation Rate Survey with Pell subgroup | GRS (customized CSV pull) | Survey years 2016–2023 (`GR2023` ≈ 2017 entering cohort at four-year institutions) | `UnitID`, `GR2023`, `PGR2023`, … `GR2016`, `PGR2016` |
| `data/processed/2023/canonical/ipeds_grad_rates_latest_by_inst.parquet` | Canonical GRS pipeline (latest rate per institution) | IPEDS DRVGR/DFR, cohorts 2004–2023 | Latest survey year per institution | `unitid`, `grad_rate_150`, `year` |

### Data Flow

1. `DataManager._load_institutions_raw()` ingests the HD2023 extract.
2. `DataManager._load_distance_raw()` loads the distance education table (optional; falls back to empty if missing).
3. `DataManager._load_pellgradrates_raw()` ingests `pellgradrates.csv` for Graduation Rate Survey reporting.
4. When `USE_CANONICAL_GRAD_DATA` is enabled (the default), the canonical GRS parquet is also loaded and rendered as the "Canonical Pipeline Snapshot" metric.
5. `CollegeExplorerSection` holds references to these DataFrames and merges them in the Summary tab when an institution is selected.

### Metric Definitions

- **Enrollment metrics** – Pulled from the 2024 columns in `distanced.csv`. If a value is missing, the UI shows “N/A”. Metrics represent the latest Fall headcount for total enrollment, exclusively online enrollment, and students taking some distance education.
- **Overall Graduation Rate** – Derived from `GR2023` (or earlier year if needed) in `pellgradrates.csv`. This is the Graduation Rate Survey statistic: first-time, full-time, degree-seeking students completing within 150% of normal program time (six years for bachelor's-degree seekers). The 2023 value at four-year institutions reflects the cohort that entered in 2017. Part-time and returning students are not counted.
- **Pell Graduation Rate** – `PGR2023` (and historical peers) capturing the same GRS 150% measure for Pell recipients only.
- **Sector Medians & Z-scores** – Computed on the fly by filtering the graduation-rate table by sector (IPEDS sectors 1–3 considered four-year, 4–6 considered two-year). Means, medians, and standard deviations enable contextual metrics for the selected institution.

### UI Callouts

- The Summary tab caption states that “Overall Graduation Rate” comes from the Graduation Rate Survey (first-time, full-time, 150% of normal time). Earlier caption text describing the values as Outcome Measures was a leftover from the pre-June-2026 pipeline and was corrected 2026-07-20.
- Overview page Data Notes describe the same GRS definition; Value Grid and College Explorer now report the same measure, so no cross-section mismatch note is needed.

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

## Federal Loans

**Purpose:** Rankings, trends, and loans-vs-graduation scatter for federal loan dollars by institution.

### Source Files

| Input | Description | Coverage | Key fields |
| ----- | ----------- | -------- | ---------- |
| `data/raw/fsa/dl_volume/*.xls` | FSA Title IV Program Volume Reports — Direct Loan volume by school (COD system), Q4 workbooks | Award years 2012-13 … 2021-22 | school, OPE ID, recipients, disbursed dollars per loan type |
| `data/processed/fsa_dl_volume.{csv,parquet}` | Tidy per-school × award-year × loan-type dataset built from the workbooks | 2013–2022, keyed by OPE ID | `opeid`, `year`, `loan_type` (sub/unsub-UG/unsub-grad/Grad PLUS/Parent PLUS), `disbursed_usd` |
| `data/processed/loan_totals_cod.{csv,parquet}` | UnitID-keyed wide derivative loaded by the dashboard (`DataSources.LOAN_RAW`) | `YR2013`–`YR2022` | `UnitID`, `Institution`, year columns |

### Pipeline & Definitions

1. `src/data/build_fsa_loan_volume.py` parses the workbooks into `fsa_dl_volume`, then maps OPE-ID totals to the largest-enrollment UnitID sharing that OPEID (~95.2% of national dollars mapped) to produce `loan_totals_cod`.
2. All Federal Loans charts (top dollars, trend, vs-graduation scatter) compute from `loan_df` at render time; graduation rates in the scatter come from the value-grid metadata (GRS, see above).
3. Loan dollars are **all Title IV Direct Loan disbursements** (subsidized, unsubsidized undergrad/grad, Grad PLUS, Parent PLUS) summed per year. Coverage begins at award year 2012-13 because COD school-level reports do not exist earlier (FFEL-era lending is not published school-by-school).

### Deprecated Source

`data/raw/fsa/loantotals.csv` (an undocumented FSA "LoanBySchool" download) understates disbursements at roughly 40–60% of the official COD figures (e.g., University of Phoenix 2013–2022: $4.93B vs the official $11.11B) and was **deprecated for dollar amounts on 2026-07-10** (`data/raw/fsa/metadata.yaml`). No dashboard chart reads it. If a deployed instance shows the low figures, it is running a pre-2026-07-10 build.

### Verification

`tests/data/test_fsa_loan_volume.py` pins the cited figures against the processed files: Phoenix 2013–2022 loans $11,108,326,427 (72.7% undergraduate-directed), Pell $2,099,633,987, combined $13,207,960,414; Walden #2; national totals.

---

## Pell Grants

**Purpose:** Rankings, trends, and Pell-vs-graduation scatters for Pell Grant dollars by institution.

### Source Files

| Input | Description | Coverage | Key fields |
| ----- | ----------- | -------- | ---------- |
| `data/raw/fsa/pelltotals.csv` | FSA Pell Grant disbursements by school (`DataSources.PELL_RAW`) | `YR2008`–`YR2022` | `UnitID`, `Institution`, year columns |
| `data/processed/pell_top_dollars*.csv` | Ranking and top-10 trend datasets (`data/processed/build_pell_top_dollars.py`) | Rankings 2013–2022; trends 2008–2022 | `rank`, `PellDollars`, `YearsCovered` |
| `data/processed/pell_vs_grad_scatter*.csv` | Pell dollars vs graduation rate (`build_pell_vs_grad_scatter.py`) | 2013–2022 | `GraduationRate` (value-grid GRS), `PellDollars` |
| `data/processed/pell_grad_rate_scatter*.csv` | Pell-recipient graduation rate scatter (`build_pell_grad_rate_scatter.py`) | Rates avg `PGR2017`–`PGR2023`; dollars 2013–2022 | `PellGraduationRate`, `PellDollars` |

### Window Convention (2026-07-20)

Cross-institution **rankings and scatters sum award years 2013–2022 only** (`RANKING_START_YEAR = 2013` in `src/charts/pell_top_dollars_chart.py` and the three builders), for two reasons: (1) commensurability with the COD loan data, which begins in 2013; (2) institutions that consolidated reporting IDs (e.g., University of Phoenix under UnitID 484613) carry no pre-2013 values in the Pell file, so an all-years sum would silently compare unequal windows. **Trend charts keep the full 2008–2022 series.** The scatter's `GraduationRate` is sourced from `tuition_vs_graduation.csv`, so it always matches the Value Grid (GRS).

### Verification

`tests/data/test_pell_window.py` pins the window labels, the Phoenix scatter rate against the Value Grid rate, Phoenix's $2,099,633,987 / #1 rank, and CSU Northridge's #10 national rank over 2013–2022.

---

## Open Items & Next Steps

- **Documentation integration:** Decide where this provenance summary should live for end users (e.g., README, in-app “Data Sources” modal, or documentation site).
- **Outcome Measures vs Graduation Rates:** RESOLVED — since June 2026 every surface (Value Grid, Faculty, College Explorer, Pell/loan scatters) reports the GRS 150% first-time/full-time rate; College Explorer caption text was corrected to match on 2026-07-20. Remaining idea: surface the IPEDS Outcome Measures 8-year, all-entering-undergraduates rate (`data/raw/ipeds/om2023.csv` — committed and test-pinned but not loaded by the app) as an explicitly labeled *complementary* metric rather than a replacement.
- **Additional sections:** Distance Education, Faculty, and the feature-flagged Canonical sections still need comparable provenance notes (Pell Grants and Federal Loans are now covered above).
- **Testing hooks:** Pinned regression tests now guard the headline figures: `tests/data/test_fsa_loan_volume.py`, `test_pell_window.py`, `test_om2023.py`, `test_uop_grs_cohorts.py`, `test_uop_scorecard_debt.py`.
