
# Phase 01 — Source Inventory & Schema Definition  
*(Canonical IPEDS Graduation Rates)*

## Objective
Establish the **foundation** for the canonical IPEDS Graduation Rates dataset by  
1️⃣ confirming all raw input files are present and documented, and  
2️⃣ defining a clear, stable **schema contract** for the canonical output tables.

This phase sets the stage for extraction and transformation in later phases.

---

## Scope
- Covers only **data discovery and schema design**.  
- No transformation, cleaning, or output generation yet.  
- Focus dataset: IPEDS Graduation Rates (2004 – 2023).  
- Future datasets (Scorecard, Pell Grants, etc.) will follow the same template.

---

## Tasks for Codex

### 1. Verify Environment and Structure
Confirm the following repo paths are present (create empty directories if they are missing):

```
data/raw/                           # canonical project follows existing data-first layout
data/raw/ipeds/                     # IPEDS files remain in their current provider folder
data/processed/<year>/canonical/    # per-year canonical outputs (e.g., data/processed/2023/canonical/)
src/pipelines/canonical/ipeds_grad/
tests/pipelines/canonical/
docs/
out/canonical/ipeds_grad/
```

⚠️ Do **not** rename or relocate existing raw files—if the repo currently keeps IPEDS data directly under `data/raw/`, simply ensure that structure is documented.  
When preparing the processed area, create the `<year>` directory that corresponds to the latest collection (2023 today) and nest `canonical/` inside it so downstream loaders continue to find files at `data/processed/2023/canonical/…`.

---

### 2. Inventory Raw IPEDS Sources
Generate a short **README inventory** at  
`docs/ipeds_raw_inventory.md` listing every file in `data/raw/ipeds/` relevant to graduation rates.

Required baseline files (names may vary slightly by year):

| File | Description |
|------|--------------|
| `DRVGR_2004_2023.csv` | Wide derived graduation-rate table |
| `grYYYY.csv` | Annual Graduation Rates component |
| `hdYYYY.csv` | Institutional Characteristics (metadata) |
| *(optional)* `grsYYYY.csv` | Subcohorts (Pell, gender, etc.) |

For each file, include:
- Year range covered  
- Approximate **row count or file size** (see note below)  
- Key columns  
- Encoding / delimiter if non-standard

> **Note on row counts:**  
> Using `pandas.read_csv(..., nrows=1000)` only loads the first 1,000 rows, so it will always report 1,000 regardless of file size.  
> To estimate total rows, use a streaming count such as:  
> ```python
> sum(1 for _ in open("gr2023.csv")) - 1
> ```  
> or record the file’s size in MB as a proxy if counting every line is impractical.  
> This prevents misleading inventory numbers and gives reviewers a sense of file scale.

Output: a markdown table summarizing this inventory.

---

### 3. Define Canonical Schema Contract
Create `docs/schema_canonical_ipeds_grad.md` describing the **long-format schema** to be produced in Phase 02.

#### Required columns
| Column | Type | Description |
|---------|------|-------------|
| `unitid` | int64 | Institution ID |
| `year` | int16 | Reference year of cohort (2004–2023) |
| `instnm` | string | Institution name (from HD) |
| `control` | category {Public, Private NP, Private FP} | Control type |
| `level` | category {4-year, 2-year, <2-year} | Institution level |
| `state` | string (2-letter) | State abbreviation |
| `sector` | category | Optional IPEDS sector code |
| `grad_rate_150` | float32 | Graduation rate within 150 % of normal time (%) |
| `source_flag` | string {DRV, DFR} | Source identifier |
| `is_revised` | bool | Whether column had `_RV` suffix |
| `cohort_reference` | string | Text descriptor (“2017 cohort, 4-year”) |
| `load_ts` | datetime | Ingestion timestamp |

#### Field rules
- Percent values stored as numeric 0–100.  
- Drop rows missing `unitid` or `year`.  
- Range validation: `0 ≤ grad_rate_150 ≤ 100`.  
- Enumerations documented in `docs/data_dictionary_ipeds_grad.md` (created later).

---

### 4. Document Data Lineage
Add a section to `docs/README_canonical_ipeds_grad.md` titled **“Data Lineage and Inputs”**, noting:
- Raw source folder(s)  
- Extraction year range  
- IPEDS components used (`GR`, `HD`, `DRV`)  
- Update frequency (annual winter collection)

This will serve as an anchor for metadata in later phases.

---

### 5. Add Governance Entries
Append the following entry to `DECISION_LOG.md`:

> **DL-001 — Canonical IPEDS Grad Phase 01 Approved Scope**  
> - Canonical pipeline remains in `src/pipelines/canonical/ipeds_grad/`.  
> - Raw inputs sourced from IPEDS Winter 2023-24 collection (2004–2023 coverage).  
> - Output schema defined in `docs/schema_canonical_ipeds_grad.md`.  
> - Next phase (02) will implement extraction logic.

---

## Deliverables
| File | Purpose |
|------|----------|
| `docs/ipeds_raw_inventory.md` | Summary of raw inputs |
| `docs/schema_canonical_ipeds_grad.md` | Canonical schema definition |
| Updated `DECISION_LOG.md` | Governance record |
| Updated `docs/README_canonical_ipeds_grad.md` | Data lineage section |

---

## Exit Criteria (Go/No-Go)
✅ All required files exist and are committed.  
✅ Inventory and schema docs pass review.  
✅ No data processing code beyond lightweight inspection.  
Once approved, Codex may proceed to **Phase 02 (Extraction Wide → Long)**.

---
