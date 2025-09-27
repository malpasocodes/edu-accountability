# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based dashboard for analyzing higher education data, focusing on college accountability metrics including cost vs graduation rates, federal loans, and Pell grants. The application visualizes IPEDS (Integrated Postsecondary Education Data System) data to provide insights on institutional performance and value.

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

### Data Flow
1. **Raw Data** (`data/raw/`): IPEDS CSV extracts including `cost.csv`, `enrollment.csv`, `gradrates.csv`, `institutions.csv`, `loantotals.csv`, `pelltotals.csv`
2. **Processed Data** (`data/processed/`): Parquet files optimized for performance with Snappy compression
3. **Caching**: Streamlit's `@st.cache_data` decorator with `DATA_VERSION = "parquet_v1"` for cache invalidation

### Module Structure
- `app.py`: Main Streamlit entry point with navigation and section rendering
- `src/data/datasets.py`: Core data loading with Parquet/CSV fallback, schema enforcement, and validation
- `src/charts/`: Visualization components (e.g., `cost_vs_grad_chart.py`, `pell_trend_chart.py`)
- `src/ui/renderers.py`: UI utilities for rendering dataframes and components

### Key Data Processing Details
- **Parquet Schema**: `UnitID`/`enrollment`/`year` as Int32, `cost`/`graduation_rate` as float32, `sector`/`state` as pandas category, `institution` as pandas string
- **Validation**: Row counts, non-null counts, and statistical checks when converting CSV to Parquet
- **Fallback**: Automatic CSV fallback if Parquet is unavailable or outdated

### Navigation Structure
The app uses session state to manage navigation between sections:
- Overview (landing page)
- College Value Grid (4-year and 2-year cost vs graduation analysis)
- Federal Loans (top recipients, trends, graduation correlations)
- Pell Grants (top recipients, trends, graduation correlations)

## Important Conventions from AGENTS.md

- **Data-First Structure**: Keep canonical IPEDS extracts in root, derived outputs in `data/processed/`, source pulls in `data/raw/`
- **Naming**: Chart modules as `*_chart.py`, dataset loaders as `load_*.py`, constants in `UPPER_SNAKE_CASE`
- **Commits**: Use Conventional Commits (`feat:`, `fix:`, `data:`)
- **Testing**: Use pytest with fixtures in `tests/fixtures/`, align test structure with `src/`
- **Security**: Exclude secrets/PII, use `.env` for credentials, share only aggregate data