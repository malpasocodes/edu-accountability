# IPEDS Institutions Missing Metadata (Phase 03)

During metadata enrichment we detected **1** institution present in the canonical graduation-rate table that lacks a matching record in `data/raw/ipeds/2023/institutions.csv`. This typically means the institution closed, merged, or otherwise fell out of the current HD snapshot.

| UnitID | Institution Name | Notes |
|--------|------------------|-------|
| 131098 | Wesley College | Missing from 2023 HD file; investigate older HD releases or successor institution (Delaware State). |

Actions:
- Attempt lookup in `data/raw/ipeds/2024/HD2024.csv` during Phase 04 validation.
- If still absent, document as a permanently closed institution and consider backfilling metadata manually for historical completeness.
