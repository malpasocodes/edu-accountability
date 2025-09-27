# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based dashboard for analyzing higher education data, focusing on college accountability metrics including cost vs graduation rates, federal loans, and Pell grants. The application visualizes data from multiple sources (IPEDS and Federal Student Aid) with comprehensive data governance and provenance tracking. 

**Current Version**: v0.3 (Navigation consolidation with tab-based UX)

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

# Install dependencies
pip install -r requirements.txt  # Production dependencies
pip install -e '.[dev]'          # Development dependencies (includes pytest, ruff, black)
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

# Validate data dictionary and sources
python -c "from src.data.models import DataDictionary; DataDictionary.load_from_file('data/dictionary/schema.json')"
```

### Code Quality
```bash
# Lint code with ruff
ruff check .

# Format code with black
black src tests

# Run tests
pytest -q
```

## Architecture & Key Components

### Modular Architecture (v0.2+)
The application follows a clean, modular architecture with separation of concerns:

- **`app.py`**: Thin orchestration layer (~135 lines, down from 648)
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
  - `overview.py`, `value_grid.py`, `federal_loans.py`, `pell_grants.py`: Section implementations
- **`src/state/`**: Session state management
  - `session_manager.py`: Centralized session state handling
- **`src/charts/`**: Visualization components
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
- **Overview**: Landing page with project context
- **College Value Grid**: Cost vs graduation analysis with 4-year/2-year charts
- **Federal Loans**: 3 consolidated charts with tabs (down from 6 individual buttons)
  - "Top 25 Federal Loan Dollars" → 4-year/2-year tabs
  - "Federal Loans vs Graduation Rate" → 4-year/2-year tabs  
  - "Federal Loan Dollars Trend" → 4-year/2-year tabs
- **Pell Grants**: 3 consolidated charts with tabs (down from 6 individual buttons)
  - "Top 25 Pell Dollar Recipients" → 4-year/2-year tabs
  - "Pell Dollars vs Graduation Rate" → 4-year/2-year tabs
  - "Pell Dollars Trend" → 4-year/2-year tabs

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

## Version History & Major Milestones

- **v0.1**: Initial Streamlit dashboard with basic functionality
- **v0.2**: Major architecture refactoring + data governance system
  - Extracted business logic from monolithic app.py (648→135 lines)
  - Implemented modular architecture with clean separation of concerns
  - Added comprehensive data dictionary and multi-source governance
  - Reorganized data by source (IPEDS/FSA) with metadata tracking
- **v0.3**: Navigation consolidation for improved UX
  - Reduced Federal Loans navigation from 6 to 3 buttons with tabs
  - Reduced Pell Grants navigation from 6 to 3 buttons with tabs
  - Enhanced user experience with consistent tab-based pattern

For detailed changes, see `LOG.md` which tracks all modifications with file references.