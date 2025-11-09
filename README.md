# EDU Accountability Lab

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python&logoColor=white)](https://python.org)

A data-driven dashboard for analyzing higher education accountability, affordability, and outcomes across U.S. institutions. Built with Streamlit and powered by IPEDS, Federal Student Aid, and College Scorecard data.

## Features

### 🏠 Overview
- Landing page with project context and navigation
- Data scope explanations and important disclaimers
- Navigation cards for quick access to all sections

### 📊 College Value Grid
- Cost vs graduation rate analysis for 4-year and 2-year institutions
- Quadrant visualization identifying high-value colleges (high graduation, low cost)
- Interactive scatter plots with median reference lines
- Quadrant breakdowns with institution lists and CSV downloads
- 6,000+ institutions with enrollment filtering (all/>500/>1,000/>5,000/>10,000)

### 💵 Federal Loans
- Largest federal loan portfolios with Top 10/25/50/100 selector (aggregated 2008-2022)
- Loan trends vs graduation rates with year-over-year analysis
- Multi-year trend charts for top 10 institutions
- Aggregate national trend analysis showing total lending patterns
- Consolidated tab-based navigation (4-year/2-year)
- Sector-colored bar and multi-series line chart visualizations

### 🎓 Pell Grants
- Largest Pell grant portfolios with Top 10/25/50/100 selector (aggregated 2008-2022)
- Pell vs graduation rate correlation analysis with Top-N selector + grad-rate guide rails
- Year-over-year funding pattern trends (2008-2022)
- Aggregate national trend analysis showing total aid patterns
- Need-based aid distribution visualizations
- Tab-based 4-year/2-year comparisons with sector-colored charts + totals

### 💻 Distance Education
- Top 25 institutions by total enrollment with distance breakdown
- COVID-era trend analysis (2020-2024) with year-over-year changes
- Exclusive distance vs on-campus/hybrid enrollment patterns
- Stacked bar charts showing enrollment composition
- Institution-specific trend lines with percentage calculations

### 📈 Earnings Premium Analysis (National)
**Comprehensive 9-page analysis for July 1, 2026 EP requirements:**
- **Overview**: Explanation of One Big Beautiful Bill Act and EP Test framework
- **Risk Distribution**: 6,429 institutions categorized into 4 risk levels (High/Moderate/Low/Very Low) with complete downloadable institution lists
- **Risk Map**: Interactive scatter plot (earnings vs state thresholds) with filters by risk level, sector, and state
- **Risk Quadrants**: Sector-colored scatter plots for each risk category
- **Sector Comparison**: 6 sector tabs (Public/Private nonprofit/For-profit × 4yr/2yr) with complete institution lists and CSV exports
- **State Analysis**: State-by-state deep dives with threshold rankings and risk breakdowns (50 states + DC + National Overview)
- **Program Distribution**: Scale visualization showing ~165,000 programs subject to EP requirements across 3,900+ institutions
- **Institution Lookup**: Searchable institution finder with detailed risk assessments and peer comparisons
- **Methodology & Limitations**: Data sources, calculation formulas, and critical disclaimers

**Key Statistics**: 28.4% Very Low Risk, 22.1% Low Risk, 13.8% Moderate Risk, 19.7% High Risk, 16.0% No Data

### 💰 ROI Analysis (California Institutions)
- **Overview**: Federal policy framework and Earnings Premium Test context
- **Cost vs Earnings Quadrant**: Scatter plot with ROI gradient coloring for 327 CA institutions
- **Top 25 ROI Rankings**: Side-by-side comparison of statewide (C-Metric) vs regional (H-Metric) baselines
- **ROI by Sector**: Box plot distribution showing median, quartiles, and outliers across sectors
- Dual baseline methodology: Statewide ($24,939) vs county-specific thresholds
- Includes public community colleges, private for-profit, and private nonprofit institutions

### 🔍 College Explorer
**Institution-level deep dives with 4 comprehensive tabs:**
- **Summary**: Institution details, enrollment metrics (total/distance/hybrid), graduation rates with sector benchmarks and z-scores
- **Federal Loans & Pell Grants**: Combined 15-year trend visualization (2008-2022) with cumulative totals and year-over-year changes
- **Graduation Rates**: Dual-line trend (Overall vs Pell students) with equity gap analysis (2016-2023)
- **Distance Education**: Enrollment composition breakdown with line charts and stacked bars (2020-2024)
- Searchable dropdown with 6,050+ institutions
- Summary statistics with recent year values and historical averages

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/college_act_charts.git
cd college_act_charts

# Create uv-managed virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies with uv
uv pip install -r requirements.txt
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

## Data Sources

- **IPEDS** (Integrated Postsecondary Education Data System): Cost, enrollment, graduation rates, institutional characteristics, distance education
- **IPEDS Completions**: Program-level completions data (C2024_a.csv) for program count analysis
- **Federal Student Aid**: Federal loan and Pell grant totals by institution (2008-2022)
- **College Scorecard**: Median earnings data for ROI analysis
- **U.S. Census ACS**: High school baseline earnings for ROI calculations
- **Earnings Premium Analysis**: State median earnings thresholds, institutional earnings medians, enrollment data

All data sources are documented in `data/dictionary/sources.yaml` with update procedures and provenance tracking.

## Canonical Data Pipeline

- The canonical IPEDS Graduation Rates pipeline (Phases 01–05) lives under `src/pipelines/canonical/ipeds_grad/` with matching docs in `docs/README_canonical_ipeds_grad.md`.
- Rebuild steps:
  1. `python -m src.pipelines.canonical.ipeds_grad.extraction`
  2. `python -m src.pipelines.canonical.ipeds_grad.enrich_metadata`
  3. `python -m src.pipelines.canonical.ipeds_grad.build_outputs`
- Outputs land in `data/processed/2023/canonical/` and provenance metadata in `out/canonical/ipeds_grad/`. See `docs/data_dictionary_ipeds_grad.md` for schemas and validations.
- Additional canonical datasets (Percent Pell, Percent Loans) share the same workflow (`src/pipelines/canonical/ipeds_sfa/`). For quick previews, open the “Canonical IPEDS” section in the app.
- App integration toggle: set environment variable `USE_CANONICAL_GRAD_DATA=true` (default) to power the College Explorer graduation summary with the canonical pipeline; set to `false` to fall back to legacy Outcome Measures data only.

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

Build Earnings Premium metrics and program counts:

```bash
# Build program counts from IPEDS completions
python src/data/build_program_counts.py

# Build EP metrics dataset (includes program counts)
python src/data/build_ep_metrics.py
```

Build ROI datasets:

```bash
# Build ROI OPEID mapping
python src/data/build_roi_opeid_mapping.py

# Build ROI metrics dataset
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

**Current Version**: v0.8 - Comprehensive dashboard with 8 major sections including advanced Earnings Premium Analysis with 9 sub-pages, 6,000+ institutions, program-level tracking (~165,000 programs), and complete state/sector/risk analysis capabilities.

## Technical Notes

### Processed Data
- Files: Multiple Parquet files including `tuition_vs_graduation.parquet`, `ep_analysis.parquet` (6,429 institutions), `program_counts.parquet` (3,936 institutions), `roi_metrics.parquet` (327 CA institutions), and federal aid datasets
- Compression: Snappy via `DataFrame.to_parquet(..., compression="snappy")` balances size and load speed
- Column dtypes: `UnitID`/`enrollment`/`year` → `Int32`, `cost`/`graduation_rate` → `float32`, `sector`/`state` → pandas `category`, and `institution` → pandas `string`
- Cache versioning: `DATA_VERSION = "parquet_v1"` in `src/data/datasets.py` scopes Streamlit's `st.cache_data` to current Parquet schema
- Regeneration: Run `python -m src.data.datasets` to rebuild Parquet (falls back to CSV, validates counts/stats, and overwrites Parquet outputs)

## Contributing

This is a research project. For questions or collaboration opportunities, please open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- IPEDS for comprehensive institutional data
- Federal Student Aid for financial aid data
- College Scorecard for earnings outcomes
- [epanalysis](https://github.com/malpasocodes/epanalysis) for California ROI methodology
