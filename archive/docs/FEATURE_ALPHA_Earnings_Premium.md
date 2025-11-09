# Feature Spec: **Alpha Version** – Earnings Premium: College vs Local Baseline

> **Goal (alpha):** Add a new exploratory feature to the Streamlit site that lets users compare a college’s earnings outcome to a **baseline** (initially the **state baseline** already used by the site’s C‑Metric; later extendable to county/PUMA baseline). This feature ships behind an “Alpha Version” section in the sidebar and proceeds in **five gated phases**. **Do not advance to the next phase without my explicit “Go ahead.”**

---

## 0) Naming & Placement

- **Sidebar section (expander):** `Alpha Version`  
- **Page inside the expander:** `Earnings Premium: College vs Local Baseline (Alpha)`  
  - Short slug/path: `alpha_ep_compare`
  - Rationale: clearer than “Earnings Premium Metric Comparison”; it signals *what* is being compared and that it’s an *alpha*.
- **Style:** Match the existing sidebar pattern (icon + label, expander with one or more buttons).

---

## 1) Data & Constraints (assume these are available under `data/raw/`)

- The site already uses **C‑Metric** (state baseline) elsewhere. Reuse that logic/data for Phase 2.
- All relevant new raw data (if needed in later phases) live under `data/raw/`:
  - IPEDS institution core (e.g., `HD2024.csv`), completions (`C2024.A.csv`), fall enrollments (`EFFY2024.csv`), etc.
  - PUMS & crosswalks (if needed later): `usa_*.csv.gz` and `geocorr*PUMA_to_county*.csv`.
- **Alpha scope:** In Phases 1–3, the baseline = **state baseline (C‑Metric)**. Phases 4–5 introduce a toggle to allow **county/PUMA baseline** once validated (but it can default to state if county/PUMA isn’t present yet).

**Key columns likely in use already:**
- `unitid` (IPEDS)
- `state/STATEFIP/stabbr`
- Outcome measure used by C‑Metric (institution-level earnings figure you are already surfacing)
- Baseline measure (state-level earnings figure used by C‑Metric)

> If column names differ in your repo, implement a thin mapping layer in `services/alpha/config.py` so the page code stays stable.

---

## 2) Deliverables & Non‑Goals

- **Deliverables (per phase):** working code, tests, and a short **Phase Report** written to `data/derived/reports/PHASE_##_REPORT.md` summarizing what’s done, data checked, and any TODOs/risks.
- **Non‑Goals (alpha):** No sanction logic, no official GE determinations, no student‑facing language, no promises about DOE methodology.

---

## 3) Architecture Notes

- Keep the **feature isolated** under `alpha/` namespacing so it’s easy to remove or iterate:
  - `app/pages/alpha_ep_compare.py` (Streamlit page)
  - `app/services/alpha/ep_compare.py` (domain logic)
  - `app/services/alpha/config.py` (paths, column maps, feature flags)
  - `app/services/alpha/io.py` (data loaders + schema checks)
  - `tests/alpha/…` (unit tests)
- Use **Streamlit caching** for I/O and computed frames.
- **Feature flag**: `ALPHA_EP_COMPARE_ENABLED=true` (env or config). The sidebar button should appear only if this evaluates truthy.

---

## 4) Five Phases (gated)

Each phase ends with:
1. Code committed,
2. Minimal tests passing,
3. A short **Phase Report** in `data/derived/reports/`,
4. A prompt in the console/log asking for my approval to proceed.

### **Phase 1 — UI Scaffolding (Sidebar + Page Stub)**
**Objective:** Add the “Alpha Version” expander and a working page stub that loads with no data dependencies.

**Tasks**
- Add a new expander `Alpha Version` to the sidebar UI (mirroring existing style).
- Inside the expander, add a button/link: `Earnings Premium: College vs Local Baseline (Alpha)` → routes to `alpha_ep_compare` page.
- Create `alpha_ep_compare.py` page with:
  - Title, short description, and feature flag check.
  - A read-only “Scope & Caveats” callout block.
  - A disabled baseline toggle (grayed out) indicating “State (active) | County/PUMA (coming soon)”.

**Acceptance Criteria**
- Page appears only when `ALPHA_EP_COMPARE_ENABLED=true`.
- Clicking the button loads the page with no errors.
- **Phase Report** includes screenshots + a note of any TODOs.

---

### **Phase 2 — Data Wiring (State Baseline via existing C‑Metric)**
**Objective:** Wire in the **state baseline** already present in the app (reuse existing loaders) and show a basic table for a selected state’s institutions.

