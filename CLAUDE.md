# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based dashboard for analyzing higher education data, focusing on college accountability metrics including cost vs graduation rates, federal loans, and Pell grants. The application visualizes data from multiple sources (IPEDS and Federal Student Aid) with comprehensive data governance and provenance tracking. 

**Current Version**: v0.8 (Comprehensive Overview pages across all sections)

**Key Features**:
- Modular architecture with separation of concerns
- Multi-source data integration with governance framework
- Tab-based navigation for improved user experience
- Comprehensive data dictionary and validation
- Performance-optimized with Parquet caching

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies (defined in pyproject.toml)
pip install -r requirements.txt  # Production dependencies: streamlit, pandas, altair, plotly
pip install -e '.[dev]'          # Development dependencies (includes pytest, ruff, black)

# Alternative: Use uv for faster installs
uv pip install -r requirements.txt
```

### Running the Application
```bash
# Launch the Streamlit dashboard
streamlit run app.py
```

### Data Processing
```bash
# Regenerate Parquet files from CSV sources
python -m src.data.datasets

# Build processed Pell grant datasets
python data/processed/build_pell_top_dollars.py
python data/processed/build_pell_vs_grad_scatter.py

# Build ROI analysis datasets
python src/data/build_roi_opeid_mapping.py  # Map OPEID to UnitID for institutions
python src/data/build_roi_metrics.py         # Generate ROI metrics Parquet

# Validate data dictionary and sources
python -c "from src.data.models import DataDictionary; DataDictionary.load_from_file('data/dictionary/schema.json')"
```

### Code Quality
```bash
# Lint code with ruff
ruff check .

# Format code with black
black src

