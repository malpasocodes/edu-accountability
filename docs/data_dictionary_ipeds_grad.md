# Data Dictionary — Canonical IPEDS Graduation Rates

## 1. Long Table (`ipeds_grad_rates_long.parquet`)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `unitid` | int64 | `110635` | IPEDS UnitID (joins to other datasets). |
| `year` | int16 | `2023` | Cohort reference year sourced from DRV/DFR column names. |
| `instnm` | string | `California State University-Long Beach` | Institution name as listed in HD. |
| `control` | string enum | `Public` | Institution control (see §4). |
| `level` | string enum | `4-year` | Institutional level (see §4). |
| `state` | string | `CA` | Two-letter postal abbreviation. |
| `sector` | string enum | `Public, 4-year or above` | IPEDS sector bucket (see §4). |
| `grad_rate_150` | float32 | `68.4` | Graduation rate within 150% of normal time, expressed 0–100. |
| `source_flag` | string | `DRVGR` | Indicates whether value came from DRVGR or DFR table. |
| `is_revised` | bool | `True` | `True` if the original wide column ended with `_RV`. |
| `cohort_reference` | string | `2023 cohort, total cohort` | Human-readable descriptor derived from the wide column header. |
| `load_ts` | datetime | `2025-11-07T18:42:49.068796` | UTC timestamp recorded during extraction. |

### Validation Rules
- `unitid` + `year` must be unique once revisions are collapsed.
- `grad_rate_150` must be null or between 0 and 100.
- `control`, `level`, and `sector` must be from the enumerations below unless metadata is missing (see `docs/ipeds_missing_metadata.md`).

## 2. Latest-by-Institution (`ipeds_grad_rates_latest_by_inst.parquet`)

One row per `unitid`, retaining the most recent cohort year present in the long table. Columns mirror the long table plus:

| Column | Description |
|--------|-------------|
| `latest_year` | Alias of `year` (most recent cohort). |

Validation: row count equals the number of distinct UnitIDs present in the long table (currently 5,437).

## 3. Summary by Year (`ipeds_grad_rates_summary_by_year.parquet`)

| Column | Description |
|--------|-------------|
| `year` | Cohort year. |
| `sector` | Sector bucket (Unknown if metadata missing). |
| `institution_count` | Distinct UnitIDs contributing to the group. |
| `avg_grad_rate` | Mean of `grad_rate_150` for the group. |
| `median_grad_rate` | Median rate. |
| `p25_grad_rate` | 25th percentile of the distribution. |
| `p75_grad_rate` | 75th percentile. |

Validation: `institution_count` should equal the number of non-null rates contributing to percentile calculations.

## 4. Enumerations

### Control
- `Public`
- `Private NP` (nonprofit)
- `Private FP` (for-profit)

### Level
- `4-year`
- `2-year`
- `<2-year`

### Sector
- `Public, 4-year or above`
- `Private nonprofit, 4-year or above`
- `Private for-profit, 4-year or above`
- `Public, 2-year`
- `Private nonprofit, 2-year`
- `Private for-profit, 2-year`
- `Public, less-than 2-year`
- `Private nonprofit, less-than 2-year`
- `Private for-profit, less-than 2-year`
- `Unknown` (only when HD metadata is unavailable)

## 5. Reproduction Steps
1. **Extraction** — `python -m src.pipelines.canonical.ipeds_grad.extraction`
2. **Metadata enrichment** — `python -m src.pipelines.canonical.ipeds_grad.enrich_metadata`
3. **Outputs build** — `python -m src.pipelines.canonical.ipeds_grad.build_outputs`

Each run writes provenance to `out/canonical/ipeds_grad/run_latest.json`. Include that JSON in reviews to show inputs, row counts, and git SHA.

### Percent Pell Grants (SFA)
1. `python -m src.pipelines.canonical.ipeds_sfa.extraction`
2. `python -m src.pipelines.canonical.ipeds_sfa.enrich_metadata`
3. `python -m src.pipelines.canonical.ipeds_sfa.build_outputs`

Provenance stored under `out/canonical/ipeds_pell/`.

## 6. Known Limitations
- Wesley College (UnitID 131098) lacks metadata in the 2023 HD file; see `docs/ipeds_missing_metadata.md` for remediation options.
- Graduation rates reflect institution-level totals only; Pell subcohorts remain out of scope for the canonical MVP.
