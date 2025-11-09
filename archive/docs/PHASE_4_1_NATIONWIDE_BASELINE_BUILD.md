# Phase 4.1 — Build Nationwide County Baselines from PUMS

## 🎯 Goal
Replace the current CA-only county baseline with a **nationwide county baseline** computed directly from PUMS.

This baseline will allow the *Earnings Premium: College vs Local Baseline (Alpha)* feature to compare institutional earnings against local (county-level) earnings medians for high-school graduates aged 25–34 across all U.S. counties.

---

## 🧩 Inputs (already in repo)

| Purpose | Path | Notes |
|----------|------|-------|
| ACS PUMS | `data/raw/pums/usa_00005.csv.gz` | IPUMS extract; person-level |
| PUMA→County Crosswalk | `data/raw/mcdcgeocorr/geocorr2022_2530108394.csv` | MCDC Geocorr output, includes allocation factor `afact` |
| IPEDS / Institutional Directory | `data/raw/ipeds/HD2024.csv` or `institutions.csv` | Used later for joins; no changes needed |

---

## ⚙️ Specification

### **1️⃣ New script**
`src/data/build_county_baselines_nationwide.py`

Steps:

1. Load `usa_00005.csv.gz` with dtype control and keep only:
   - `AGE`, `EDUC` or `EDUCD`, `INCWAGE`, `PERWT`, `STATEFIP`, `PUMA`

2. Filter persons:
   - `AGE ∈ [25, 34]`
   - Education = **high-school graduate** (using the appropriate `EDUC`/`EDUCD` codes)
   - Non-missing `INCWAGE`

3. Compute **PUMA-level weighted median** of `INCWAGE` using `PERWT`.  
   Also record unweighted N and sum of PERWT.

4. Load the **PUMA→County crosswalk** (`geocorr2022_2530108394.csv`):
   - Keep: `state`, `puma22`, `county`, `afact` (allocation factor)
   - Ensure all numeric fields are correctly typed

5. Join PUMA medians to the crosswalk (`state` + `PUMA` keys).

6. **Allocate PUMA medians to counties** by multiplying each PUMA median’s contribution by `afact` and aggregating to county FIPS:
   - For counties overlapping multiple PUMAs, compute a **population-weighted mean** using `afact * population_weight` as weights.  
   - Document this as an *approximation to the true weighted median*.

7. Output to:
   - `data/processed/county_baselines.parquet`  
   Columns:
     - `FIPS` (Int32)  
     - `state_fips` (Int16)  
     - `county_code` (Int16)  
     - `county_baseline_earnings` (float32, HS median 25–34)  
     - `sample_size` (Int32, sum of unweighted N)  
     - `population_weight` (Int64, sum of PERWT)

8. Print and log coverage stats (expect ~3,100+ counties).

---

### **2️⃣ Validation & QA**
Generate `data/processed/county_baselines_profile.json` with:

- Total counties covered  
- Min / median / max `county_baseline_earnings`  
- Top & bottom 10 counties by median earnings  
- Count of counties with `sample_size < 200` or `population_weight == 0`  

---

### **3️⃣ Integration**
No UI overhaul required.

- Keep the **baseline toggle** (“State | County/PUMA”) in the Alpha page.
- Replace the old CA-only CSV reference with the new nationwide `county_baselines.parquet`.
- Remove any “CA-only” labeling in text or tooltips.
- Ensure `prepare_comparison_data("county")` uses the new parquet file.

---

### **4️⃣ Performance**
- Use **chunked reading** for PUMS (`chunksize=1_000_000`) to stay under ~2–3 GB RAM.  
- Cache the computed parquet so the baseline can be reused.  
- Add a rebuild command:
  ```bash
  python -m src.data.build_county_baselines_nationwide
  ```

---

### **5️⃣ Acceptance Criteria**

| Check | Expectation |
|--------|-------------|
| `county_baselines.parquet` | ≥ 3,000 distinct county FIPS codes |
| Coverage | ≥ 50% of institutions map to a county baseline in multiple states (TX, FL, NY, IL) |
| Charts | Update correctly when toggling baselines |
| Performance | Build completes <15 minutes on dev machine |
| QA Output | `county_baselines_profile.json` present with reasonable ranges |

---

### **6️⃣ Deliverables**

1. Script: `src/data/build_county_baselines_nationwide.py`
2. Output: `data/processed/county_baselines.parquet`
3. QA Report: `data/processed/county_baselines_profile.json`
4. Short Markdown summary: `data/derived/reports/PHASE_4_1_STATUS_REPORT.md`
   - Include coverage summary, QA stats, and warnings.

---

### **7️⃣ Prompt Completion Message**
At end of run, print:

```
✅ Phase 4.1 complete — Nationwide county baselines generated.
📊 Coverage: {num_counties} counties, median earnings ${median_income}
Awaiting GO AHEAD for Phase 5.
```

---

### **8️⃣ Optional Fallback**
Until the new baseline file is available:
- Keep the toggle labeled **“County (Pilot)”**
- Show a coverage banner if <10% of filtered institutions have county data
- Continue to fallback to **state baseline** for missing counties

---

**Author:** Alfred Essa  
**File:** `docs/PHASE_4_1_NATIONWIDE_BASELINE_BUILD.md`
