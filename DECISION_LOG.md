# Decision Log

| Date       | Decision                                                                 | Rationale                                                                                  | Related Files |
|------------|---------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|---------------|
| 2025-11-07 | Adopt `uv` for virtual env creation and dependency installs in Quick Start | Aligns documentation with the canonical pipeline plan that standardizes on `uv` tooling. | README.md     |
| 2025-11-07 | DL-001 — Canonical IPEDS Grad Phase 01 scope approved | Confirms pipeline location, raw input coverage (Winter 2023-24), and schema definition artifact. | docs/schema_canonical_ipeds_grad.md |
| 2025-11-07 | DL-002 — Phase 02 extraction uses `data/raw/ipeds/grad_rates_2004_2023.csv` | Standardizes on the consolidated DRVGR file and stores long-format output under `data/processed/2023/canonical/`. | src/pipelines/canonical/ipeds_grad/extraction.py |
| 2025-11-07 | DL-003 — Phase 03 metadata joins IPEDS 2023 institutions | Control/level/state/sector fields now derive from `data/raw/ipeds/2023/institutions.csv`; unmatched UnitIDs (18 rows) remain null and flagged for future remediation. | src/pipelines/canonical/ipeds_grad/enrich_metadata.py |