**Tasks**
- Implement `services/alpha/io.py` to reuse/import the existing C‑Metric data access layer for:
  - Institution earnings (current metric already shown elsewhere)
  - State baseline earnings (the C‑Metric baseline)
- On the page:
  - Add filters: **State**, **Sector/Control**, optional **Min Enrollment**.
  - Display a basic data table with: `unitid, name, state, inst_earnings, state_baseline`.
  - Add a computed column `ep_delta = inst_earnings - state_baseline` and `ep_ratio = inst_earnings / state_baseline`.
- Add light schema checks (row counts, not‑null checks for required columns).

**Acceptance Criteria**
- Table renders with filters and computed EP fields.
- **Phase Report** documents:
  - Data sources/paths used,
  - Schema snapshot (column names + dtypes),
  - Row counts after filters,
  - % rows with non-null earnings and baseline.

---

### **Phase 3 — Visuals + Download (State Baseline)**
**Objective:** Provide quick visuals + CSV export to make the alpha useful for review.

**Tasks**
- Add simple visuals:
  - Scatter: `state_baseline` (x) vs `inst_earnings` (y) with a 45° reference line.
  - Histogram of `ep_delta`.
- Provide **Download CSV** of the filtered/computed table.
- Add unit tests for `ep_delta` and `ep_ratio` correctness on a tiny fixture.

**Acceptance Criteria**
- Plots render without layout jank.
- CSV downloads the exact table shown.
- Tests pass.
- **Phase Report** includes example plots and summary stats (mean/median `ep_delta`).

---

### **Phase 4 — Baseline Toggle (State ↔ County/PUMA, if available)**
**Objective:** Introduce a toggle to switch baselines. If county/PUMA data are not present, keep the toggle visible but disabled with a helpful note.

**Tasks**
- Add a baseline selector: `Baseline Source = State (default) | County/PUMA (beta)`.
- Implement loaders in `services/alpha/io.py` for **county/PUMA baseline** from `data/raw/` files if present:
  - Expected inputs (if available): `geocorr*_PUMA_to_county*.csv`, `usa_*.csv.gz` processed medians, or a pre‑baked county baseline CSV.
- Add a clean join from institution → county baseline (fail gracefully if missing county for an institution; show a warning badge).
- Recompute `ep_delta`/`ep_ratio` based on selected baseline.

**Acceptance Criteria**
- When county/PUMA baseline exists, the toggle becomes active, and the table + charts update accordingly.
- Missing data paths or unmatched counties produce **non‑blocking** warnings (not crashes).
- **Phase Report** documents mapping coverage (% of institutions mapped to a county baseline), any biases discovered, and performance notes.

---

### **Phase 5 — QA, Performance, Docs**
**Objective:** Harden the alpha feature for broader internal testing.

**Tasks**
- Add caching to heavy loaders; ensure memory footprint is reasonable.
- Add a **“Notes & Limitations”** panel that explains:
  - Alpha status, approximation caveats,
  - Differences between state vs county/PUMA baselines,
  - That this is not GE, not sanctions, and may not match DOE methodology.
- Add smoke tests for the page to load end‑to‑end.
- Write short **user docs**: `docs/alpha_ep_compare.md` (how to use, where data come from).

**Acceptance Criteria**
- Page loads fast on typical filters.
- Docs render in repo; **Phase Report** summarizes test results and any open issues.

---

## 5) Developer Prompts

When you’re ready for each phase, you (Claude Code) should:
1. Implement changes,
2. Run local checks,
3. Write `data/derived/reports/PHASE_##_REPORT.md` with a concise summary,
4. Print: **“Phase ## complete. Awaiting GO AHEAD.”**

Do **not** start the next phase until I explicitly approve.

---

## 6) Nice‑to‑Haves (later)

- Compare **institution vs program** once program‑level earnings are available.
- Add **statewide and sector medians** to the scatter (optional overlays).
- Persist filter selections via query params for shareable views.

---

## 7) Quick Checklist

- [ ] Feature flag in config/env
- [ ] Sidebar: Alpha Version expander + page link
- [ ] Page stub with scope/caveats
- [ ] Reuse C‑Metric state baseline (Phase 2)
- [ ] EP deltas/ratios + filters + table
- [ ] Plots + CSV export
- [ ] Baseline toggle (state ↔ county/PUMA) with graceful fallback
- [ ] Reports per phase
- [ ] Docs + tests + caching

---

**Author:** Alfred / ChatGPT  
**File:** `docs/FEATURE_ALPHA_Earnings_Premium.md`