# Run tests (note: no tests/ directory exists yet)
pytest -q
```

## Architecture & Key Components

### Modular Architecture (v0.2+)
The application follows a clean, modular architecture with separation of concerns:

- **`app.py`**: Thin orchestration layer (141 lines, down from 648)
- **`src/config/`**: Configuration management
  - `constants.py`: Dashboard constants and chart labels
  - `navigation.py`: Navigation configuration with section definitions
  - `data_sources.py`: Data source paths and loading configuration
- **`src/core/`**: Core business logic
  - `data_manager.py`: Central data management and resource loading
  - `data_loader.py`: Data loading with validation and caching
  - `exceptions.py`: Custom exception handling
- **`src/sections/`**: Dashboard sections as classes
  - `base.py`: Abstract base section with common functionality
  - `overview.py`: Landing page with navigation cards
  - `value_grid.py`: Cost vs graduation analysis
  - `federal_loans.py`: Federal loan analysis
  - `pell_grants.py`: Pell grant analysis
  - `distance_education.py`: Distance education enrollment (v0.4+)
  - `college_explorer.py`: Institution-level analysis (v0.6+)
- **`src/state/`**: Session state management
  - `session_manager.py`: Centralized session state handling
- **`src/charts/`**: Visualization components (20+ chart modules)
- **`src/ui/`**: UI utilities and renderers

### Data Flow & Governance
1. **Raw Data** (`data/raw/`): Organized by source with metadata
   - `ipeds/2023/`: IPEDS data (cost, enrollment, gradrates, institutions)
   - `fsa/`: Federal Student Aid data (loantotals, pelltotals)
   - Each source includes `metadata.yaml` with provenance info
2. **Data Dictionary** (`data/dictionary/`): 
   - `schema.json`: Machine-readable field definitions with validation rules
   - `sources.yaml`: Comprehensive source registry with update procedures
3. **Processed Data** (`data/processed/`): Parquet files optimized for performance with Snappy compression
4. **Validation**: Type-safe data models in `src/data/models.py` with constraint checking
5. **Caching**: Streamlit's `@st.cache_data` decorator with `DATA_VERSION = "parquet_v1"` for cache invalidation

### Key Data Processing Details
- **Parquet Schema**: `UnitID`/`enrollment`/`year` as Int32, `cost`/`graduation_rate` as float32, `sector`/`state` as pandas category, `institution` as pandas string
- **Validation**: Row counts, non-null counts, and statistical checks when converting CSV to Parquet
- **Fallback**: Automatic CSV fallback if Parquet is unavailable or outdated

### Navigation Structure (v0.3+)
The app uses configuration-driven navigation with consolidated tab-based UX:

**Sections**:
- **Overview**: Landing page with project context and navigation cards
- **College Value Grid**: Cost vs graduation analysis with 4-year/2-year charts
- **Federal Loans**: 4 consolidated charts with tabs
  - "Top 25 Federal Loan Dollars" → 4-year/2-year tabs
  - "Federal Loans vs Graduation Rate" → 4-year/2-year tabs
  - "Federal Loan Dollars Trend (Top 10)" → 4-year/2-year tabs
  - "Federal Loan Dollars Trend (Total)" → 4-year/2-year tabs
- **Pell Grants**: 4 consolidated charts with tabs
  - "Top 25 Pell Dollar Recipients" → 4-year/2-year tabs
  - "Pell Dollars vs Graduation Rate" → 4-year/2-year tabs
  - "Pell Dollars Trend (Top 10)" → 4-year/2-year tabs
  - "Pell Dollars Trend (Total)" → 4-year/2-year tabs
- **Distance Education** (v0.4+): 3 consolidated charts with tabs
  - "Top 25 Distance Education Enrollment" → 4-year/2-year tabs
  - "Total Enrollment Trend" → 4-year/2-year tabs
  - "Distance Education Trend" → 4-year/2-year tabs
- **College Explorer** (v0.6+): Institution-level analysis with 4 tabs
  - "Summary": Institution details, enrollment metrics, graduation rates
  - "Federal Loans & Pell Grants": Combined federal aid trends (2008-2022)
  - "Graduation Rates": Overall vs Pell student trends (2016-2023)
  - Searchable dropdown with 6,050+ institutions

**Implementation**: 
- Configuration in `src/config/navigation.py` with `SectionConfig` and `ChartConfig` classes
- Session state managed by `src/state/session_manager.py`
- Tab rendering using `st.tabs(["4-year", "2-year"])` pattern

## Development Patterns & Conventions

### Navigation Consolidation Pattern (v0.3)
When consolidating navigation buttons with tabs:
1. **Constants**: Add consolidated labels in `src/config/constants.py` (e.g., `LOAN_TOP_DOLLARS_LABEL`)
2. **Exports**: Update `src/config/__init__.py` to export new labels
3. **Section Logic**: In section class, add `_render_*_with_tabs()` methods:
   ```python
   def _render_chart_with_tabs(self, title: str) -> None:
       tab1, tab2 = st.tabs(["4-year", "2-year"])
       with tab1:
           self._render_chart("four_year", f"{title} (4-year)")
       with tab2:
           self._render_chart("two_year", f"{title} (2-year)")
   ```
4. **Backward Compatibility**: Keep individual chart handling for existing links

### Configuration-Driven Architecture
- **Navigation**: Use `NavigationConfig` classes with `SectionConfig` and `ChartConfig`
- **Constants**: Centralize all labels and identifiers in `src/config/constants.py`
- **Data Sources**: Define paths in `src/config/data_sources.py` for environment flexibility

### Data Governance Best Practices
- **Source Organization**: Separate by data provider (`ipeds/`, `fsa/`)
- **Metadata**: Include `metadata.yaml` with each source for provenance
- **Validation**: Use `src/data/models.py` classes for type safety and constraint checking
- **Documentation**: Maintain machine-readable schema in `data/dictionary/schema.json`

## Important Conventions from AGENTS.md

- **Data-First Structure**: Organize raw data by source (`data/raw/ipeds/`, `data/raw/fsa/`), derived outputs in `data/processed/`
- **Naming**: Chart modules as `*_chart.py`, section classes as `*Section`, constants in `UPPER_SNAKE_CASE`
- **Commits**: Use Conventional Commits (`feat:`, `fix:`, `data:`) with Claude Code attribution
- **Testing**: Use pytest with fixtures in `tests/fixtures/`, align test structure with `src/`
- **Security**: Exclude secrets/PII, use `.env` for credentials, share only aggregate data

## Version History

**Current Version**: v0.8 (Comprehensive Overview pages across all sections)

**Major Milestones**:
- **v0.1**: Initial Streamlit dashboard
- **v0.2**: Architecture refactoring + data governance (648→141 line app.py)
- **v0.3**: Navigation consolidation with tab-based UX
- **v0.4**: Distance Education section (COVID-era analysis)
- **v0.5**: Visual design enhancements (gradient hero, stacked bars)
- **v0.6**: College Explorer foundation (6,050+ institutions)
- **v0.7**: College Explorer comprehensive metrics (federal aid + graduation trends)
- **v0.8**: Comprehensive Overview pages (current)

For detailed changes with file references, see [LOG.md](LOG.md).