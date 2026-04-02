# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Streamlit dashboard analyzing U.S. higher education accountability, affordability, and outcomes. It covers ~6,000+ institutions using IPEDS, Federal Student Aid, College Scorecard, and Census data. Deployed on Render.com.

## Commands

```bash
# Run the dashboard
streamlit run app.py

# Lint and format
ruff check .
black src

# Run all tests
pytest -q

# Run a single test file
pytest tests/test_ep_calculations.py -v

# Regenerate processed Parquet files from CSV sources
python -m src.data.datasets

# Build EP and ROI datasets
python src/data/build_ep_metrics.py
python src/data/build_roi_metrics.py

# Run a canonical pipeline (3-phase pattern: extract → enrich → output)
python -m src.pipelines.canonical.ipeds_grad.extraction
python -m src.pipelines.canonical.ipeds_grad.enrich_metadata
python -m src.pipelines.canonical.ipeds_grad.build_outputs
```

## Architecture

**Entry point:** `app.py` — configures Streamlit page, initializes `SessionManager` and `DataManager`, renders sidebar navigation and main content area.

**Section-based routing:** The sidebar drives navigation. `SessionManager` tracks the active section and chart in `st.session_state`. `app.py:render_main()` maps section names to section class instances and calls `section.render(active_chart)`.

**Key layers:**

- `src/config/` — Constants, navigation tree (`SectionConfig` → `ChartConfig`), data source paths, feature flags (loaded from env vars / `.env`)
- `src/core/` — `DataManager` orchestrates all data loading with `@st.cache_data`; `DataLoader` handles CSV/Parquet I/O
- `src/sections/` — Each section extends `BaseSection(ABC)` with `render_overview()`, `render_chart(chart_name)`, and `get_available_charts()`. The base `render()` method dispatches between overview and chart views.
- `src/charts/` — Dedicated chart modules (Altair primary, Plotly secondary). Each chart is a standalone function receiving a DataFrame.
- `src/data/` — `datasets.py` manages Parquet loading/regeneration; `build_*.py` scripts produce derived datasets
- `src/pipelines/canonical/` — ETL pipelines following a 3-phase pattern (extraction → enrich_metadata → build_outputs). Each pipeline has its own subdirectory under `src/pipelines/canonical/`.
- `src/state/` — `SessionManager` wraps `st.session_state` for section/chart tracking
- `src/analytics/` — Statistical utilities (e.g., z-scores for graduation rates)

**Data flow:** Raw CSV/Parquet files in `data/raw/` → processed Parquet in `data/processed/` → loaded by `DataManager` → passed to sections → rendered by chart modules.

**Feature flags** (`src/config/feature_flags.py`): Control experimental sections via environment variables. `USE_CANONICAL_GRAD_DATA` (default: true) toggles canonical vs legacy data in College Explorer. `ENABLE_CANONICAL_IPEDS_SECTION` and `ENABLE_CANONICAL_SCORECARD_SECTION` (default: false) gate experimental sections.

## Adding a New Section

1. Add constants in `src/config/constants.py`
2. Create a `SectionConfig` in `src/config/navigation.py`
3. Implement a class extending `BaseSection` in `src/sections/`
4. Create chart modules in `src/charts/`
5. Register the section in `app.py:render_main()` and the sections `__init__.py`

## Adding a New Chart to an Existing Section

1. Add the chart label to the relevant `*_CHARTS` list in `src/config/constants.py`
2. Create a chart rendering function in the appropriate `src/charts/` module
3. Handle the chart name in the section's `render_chart()` and `get_available_charts()` methods

## Data Conventions

- Parquet with Snappy compression is the primary format; CSV is the fallback
- Column dtypes: `UnitID`/`enrollment`/`year` → `Int32`, costs/rates → `float32`, `sector`/`state` → `category`, `institution` → `string`
- Cache versioning via `DATA_VERSION = "parquet_v1"` in `src/data/datasets.py`
- Data sources are registered in `data/dictionary/sources.yaml`

## Testing

Tests mirror the `src/` structure under `tests/`. Pipeline tests cover extraction, enrichment, and output phases. Use `pytest -q` for a quick run or target specific files with `pytest tests/path/to/test.py -v`.

## Dependencies

Managed with `uv`. Python 3.10+ (deployed as 3.11.7). Core deps: streamlit, pandas, altair, plotly. Dev deps: pytest, ruff, black. Install with `uv venv && source .venv/bin/activate && uv pip install -r requirements.txt`.
