# EDU Accountability Lab

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python&logoColor=white)](https://python.org)

A data-driven dashboard for analyzing higher education accountability, affordability, and outcomes across U.S. institutions. Built with Streamlit and powered by IPEDS, Federal Student Aid, and College Scorecard data.

## Features

### 📊 College Value Grid
- Cost vs graduation rate analysis for 4-year and 2-year institutions
- Quadrant visualization identifying high-value colleges (high graduation, low cost)
- 6,000+ institutions with enrollment and sector breakdowns

### 💰 Federal Loans & Pell Grants
- Top 25 recipients by total dollar volume (2008-2022)
- Loan/grant trends vs graduation rates
- Stacked bar visualizations showing year-over-year funding patterns

### 🌐 Distance Education
- Top 25 institutions by total enrollment with distance education breakdown
- Multi-year trend analysis (2020-2024) showing COVID-era shifts
- Exclusive distance vs hybrid vs in-person enrollment patterns

### 📈 ROI Analysis (California 2-Year Institutions)
- Cost vs earnings quadrant analysis for 327 CA community/technical colleges
- Dual baseline methodology (statewide vs county-specific)
- Return on investment rankings by sector

### 🔍 College Explorer
- Institution-level deep dives with searchable dropdown
- Federal aid trends, graduation rates, distance education enrollment
- Summary statistics with sector-specific benchmarks

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/college_act_charts.git
cd college_act_charts

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## Data Sources

- **IPEDS** (Integrated Postsecondary Education Data System): Cost, enrollment, graduation rates, institutional characteristics
- **Federal Student Aid**: Federal loan and Pell grant totals by institution (2008-2022)
- **College Scorecard**: Median earnings data for ROI analysis
- **U.S. Census ACS**: High school baseline earnings for ROI calculations

All data sources are documented in `data/dictionary/sources.yaml` with update procedures and provenance tracking.

## Project Structure

```
college_act_charts/
├── app.py                  # Main Streamlit application
├── src/
│   ├── sections/          # Dashboard sections (overview, value_grid, loans, etc.)
│   ├── charts/            # Chart rendering modules (20+ visualization types)
│   ├── core/              # Data management and loading
│   ├── config/            # Configuration and navigation
│   └── ui/                # UI utilities and renderers
├── data/
│   ├── raw/               # Source data organized by provider (ipeds/, fsa/)
│   ├── processed/         # Optimized Parquet files with Snappy compression
│   └── dictionary/        # Data dictionary and source registry
└── docs/                  # Additional documentation

```

## Development

### Data Processing

Regenerate processed Parquet files from CSV sources:

```bash
python -m src.data.datasets
```

Build ROI metrics dataset:

```bash
python src/data/build_roi_metrics.py
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with black
black src

# Run tests
pytest -q
```

## Version History

See [LOG.md](LOG.md) for detailed changelog.

**Current Version**: v0.8 - Comprehensive Overview pages with consistent formatting and visual hierarchy across all sections.

## Technical Notes

### Processed Data
- Files: `data/processed/tuition_vs_graduation.parquet` and `data/processed/tuition_vs_graduation_two_year.parquet` are Snappy-compressed Parquet sources used by the app
- Compression: Snappy via `DataFrame.to_parquet(..., compression="snappy")` balances size and load speed
- Column dtypes: `UnitID`/`enrollment`/`year` → `Int32`, `cost`/`graduation_rate` → `float32`, `sector`/`state` → pandas `category`, and `institution` → pandas `string`
- Cache versioning: `DATA_VERSION = "parquet_v1"` in `src/data/datasets.py` scopes Streamlit's `st.cache_data` to current Parquet schema
- Regeneration: Run `python -m src.data.datasets` to rebuild Parquet (falls back to CSV, validates counts/stats, and overwrites Parquet outputs)

## Contributing

This is a research project. For questions or collaboration opportunities, please open an issue.

## License

[Add your license information here]

## Acknowledgments

- IPEDS for comprehensive institutional data
- Federal Student Aid for financial aid data
- College Scorecard for earnings outcomes
- [epanalysis](https://github.com/malpasocodes/epanalysis) for California ROI methodology
