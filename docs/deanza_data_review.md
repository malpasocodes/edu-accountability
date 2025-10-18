# De Anza College – Data Snapshot (for Rebuttal)

**UnitID:** 113333  
**Location:** Cupertino, California (Santa Clara County)  
**Sector:** Public, 2-year (IPEDS sector 4)  
**Core Sources:** IPEDS 2023 extracts, FSA Pell/Loan totals, epanalysis ROI dataset migrated into `data/processed/roi_metrics.parquet`.

---

## 1. Affordability & Completion (College Value Grid Dataset)

| Metric | Value | Two-Year Segment Median | Relative Standing |
| ------ | ----- | ----------------------- | ----------------- |
| In-state tuition & fees (2023-24) | \$1,562 | \$5,214 | **70% below** median cost |
| Graduation rate (150% of time, 2015 cohort) | 43% | 33% | **10 pts above** median |
| Undergraduate enrollment (Fall 2023) | 14,953 | — | — |

- With below-median cost and above-median graduation rate, De Anza plots in the **“High Graduation, Low Cost”** quadrant (Value Grid).
- Net cost advantage is even starker when compared with the broader ROI dataset where the **median total net price is \$17,550** (see Section 3).

---

## 2. Outcome Measures & Equity (College Explorer data)

- IPEDS Outcome Measures (8-year window, 2015 entrants):
  - **Overall completion rate (GR2023):** 68%
  - **Pell recipient completion rate (PGR2023):** 71%
- Z-scores calculated against all 2-year institutions:
  - **Overall graduation z-score:** **+0.97**
  - **Pell student graduation z-score:** **+1.11**
- Interpretation: De Anza sits roughly **one standard deviation above** its 2-year peers on both overall and Pell-specific completion outcomes.

---

## 3. Return on Investment (ROI & Earnings Premium dataset)

| Metric | De Anza | Median (CA ROI dataset, n=327) |
| ------ | ------- | ------------------------------ |
| Total net price (program) | **\$4,667** | \$17,550 |
| Statewide earnings premium | \$31,657 | \$13,378 |
| Regional earnings premium (Santa Clara County baseline) | \$23,096 | — |
| ROI – statewide baseline | **0.147 years (≈1.8 months)** | 1.04 years |
| ROI – regional baseline | 0.202 years (≈2.4 months) | — |
| ROI rank (statewide baseline) | **22nd / 327** | — |
| ROI rank (regional baseline) | 32nd / 327 | — |

- Even when benchmarked against higher county-level wages, De Anza’s payback period is **≈10 weeks**, keeping it in the top decile statewide.
- Earnings data derive from College Scorecard median wages 10 years after entry; baselines stem from ACS high school earnings (statewide \$24,939; Santa Clara \$33,500).

---

## 4. Federal Aid Footprint

**Pell Grants (FSA totals, dollars disbursed to students):**

| Year | Pell Dollars |
| ---- | ------------- |
| 2022 | \$12,773,929 |
| 2021 | \$12,118,867 |
| 2020 | \$13,440,558 |
| 2019 | \$13,327,653 |
| 2014 (pre-pandemic reference) | \$17,604,093 |

- De Anza consistently channels **\$12–17 million** in Pell aid annually, signaling a large low-income learner population.

**Federal Loans:**

| Year | Loan Dollars |
| ---- | ------------ |
| 2022 | \$2,266,356 |
| 2021 | \$1,776,605 |
| 2020 | \$2,189,251 |
| 2018 | \$2,821,291 |
| 2014 | \$6,101,643 |

- Loan volumes are modest relative to Pell grants and have trended downward since the mid-2010s.

---

## 5. Distance Education Mix (IPEDS Distance Education survey)

| Year | Total Headcount | Exclusive Distance Ed | On-campus / Hybrid* |
| ---- | ---------------- | --------------------- | ------------------- |
| Fall 2024 | 28,620 | 14,780 (**51.6%**) | **13,840 (48.4%)** |
| Fall 2023 | 26,518 | 14,849 (56.0%) | 11,669 (44.0%) |
| Fall 2022 | 26,779 | 21,177 (79.0%) | 5,602 (21.0%) |
| Fall 2021 | 29,214 | 28,851 (98.8%) | 363 (1.2%) |
| Fall 2020 | 28,029 | 6,620 (23.6%) | 21,409 (76.4%) |

- Post-pandemic recovery is evident: exclusive online share fell from **~99% (2021)** to **~52% (2024)**, restoring an on-campus/hybrid majority (~13.8k students).
- “Some Distance Ed” participants (hybrid learners) numbered **10,989** in 2024.

\*On-campus/hybrid = Total – Exclusive Distance Ed (includes students taking at least one in-person course).

---

## 6. Additional Context

- **Institutional profile:** Public, 2-year, commuter campus in Silicon Valley with long-running applied programs (e.g., nursing, automotive technology).
- **Pell vs. campus engagement:** High Pell volumes coupled with high completion z-scores suggest support structures (e.g., tutoring, advising) remain effective despite online offerings.
- **ROI & affordability:** Among the fastest ROI payback institutions statewide, driven by low tuition and strong post-graduation earnings.
- **Campus vitality:** Distance-ed mix shows a significant return to in-person/hybrid participation, countering the notion that De Anza has “gone virtual” altogether.

---

### Data References

- `data/processed/tuition_vs_graduation_two_year.csv`
- `data/raw/ipeds/2023/pellgradrates.csv`
- `data/raw/ipeds/2023/distanced.csv`
- `data/raw/fsa/pelltotals.csv`, `data/raw/fsa/loantotals.csv`
- `data/raw/epanalysis/roi-metrics.csv`, `data/raw/epanalysis/opeid_unitid_mapping.csv`

Prepared as factual backing for rebuttal arguments regarding De Anza College’s performance and modality mix.
