
# Project: Canonical Pipeline Integration for EDU Accountability

## Purpose
This project establishes a **canonical data pipeline architecture** inside the existing EDU Accountability repository.  
It defines how all critical datasets (starting with IPEDS Graduation Rates) are cleaned, transformed, validated, and versioned **within the same repo** that powers the website and dashboards.

The goal is to achieve:
- A **single source of truth** for all data.
- **Reproducible, traceable transformations**.
- **Predictable data contracts** between pipelines and the dashboard.
- A **governed, review-driven workflow** that ensures quality without fragmenting the filesystem.

---

## Guiding Principles

- **Unified repository:** Keep the canonical pipeline, app code, and data in one repo (`data/raw`, `data/processed/<year>`, `src/...`, `tests/...`).
- **Namespace isolation:** Canonical code lives under `src/pipelines/canonical/…` with mirrored tests in `tests/pipelines/canonical/…`.
- **Predictable outputs:** Canonical artifacts are written into subfolders such as  
  `data/processed/2023/canonical/ipeds_grad_rates_long.parquet`.
- **Provenance and validation:** Each canonical build writes a run-metadata record  
  (`out/canonical/ipeds_grad/run-<timestamp>.json`) capturing inputs, hashes, and validation results.
- **Workflow, not separation:** The canonical pipeline is isolated via feature branches, module namespaces, and governance practices — not by moving to a separate project tree.

---

## Branch Policy

- Create a dedicated feature branch for each canonical dataset:

  ```
  feat/canonical-ipeds-grad
  ```

- Work only inside this branch until review and sign-off.
- Require `pytest` + `ruff` to pass before merging.
- Record major design or schema decisions in `DECISION_LOG.md`.

---

## Directory and File Conventions

```
data/
  raw/                     # raw IPEDS and other sources
  processed/
    2023/
      canonical/           # canonical outputs live here
src/
  core/                    # standard loaders reference canonical outputs
  pipelines/
    canonical/
      ipeds_grad/          # first canonical pipeline (this project)
tests/
  pipelines/
    canonical/
      test_ipeds_grad.py
out/
  canonical/
    ipeds_grad/
      run-<timestamp>.json
docs/
  schema_canonical_ipeds_grad.md
  data_dictionary_ipeds_grad.md
```

Scripts and orchestration:

```
scripts/run_canonical_ipeds_grad.sh
python -m src.pipelines.canonical.ipeds_grad.build
```

---

## Example Canonical Outputs (IPEDS Graduation Rates)

| Output | Description |
|---------|-------------|
| `data/processed/2023/canonical/ipeds_grad_rates_long.parquet` | Institution × Year graduation rates (2004–2023) |
| `data/processed/2023/canonical/ipeds_grad_rates_latest_by_inst.parquet` | Most recent graduation rate per institution |
| `data/processed/2023/canonical/ipeds_grad_rates_summary_by_year.parquet` | National and sector summaries |
| `out/canonical/ipeds_grad/run-<timestamp>.json` | Metadata: timestamps, git SHA, input hashes, validation results |

---

## Phased Plan Overview

The canonical framework applies across all datasets, but the first implementation targets IPEDS Graduation Rates.  
Each phase ends with a **STOP checkpoint** and requires explicit “Go-ahead” before the next begins.

### **Phase 00 — Setup and Branch**
Create `feat/canonical-ipeds-grad`, scaffold `src/pipelines/canonical/ipeds_grad/` and mirrored test directory.  
Verify CI, `pytest`, and `ruff` run cleanly.

### **Phase 01 — Source Inventory and Schema Definition**
Inventory IPEDS files in `data/raw/`.  
Define canonical schema and data contract in `docs/schema_canonical_ipeds_grad.md`.

### **Phase 02 — Extraction (Wide → Long)**
Implement parsing of DRV/DFR tables to standardized long format.  
Add unit tests under `tests/pipelines/canonical/`.

### **Phase 03 — Metadata Enrichment**
Merge institutional metadata from IPEDS HD files.  
Normalize control, level, state, and sector fields.

### **Phase 04 — Rate Policy Documentation**
Document precedence rules (official DRV vs computed rates).  
Update `DECISION_LOG.md` accordingly.

### **Phase 05 — Canonical Outputs Build**
Write validated outputs into  
`data/processed/<year>/canonical/ipeds_grad_*.parquet`.  
Generate `run-<timestamp>.json` metadata.

### **Phase 06 — Documentation**
Add `docs/data_dictionary_ipeds_grad.md` and update repository README sections describing canonical data governance.

### **Phase 07 — Gentle App Integration**
Update `src/core/loaders.py` to reference canonical outputs.  
Add a config toggle (e.g., `USE_CANONICAL_DATA=True`) and test one chart with the canonical feed.

### **Phase 08 — Validation and Comparison**
Compare canonical vs existing dashboard metrics (medians, distributions, sample institutions).  
Record findings in `DECISION_LOG.md`.

### **Phase 09 — Merge and Tag**
Merge `feat/canonical-ipeds-grad` → `main`.  
Tag release `canonical-ipeds-grad-v1.0` and archive metadata in `out/canonical/ipeds_grad/`.

---

## Governance and Quality Gates

- **Decision log:** Every schema or tooling decision appended to `DECISION_LOG.md`.
- **CI enforcement:** All canonical modules must pass `pytest` and `ruff` before PR approval.
- **Metadata:** Every canonical run emits a structured JSON record with hashes of inputs and row counts.
- **Review cadence:** Architecture or data-governance review at each STOP checkpoint.

---

## Summary

This integrated model keeps canonical data generation **co-located** with the app while maintaining isolation through modular design and workflow discipline.  
It ensures every dataset — starting with IPEDS Graduation Rates — is:
- Cleaned and validated consistently,  
- Versioned and reproducible,  
- Immediately consumable by dashboards and APIs,  
- Documented and auditable.

Once IPEDS Graduation Rates reach version `v1.0`, the same canonical framework can onboard additional datasets (College Scorecard, Pell Grants, Census, etc.) with minimal friction.

---
