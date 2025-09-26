# Streamlit UI Build Plan — Ten Phases (Instructions for Codex)

This document breaks the app into **ten implementation phases** so work can ship incrementally without breaking UX. Each phase includes: goal, inputs, tasks, acceptance criteria, and notes.

---

## Phase 1 — Skeleton App + Data Hooks
**Goal:** Stand up a minimal Streamlit app with a clean layout and data-loading stubs.

**Inputs**
- `data/roi_with_county_baseline_combined_clean.csv`
- `data/pelltotals.csv`

**Tasks**
- Create `app.py` with a two-column layout: **Sidebar** and **Main**.
- Add a global loader function for each dataset (no transforms yet).
- Render a simple welcome text in Main.

**Acceptance**
- App runs with no errors; both CSVs load successfully (shape logged).
- Sidebar appears; Main shows a welcome message.

**Notes**
- Use `@st.cache_data` for loaders.
- Do not build charts yet.

---

## Phase 2 — Sidebar Sections (Collapsible)
**Goal:** Organize the Sidebar by **chart families**.

**Tasks**
- Add two collapsible groups in the Sidebar:
  - **College Value Grid**
  - **Pell Grants**
- Inside each group, show a radio or selectbox for **Chart Type** (placeholder choices).

**Acceptance**
- Only one group can be “active” at a time (whichever the user is interacting with).
- The chosen chart type persists across re-runs.

**Notes**
- Keep control names short and stable (used as keys later).

---

## Phase 3 — Contextual Filters (Section-Scoped)
**Goal:** Filters should apply **only** to the active section.

**Tasks**
- College Value Grid filters: Region (multi), Sector (Public/Private), Credential.
- Pell Grants filters: Region (multi), Sector, Enrollment band.
- Wire filters to return a filtered DataFrame (no charts yet; print a small preview).

**Acceptance**
- Changing filters in one section does not alter the other section’s state.
- Filtered row counts update correctly.

**Notes**
- Show a friendly empty-state message if the filter result is zero rows.

---

## Phase 4 — Value Grid: Quadrants Chart (MVP)
**Goal:** First real chart: Net Price (x) vs Median Earnings (y), with quadrant medians.

**Tasks**
- Compute x/y medians on the **filtered** dataset.
- Plot scatter; draw vertical/horizontal median lines.
- Color by Sector; labels off by default (toggleable).

**Acceptance**
- Chart updates with Region/Sector/Credential filters.
- Median lines reflect the current filtered subset.

**Notes**
- Keep tooltips minimal; avoid clutter.

---

## Phase 5 — Value Grid: ROI & Premium Charts
**Goal:** Add two more charts to the Value Grid family.

**Tasks**
- **ROI Scatter**: plot `roi_statewide_years` vs `roi_regional_years`; add 45° reference line; bubble size optional.
- **Premium Bars**: side-by-side bars for C-Premium vs H-Premium (top N institutions toggle).

**Acceptance**
- Users can switch between the three charts (Quadrants / ROI Scatter / Premium Bars).
- Charts honor the same section filters.

**Notes**
- Validate numeric coercion to avoid NaN plotting.

---

## Phase 6 — Pell Grants: Core Visuals
**Goal:** Build two charts for Pell Grants using `pelltotals.csv`.

**Tasks**
- **Pell Share (bars)**: Pell recipients / enrollment; sort desc; top N toggle.
- **Pell vs Net Price (bubble)**: x = net price, y = Pell share, size = enrollment, color = sector.

**Acceptance**
- Charts respond to Pell-section filters (Region/Sector/Enrollment band).
- Data preview shows the exact filtered subset used in the chart.

**Notes**
- Add optional “normalize by enrollment” toggle for dollar metrics.

---

## Phase 7 — Display Options & UX Polish
**Goal:** Make charts easier to read and export.

**Tasks**
- Add a **Display** block under each section:
  - Point labels on/off, show medians on/off, color by (sector/region),
  - Sort by (for bars), top N, show legend on/off.
- Add **Download**: PNG of chart + CSV of filtered data.

**Acceptance**
- Exported CSV matches the plotted subset.
- Exported PNG matches current chart state.

**Notes**
- Keep captions to one sentence beneath charts.

---

## Phase 8 — Rankings View (Unified List)
**Goal:** Provide a ranked list that compares SW vs Local ROI ranks.

**Tasks**
- Build a single table showing: Institution | Region | ROI Rank (Statewide) | ROI Rank (Local) | Δ.
- Add sort by Δ (largest change first) and search box for institution.

**Acceptance**
- Ranks match the underlying fields in the dataset.
- Sorting and search work together without breaking filters.

**Notes**
- Do not add heavy formatting; keep it fast and readable.

---

## Phase 9 — Help / About + Tooltips
**Goal:** Light documentation in-app.

**Tasks**
- Add an **About** section or modal with:
  - Short glossary (C-Premium, H-Premium, C-ROI, H-ROI),
  - Data provenance (e.g., ACS vintage note).
- Add help tooltips next to key controls (i-icons).

**Acceptance**
- Users can find definitions without leaving the app.
- Tooltips render on hover and are concise.

**Notes**
- Avoid long paragraphs; link to your site for deeper docs later.

---

## Phase 10 — Performance & Guardrails
**Goal:** Make it robust for large filters and edge cases.

**Tasks**
- Ensure `@st.cache_data` on loaders + any heavy transforms.
- Memoize expensive aggregations (e.g., medians) by parameter hash.
- Add defensive checks for missing columns and NaNs.
- Validate that empty states never crash charts.

**Acceptance**
- App stays responsive (< 1–2s) for common filter changes.
- No exceptions when datasets are missing optional columns.

**Notes**
- Log warnings (not errors) for non-critical anomalies.

---

## Deliverables Summary
- Sidebar with two collapsible **sections** (Value Grid, Pell).
- Section-scoped **filters** and **display options**.
- Charts: Quadrants, ROI Scatter, Premium Bars, Pell Share, Pell vs Net Price.
- Rankings table (SW vs Local ranks + Δ).
- Data preview + export (PNG, CSV).
- Help/About + tooltips.
- Caching and guardrails for stability.