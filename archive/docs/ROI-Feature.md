# ROI Analysis Integration Strategy
## Comprehensive Implementation Plan for College Accountability Dashboard

**Document Version:** 1.0
**Date:** 2025-10-06
**Status:** Research Complete - Awaiting Implementation Approval

---

## Executive Summary

This document outlines a comprehensive strategy for integrating Return on Investment (ROI) analysis capabilities into the College Accountability Dashboard by adapting methodologies from the [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis) repository.

**Repository Analysis Summary:**
- **Purpose**: Data-driven analysis of higher education ROI for California's 2-year and certificate-granting colleges
- **Core Methodology**: Comparative ROI calculation using statewide vs. county-based high school earnings baselines
- **Key Metrics**: Earnings premium, years to recoup investment, net present value
- **Data Sources**: College Scorecard (median earnings 10-year post-entry), IPEDS (costs), Census ACS (baseline earnings)
- **Technology Stack**: Python 3.13+, Streamlit, Pandas, Altair
- **Architecture**: Modular library structure with separate data, visualization, and UI components

**Integration Approach:**
This plan proposes enhancing the existing **College Explorer** section with ROI analysis capabilities rather than creating a standalone ROI section. This approach leverages:
1. Existing institution-level analysis infrastructure
2. Current IPEDS cost and graduation data
3. Established College Scorecard API integration pathway
4. Modular chart and data loading patterns

**Key Value Proposition:**
- Add post-graduation earnings data to provide true value assessment beyond just cost and completion rates
- Enable "years to recoup" investment calculations for individual institutions
- Compare institutions not just on inputs (cost) and process (graduation) but on outcomes (earnings)
- Provide policymakers and students with comprehensive value metrics

---

## 1. Repository Analysis: epanalysis

### 1.1 Architecture Overview

The epanalysis repository follows a clean modular architecture similar to our project:

```
epanalysis/
├── app.py                    # Streamlit orchestration (similar to our app.py)
├── lib/                      # Core modules (analogous to our src/)
│   ├── data.py              # Data loading and ROI calculations
│   ├── data_improved.py     # Enhanced data processing
│   ├── data_schema.py       # Pydantic models for validation
│   ├── charts.py            # Altair visualization components
│   ├── components.py        # Reusable UI components
│   ├── models.py            # Statistical/ML models
│   ├── hs_baseline.py       # High school baseline calculations
│   ├── ui.py                # UI utilities
│   └── utils.py             # Helper functions
├── data/                     # Raw datasets
│   ├── roi-metrics.csv      # 120 CA institutions with pre-calculated ROI
│   ├── gr-institutions.csv  # Institution characteristics
│   └── hs_median_county_25_34.csv  # County baseline earnings
├── content/                  # Application documentation
└── documentation/            # Project documentation
```

**Architectural Alignment:**
- Both use Streamlit for UI orchestration
- Both follow modular separation of concerns (data, charts, UI)
- Both use configuration-driven navigation
- Both leverage Pandas for data processing and Altair for visualization
- Both implement data validation and type safety

### 1.2 ROI Calculation Methodology

**Core Formula:**
```python
# Earnings Premium Calculation
premium_statewide = median_earnings_10yr - baseline_statewide
premium_regional = median_earnings_10yr - baseline_regional

# ROI (Years to Recoup) Calculation
roi_years_statewide = total_net_price / premium_statewide
roi_years_regional = total_net_price / premium_regional

# Where:
# - median_earnings_10yr: College Scorecard field (10 years post-entry)
# - baseline_statewide: State-level high school graduate median earnings
# - baseline_regional: County-level high school graduate median earnings
# - total_net_price: Total program cost (2-year programs multiply annual by 2)
```

**Key Insights:**
1. **Two Baseline Approaches**: Comparing against statewide vs. county-specific high school earnings reveals how local economic conditions affect perceived ROI
2. **Investment Period**: Uses total program cost (years * annual net price) as the investment amount
3. **Return Period**: 10-year post-entry earnings data provides stable outcome measurement
4. **Negative Premium Handling**: Institutions where graduates earn less than high school grads are flagged (ROI = 999 years or excluded)

**Data Requirements:**
- **Median Earnings 10-Year**: From College Scorecard API (`md_earn_wne_p10`)
- **Net Price**: From IPEDS (we already have this in `cost.csv`)
- **High School Baseline Earnings**: From Census ACS 5-year estimates by state/county
- **Program Length**: Derived from institution level/sector (2-year vs 4-year)

### 1.3 Data Schema and Models

**Institution Data Model (from data_schema.py):**
```python
@dataclass
class InstitutionBase:
    unitid: str                    # Matches our UnitID
    opeid6: str                    # OPEID identifier
    institution: str               # Institution name
    city: str
    region: str                    # Could map to our STATE field
    predominant_award: AwardType   # Certificate, Associates, Bachelors, etc.
    sector: Sector                 # PUBLIC, PRIVATE_FOR_PROFIT, PRIVATE_NON_PROFIT
    zip_code: str
    latitude: float
    longitude: float

    # ROI-specific fields
    median_earnings_10yr: float    # NEW - from College Scorecard
    annual_net_price: float        # From our cost.csv
    total_net_price: float         # Calculated: annual * years
    earnings_above_hs: float       # Calculated: earnings premium
    roi_years: float               # Calculated: years to recoup
    undergrad_students: int        # From our enrollment.csv
```

**Sector Enum:**
```python
class Sector(Enum):
    PUBLIC = "Public"
    PRIVATE_FOR_PROFIT = "Private for-profit"
    PRIVATE_NON_PROFIT = "Private nonprofit"
```

**Alignment with Our Data:**
- `unitid` → Our `UnitID` (primary key across all datasets)
- `sector` → Our `SECTOR` field maps to 1=Public, 2=Private nonprofit, 3=Private for-profit
- `predominant_award` → Our `LEVEL` field (1=4-year+, 2=2-year, 3=Less than 2-year)
- `institution` → Our `INSTITUTION` field
- We already have: city, state, zip, sector, enrollment

**Missing Fields (need to acquire):**
- `median_earnings_10yr` - **Critical new data source**
- High school baseline earnings by state/county - **New reference data**

### 1.4 Visualization Approaches

**Primary Chart Type: Quadrant Scatter Plot**
```python
# From charts.py analysis
def create_roi_scatter(df):
    """
    Scatter plot with median reference lines creating four quadrants:
    - Top Right: High earnings, high price (premium institutions)
    - Top Left: High earnings, low price (high ROI)
    - Bottom Right: Low earnings, high price (poor ROI)
    - Bottom Left: Low earnings, low price (budget options)
    """
    median_price = df['annual_net_price'].median()
    median_earnings = df['median_earnings_10yr'].median()

    chart = alt.Chart(df).mark_circle(size=70).encode(
        x=alt.X('annual_net_price:Q', title='Annual Net Price', scale=alt.Scale(zero=False)),
        y=alt.Y('median_earnings_10yr:Q', title='Median Earnings (10yr)', scale=alt.Scale(zero=False)),
        color=alt.Color('sector:N', legend=alt.Legend(title='Sector')),
        tooltip=['institution', 'annual_net_price', 'median_earnings_10yr', 'roi_years', 'sector']
    )

    # Add median reference lines
    vline = alt.Chart(pd.DataFrame({'x': [median_price]})).mark_rule(strokeDash=[5, 5], color='gray').encode(x='x:Q')
    hline = alt.Chart(pd.DataFrame({'y': [median_earnings]})).mark_rule(strokeDash=[5, 5], color='gray').encode(y='y:Q')

    return (chart + vline + hline).properties(height=520)
```

**Additional Visualization Patterns:**
1. **ROI Distribution Chart**: Histogram showing distribution of years-to-recoup across institutions
2. **Top/Bottom Rankings**: Bar charts of best/worst ROI performers (similar to our Top 25 patterns)
3. **Earnings Premium Comparison**: Stacked bar showing earnings vs. baseline by sector
4. **Trend Analysis**: If we acquire historical earnings data, show ROI trends over time

**Styling Characteristics:**
- Uses Altair's declarative approach (matches our existing charts)
- Circle marks with size=70 for scatter plots
- Sector-based color encoding (aligns with our color schemes)
- Rich tooltips with multiple metrics
- Height=520px (consistent sizing)
- Non-zero scaled axes for better data visibility

---

## 2. Integration Architecture

### 2.1 Strategic Decision: Enhance College Explorer vs. Standalone Section

**Recommendation: Integrate ROI into College Explorer (Approach A)**

**Rationale:**
1. **Conceptual Fit**: ROI is inherently institution-specific analysis - perfect for College Explorer's mission
2. **Data Reuse**: College Explorer already loads institution details, enrollment, costs - we just add earnings
3. **User Journey**: Users exploring a specific college naturally want to know earning outcomes
4. **Navigation Simplicity**: Avoid proliferation of top-level sections
5. **Existing Patterns**: Aligns with multi-tab approach (Summary, Federal Aid, Graduation, **+ ROI**)

**Current ROI Section Status:**
The placeholder `src/sections/roi.py` exists but only has "Coming Soon" stub implementations. We can either:
- **Option A (Preferred)**: Remove stub ROI section, integrate into College Explorer
- **Option B**: Keep ROI section for aggregate cross-institution ROI comparisons (Top 25 ROI, etc.)

**Proposed Hybrid Approach:**
- **College Explorer Tab**: "Earnings & ROI" - institution-level earnings and ROI analysis
- **Standalone ROI Section**: Aggregate analyses like "Top 25 ROI Institutions," "ROI by Sector," "Earnings vs Cost Quadrant"

This mirrors the existing pattern where:
- College Explorer provides institution-level detail
- Other sections (Federal Loans, Pell Grants) provide aggregate comparative analysis

### 2.2 Data Pipeline Architecture

**Enhanced Data Flow:**
```
1. Raw Data Sources:
   ├── data/raw/ipeds/2023/
   │   ├── institutions.csv       [Existing]
   │   ├── cost.csv               [Existing]
   │   ├── enrollment.csv         [Existing]
   │   └── gradrates.csv          [Existing]
   ├── data/raw/college_scorecard/
   │   └── earnings_latest.csv    [NEW - API pull]
   └── data/raw/census/
       └── hs_earnings_acs.csv    [NEW - ACS baseline]

2. Processed Data:
   ├── data/processed/
   │   ├── roi_metrics.parquet    [NEW - merged dataset]
   │   ├── roi_by_sector.parquet  [NEW - aggregate analysis]
   │   └── roi_top_institutions.parquet  [NEW - rankings]

3. Validation:
   └── src/data/models.py         [Enhanced with ROI fields]

4. Loading:
   └── src/core/data_loader.py    [Enhanced with ROI methods]

5. Section Rendering:
   ├── src/sections/college_explorer.py  [Enhanced with ROI tab]
   └── src/sections/roi.py               [New aggregate ROI section]

6. Visualization:
   └── src/charts/
       ├── roi_scatter_chart.py          [NEW]
       ├── roi_distribution_chart.py     [NEW]
       └── roi_rankings_chart.py         [NEW]
```

**Data Governance Updates:**
```yaml
# data/dictionary/sources.yaml additions:
sources:
  college_scorecard:
    name: "College Scorecard"
    provider: "U.S. Department of Education"
    organization: "Office of Federal Student Aid"
    description: "Comprehensive data on college costs, graduation, debt, and post-college earnings"
    base_url: "https://collegescorecard.ed.gov/"
    api_url: "https://api.data.gov/ed/collegescorecard/v1/"
    license: "Public Domain"
    update_frequency: "Annual"
    datasets:
      earnings:
        name: "Median Earnings by Institution"
        description: "Median earnings of students 6, 8, and 10 years after entry"
        fields:
          - md_earn_wne_p6  # 6-year earnings
          - md_earn_wne_p8  # 8-year earnings
          - md_earn_wne_p10 # 10-year earnings (primary)
          - count_wne_p10   # Count of students with earnings data

  census_acs:
    name: "American Community Survey (ACS)"
    provider: "U.S. Census Bureau"
    description: "Demographic and economic characteristics of U.S. population"
    base_url: "https://data.census.gov/"
    api_url: "https://api.census.gov/data/2021/acs/acs5"
    license: "Public Domain"
    update_frequency: "Annual (5-year estimates)"
    datasets:
      earnings_by_education:
        name: "Median Earnings by Educational Attainment"
        description: "State and county-level median earnings for high school graduates"
        table: "B20004" # Median earnings by education
        age_range: "25-34" # To match recent graduates
```

### 2.3 Configuration Changes

**Constants Update (`src/config/constants.py`):**
```python
# ROI labels - Enhanced for College Explorer integration
ROI_OVERVIEW_LABEL = "Overview"
ROI_EARNINGS_LABEL = "Earnings & ROI Analysis"
ROI_QUADRANT_LABEL = "Cost vs Earnings Quadrant"
ROI_TOP_INSTITUTIONS_LABEL = "Top 25 by ROI"
ROI_BY_SECTOR_LABEL = "ROI by Sector & Level"

ROI_CHARTS: List[str] = [
    ROI_QUADRANT_LABEL,
    ROI_TOP_INSTITUTIONS_LABEL,
    ROI_BY_SECTOR_LABEL,
]

# College Explorer additions
COLLEGE_ROI_LABEL = "Earnings & ROI"

COLLEGE_EXPLORER_CHARTS: List[str] = [
    COLLEGE_SUMMARY_LABEL,
    COLLEGE_LOANS_PELL_LABEL,
    COLLEGE_GRAD_RATES_LABEL,
    COLLEGE_ROI_LABEL,  # NEW
]
```

**Navigation Update (`src/config/navigation.py`):**
```python
# Update COLLEGE_EXPLORER section config
COLLEGE_EXPLORER = SectionConfig(
    name=COLLEGE_EXPLORER_SECTION,
    icon="🔍",
    label="College Explorer",
    overview_chart=ChartConfig(
        label=COLLEGE_EXPLORER_OVERVIEW_LABEL,
        key="nav_college_explorer_overview",
        description="Explore individual college data"
    ),
    charts=[
        ChartConfig(label=COLLEGE_SUMMARY_LABEL, key="nav_college_explorer_0", description="Institution profile and key metrics"),
        ChartConfig(label=COLLEGE_LOANS_PELL_LABEL, key="nav_college_explorer_1", description="Federal aid trends (2008-2022)"),
        ChartConfig(label=COLLEGE_GRAD_RATES_LABEL, key="nav_college_explorer_2", description="Graduation rate trends"),
        ChartConfig(label=COLLEGE_ROI_LABEL, key="nav_college_explorer_3", description="Earnings outcomes and ROI analysis"),  # NEW
    ],
    session_key="college_explorer_chart",
    description="Get detailed information on individual colleges including ROI"
)

# ROI section for aggregate analysis
ROI = SectionConfig(
    name=ROI_SECTION,
    icon="💰",
    label="ROI Analysis",
    overview_chart=ChartConfig(
        label=ROI_OVERVIEW_LABEL,
        key="nav_roi_overview",
        description="Return on investment across all institutions"
    ),
    charts=[
        ChartConfig(label=chart_label, key=f"nav_roi_{index}", description=None)
        for index, chart_label in enumerate(ROI_CHARTS)
    ],
    session_key="roi_chart",
    description="Analyze return on investment for higher education"
)
```

**Data Sources Configuration (`src/config/data_sources.py`):**
```python
# Add ROI-specific data sources
ROI_METRICS_PATH = PROCESSED_DIR / "roi_metrics.parquet"
ROI_BY_SECTOR_PATH = PROCESSED_DIR / "roi_by_sector.parquet"
ROI_TOP_INSTITUTIONS_PATH = PROCESSED_DIR / "roi_top_institutions.parquet"

EARNINGS_RAW_PATH = RAW_DIR / "college_scorecard" / "earnings_latest.csv"
HS_BASELINE_PATH = RAW_DIR / "census" / "hs_earnings_acs.csv"
```

---

## 3. Dataset Requirements and Acquisition

### 3.1 Critical New Data: College Scorecard Earnings

**Primary Data Element:**
- **Field Name**: `md_earn_wne_p10` (Median earnings of students working and not enrolled 10 years after entry)
- **Source**: College Scorecard API
- **API Endpoint**: `https://api.data.gov/ed/collegescorecard/v1/schools`
- **API Key**: Required (free registration at api.data.gov)
- **Update Frequency**: Annual (typically July/August)
- **Current Data**: 2009-10 and 2010-11 entry cohorts (as of 2024 release)

**Required Fields from API:**
```json
{
  "id": "UnitID (maps to our primary key)",
  "school.name": "Institution name",
  "latest.earnings.10_yrs_after_entry.working_not_enrolled.median": "md_earn_wne_p10",
  "latest.earnings.10_yrs_after_entry.working_not_enrolled.count": "count_wne_p10",
  "latest.earnings.6_yrs_after_entry.working_not_enrolled.median": "md_earn_wne_p6",
  "latest.earnings.8_yrs_after_entry.working_not_enrolled.median": "md_earn_wne_p8",
  "latest.cost.avg_net_price.overall": "average_net_price (validation against IPEDS)",
  "latest.completion.completion_rate_4yr_150nt": "4-year completion rate (validation)"
}
```

**API Query Example:**
```bash
curl -X GET "https://api.data.gov/ed/collegescorecard/v1/schools.json?\
api_key=YOUR_API_KEY&\
_fields=id,school.name,latest.earnings.10_yrs_after_entry.working_not_enrolled.median,\
latest.earnings.10_yrs_after_entry.working_not_enrolled.count,\
latest.cost.avg_net_price.overall&\
_per_page=100"
```

**Python Implementation Pattern:**
```python
# src/data/college_scorecard_api.py
import requests
import pandas as pd
from pathlib import Path
from typing import Optional
import streamlit as st

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_college_scorecard_earnings(api_key: str, save_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Fetch earnings data from College Scorecard API.

    Args:
        api_key: College Scorecard API key
        save_path: Optional path to save raw CSV

    Returns:
        DataFrame with UnitID, institution, earnings fields
    """
    base_url = "https://api.data.gov/ed/collegescorecard/v1/schools.json"

    fields = [
        "id",
        "school.name",
        "latest.earnings.10_yrs_after_entry.working_not_enrolled.median",
        "latest.earnings.10_yrs_after_entry.working_not_enrolled.count",
        "latest.earnings.6_yrs_after_entry.working_not_enrolled.median",
        "latest.earnings.8_yrs_after_entry.working_not_enrolled.median",
        "latest.cost.avg_net_price.overall",
    ]

    params = {
        "api_key": api_key,
        "_fields": ",".join(fields),
        "_per_page": 100,
        "_page": 0,
    }

    all_results = []

    while True:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        all_results.extend(results)

        # Check if more pages
        metadata = data.get("metadata", {})
        if params["_page"] >= metadata.get("total", 0) // params["_per_page"]:
            break

        params["_page"] += 1

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            "UnitID": r["id"],
            "institution": r["school.name"],
            "median_earnings_10yr": r["latest.earnings.10_yrs_after_entry.working_not_enrolled.median"],
            "earnings_count_10yr": r["latest.earnings.10_yrs_after_entry.working_not_enrolled.count"],
            "median_earnings_6yr": r["latest.earnings.6_yrs_after_entry.working_not_enrolled.median"],
            "median_earnings_8yr": r["latest.earnings.8_yrs_after_entry.working_not_enrolled.median"],
            "scorecard_avg_net_price": r["latest.cost.avg_net_price.overall"],
        }
        for r in all_results
    ])

    # Handle missing values (College Scorecard uses "NULL" strings and actual nulls)
    numeric_cols = ["median_earnings_10yr", "earnings_count_10yr", "median_earnings_6yr",
                    "median_earnings_8yr", "scorecard_avg_net_price"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)

    return df
```

**Data Quality Considerations:**
- **Coverage**: Not all institutions have earnings data (typically 60-70% coverage)
- **Privacy Suppression**: Institutions with <30 students in earnings cohort have suppressed data
- **Program-Level vs Institution-Level**: API provides institution-level aggregates; field-of-study data available separately
- **Cohort Timing**: 10-year data is from students who entered 10 years ago (lag inherent in metric)

### 3.2 Secondary Data: High School Baseline Earnings

**Purpose**: Calculate earnings premium by comparing graduate earnings to high school-only earnings baseline

**Two Baseline Approaches:**
1. **Statewide Baseline**: Single median for each state (simpler, more stable)
2. **County Baseline**: County-specific medians (more precise, captures local economics)

**Data Source**: Census Bureau American Community Survey (ACS) 5-Year Estimates
- **Table**: B20004 (Median Earnings in the Past 12 Months by Sex by Educational Attainment)
- **API**: `https://api.census.gov/data/2021/acs/acs5`
- **Geography**: State (for statewide) and County (for county-level)
- **Educational Attainment**: High school graduate (including equivalency), no college
- **Age Range**: 25-34 years (to match recent graduates)

**ACS API Query Example:**
```bash
# State-level high school earnings
curl "https://api.census.gov/data/2021/acs/acs5?\
get=NAME,B20004_003E&\
for=state:*&\
key=YOUR_CENSUS_API_KEY"

# County-level high school earnings
curl "https://api.census.gov/data/2021/acs/acs5?\
get=NAME,B20004_003E&\
for=county:*&\
in=state:*&\
key=YOUR_CENSUS_API_KEY"
```

**Implementation Pattern:**
```python
# src/data/census_acs_api.py
import requests
import pandas as pd
from typing import Literal

def fetch_hs_baseline_earnings(
    api_key: str,
    geography: Literal['state', 'county'] = 'state'
) -> pd.DataFrame:
    """
    Fetch high school graduate median earnings from Census ACS.

    Args:
        api_key: Census API key
        geography: 'state' or 'county' level aggregation

    Returns:
        DataFrame with state/county FIPS codes and median earnings
    """
    base_url = "https://api.census.gov/data/2021/acs/acs5"

    if geography == 'state':
        params = {
            "get": "NAME,B20004_003E",  # B20004_003E = HS grad median earnings
            "for": "state:*",
            "key": api_key,
        }
    else:  # county
        params = {
            "get": "NAME,B20004_003E",
            "for": "county:*",
            "in": "state:*",
            "key": api_key,
        }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()

    # First row is headers, rest is data
    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)

    # Rename columns
    df = df.rename(columns={
        "NAME": "geography_name",
        "B20004_003E": "hs_median_earnings",
        "state": "state_fips",
        "county": "county_fips" if geography == 'county' else None,
    })

    # Convert earnings to numeric
    df['hs_median_earnings'] = pd.to_numeric(df['hs_median_earnings'], errors='coerce')

    # Create combined FIPS code for counties
    if geography == 'county':
        df['fips'] = df['state_fips'] + df['county_fips']
    else:
        df['fips'] = df['state_fips']

    return df[['fips', 'geography_name', 'hs_median_earnings']].dropna()
```

**Mapping to Our Data:**
- Our `institutions.csv` has `STATE` field (2-letter code)
- Our `institutions.csv` has `FIPS` field (5-digit county FIPS)
- Need to create state FIPS to state code mapping
- Can join baseline earnings by FIPS to calculate regional premium

**Simplified Approach for Phase 1:**
Instead of API calls, we can use pre-calculated national and state averages:
```python
# Hardcoded baselines (2021 ACS estimates, age 25-34)
NATIONAL_HS_BASELINE = 32000  # National median for HS grads age 25-34

STATE_HS_BASELINES = {
    "AL": 28500, "AK": 38000, "AZ": 31000, "AR": 27500, "CA": 34000,
    "CO": 35500, "CT": 38000, "DE": 33500, "FL": 30000, "GA": 30500,
    # ... (all 50 states)
}
```

### 3.3 Data Merging and Validation

**Merged Dataset Schema (`data/processed/roi_metrics.parquet`):**
```python
# Core fields (from existing data)
- UnitID: int32              # Primary key
- institution: string        # Institution name
- state: category            # State abbreviation
- fips: string               # County FIPS code
- sector: category           # 1=Public, 2=Private nonprofit, 3=Private for-profit
- level: category            # 1=4-year+, 2=2-year, 3=<2-year
- enrollment: int32          # Total enrollment
- graduation_rate: float32   # 150% time graduation rate
- annual_net_price: float32  # Average annual net price

# New fields (from College Scorecard)
- median_earnings_6yr: float32   # Median earnings 6 years post-entry
- median_earnings_8yr: float32   # Median earnings 8 years post-entry
- median_earnings_10yr: float32  # Median earnings 10 years post-entry (primary)
- earnings_count_10yr: int32     # Number of students in earnings cohort

# New fields (from Census ACS)
- hs_baseline_state: float32     # State-level HS graduate median earnings
- hs_baseline_county: float32    # County-level HS graduate median earnings (if available)

# Calculated fields
- total_program_cost: float32    # annual_net_price * years (2 for 2-year, 4 for 4-year)
- earnings_premium_state: float32    # median_earnings_10yr - hs_baseline_state
- earnings_premium_county: float32   # median_earnings_10yr - hs_baseline_county
- roi_years_state: float32           # total_program_cost / earnings_premium_state
- roi_years_county: float32          # total_program_cost / earnings_premium_county
- roi_months_state: int32            # roi_years_state * 12 (for display)
- has_earnings_data: bool            # Flag for institutions with earnings data
```

**Merge Logic:**
```python
# Pseudocode for data merging
def build_roi_metrics():
    # 1. Load existing datasets
    institutions = load_institutions()  # UnitID, institution, state, fips, sector, level
    cost = load_cost()                  # UnitID, annual_net_price
    enrollment = load_enrollment()      # UnitID, enrollment
    gradrates = load_gradrates()        # UnitID, graduation_rate

    # 2. Merge existing data
    base_df = (institutions
        .merge(cost, on='UnitID', how='left')
        .merge(enrollment, on='UnitID', how='left')
        .merge(gradrates, on='UnitID', how='left')
    )

    # 3. Load new earnings data
    earnings = fetch_college_scorecard_earnings(api_key)

    # 4. Merge earnings (left join to preserve all institutions)
    df = base_df.merge(earnings, on='UnitID', how='left', suffixes=('', '_scorecard'))

    # 5. Load baseline earnings
    state_baselines = load_state_hs_baselines()  # state -> hs_baseline_state
    county_baselines = load_county_hs_baselines()  # fips -> hs_baseline_county

    # 6. Merge baselines
    df = (df
        .merge(state_baselines, left_on='state', right_on='state', how='left')
        .merge(county_baselines, left_on='fips', right_on='fips', how='left')
    )

    # 7. Calculate program cost
    df['years'] = df['level'].map({1: 4, 2: 2, 3: 2})  # 4-year, 2-year, <2-year
    df['total_program_cost'] = df['annual_net_price'] * df['years']

    # 8. Calculate earnings premiums
    df['earnings_premium_state'] = df['median_earnings_10yr'] - df['hs_baseline_state']
    df['earnings_premium_county'] = df['median_earnings_10yr'] - df['hs_baseline_county']

    # 9. Calculate ROI (handle division by zero and negative premiums)
    df['roi_years_state'] = df.apply(
        lambda row: calculate_roi(row['total_program_cost'], row['earnings_premium_state']),
        axis=1
    )
    df['roi_years_county'] = df.apply(
        lambda row: calculate_roi(row['total_program_cost'], row['earnings_premium_county']),
        axis=1
    )

    # 10. Add flags and derived fields
    df['has_earnings_data'] = df['median_earnings_10yr'].notna()
    df['roi_months_state'] = (df['roi_years_state'] * 12).round().astype('Int32')

    # 11. Validate and save
    validate_roi_metrics(df)
    df.to_parquet('data/processed/roi_metrics.parquet', engine='pyarrow', compression='snappy')

    return df

def calculate_roi(cost: float, premium: float) -> float:
    """Calculate ROI with handling for edge cases."""
    if pd.isna(cost) or pd.isna(premium):
        return np.nan
    if premium <= 0:
        return 999.0  # Flag institutions with negative/zero premium
    if cost <= 0:
        return 0.0
    return cost / premium
```

**Validation Rules:**
```python
def validate_roi_metrics(df: pd.DataFrame) -> None:
    """Validate ROI metrics dataset."""
    # Required fields exist
    required_fields = ['UnitID', 'institution', 'state', 'sector', 'level']
    assert all(field in df.columns for field in required_fields)

    # UnitID is unique
    assert df['UnitID'].is_unique

    # Earnings coverage (expect 60-70%)
    earnings_coverage = df['has_earnings_data'].mean()
    assert 0.5 <= earnings_coverage <= 0.9, f"Earnings coverage {earnings_coverage:.1%} outside expected range"

    # Valid ranges
    assert df['median_earnings_10yr'].dropna().between(10000, 200000).all(), "Earnings outside valid range"
    assert df['annual_net_price'].dropna().between(0, 80000).all(), "Net price outside valid range"
    assert df['hs_baseline_state'].dropna().between(20000, 50000).all(), "Baseline outside valid range"

    # ROI reasonableness (excluding 999 flags)
    valid_roi = df['roi_years_state'].between(0, 30)
    assert valid_roi.sum() > 0, "No institutions with valid ROI"

    print(f"Validation passed: {len(df)} institutions, {earnings_coverage:.1%} with earnings data")
```

---

## 4. Implementation Phases

### Phase 1: Foundation and Data Acquisition (Weeks 1-2)

**Objective**: Establish data pipeline and basic ROI calculations without UI changes

**Tasks:**

1.1 **Set up API access** (Day 1)
   - Register for College Scorecard API key (api.data.gov)
   - Register for Census API key (api.census.gov)
   - Store API keys in `.env` file (add to `.gitignore`)
   - Update `.env.example` with placeholder keys

1.2 **Create API client modules** (Days 2-3)
   - `src/data/college_scorecard_api.py` - Scorecard data fetcher
   - `src/data/census_acs_api.py` - ACS baseline data fetcher
   - Implement caching with `@st.cache_data`
   - Add error handling and retry logic
   - Write unit tests for API clients

1.3 **Create data processing pipeline** (Days 4-5)
   - `src/data/build_roi_metrics.py` - Main processing script
   - Implement merge logic (institutions + cost + enrollment + earnings + baselines)
   - Calculate ROI metrics (earnings premium, years to recoup)
   - Handle missing data and edge cases
   - Generate `data/processed/roi_metrics.parquet`

1.4 **Update data models** (Day 6)
   - Add ROI fields to `src/data/models.py`:
     ```python
     @dataclass(frozen=True)
     class ROIMetrics:
         unitid: int
         median_earnings_10yr: Optional[float]
         earnings_count_10yr: Optional[int]
         hs_baseline_state: float
         hs_baseline_county: Optional[float]
         total_program_cost: float
         earnings_premium_state: float
         earnings_premium_county: Optional[float]
         roi_years_state: float
         roi_years_county: Optional[float]
         roi_months_state: Optional[int]
         has_earnings_data: bool
     ```
   - Update `DataDictionary` schema with ROI fields

1.5 **Update data governance** (Day 7)
   - Add College Scorecard and Census ACS to `data/dictionary/sources.yaml`
   - Create `data/raw/college_scorecard/metadata.yaml`
   - Create `data/raw/census/metadata.yaml`
   - Document ROI calculation methodology in `data/dictionary/README.md`

1.6 **Extend DataManager** (Days 8-9)
   - Add methods to `src/core/data_manager.py`:
     ```python
     @st.cache_data(ttl=3600)
     def get_roi_metrics(_self) -> pd.DataFrame:
         """Load ROI metrics dataset."""
         return load_parquet_with_fallback(ROI_METRICS_PATH, ROI_METRICS_CSV_PATH)

     def get_institution_roi(self, unitid: int) -> Optional[Dict]:
         """Get ROI metrics for a specific institution."""
         roi_df = self.get_roi_metrics()
         institution_roi = roi_df[roi_df['UnitID'] == unitid]
         if institution_roi.empty:
             return None
         return institution_roi.iloc[0].to_dict()
     ```

1.7 **Testing and validation** (Day 10)
   - Run data pipeline end-to-end
   - Validate output against test cases
   - Check coverage metrics (% institutions with earnings data)
   - Compare calculations against epanalysis test cases
   - Document any data quality issues

**Deliverables:**
- API client modules with tests
- `data/processed/roi_metrics.parquet` with ~6,000 institutions
- Updated `src/data/models.py` and `src/core/data_manager.py`
- Complete data governance documentation
- Data pipeline validation report

**Success Criteria:**
- Successfully fetch earnings data for 60%+ of institutions
- ROI calculations match expected formulas
- All tests pass
- Data pipeline runs in <5 minutes
- Zero data validation errors

---

### Phase 2: College Explorer ROI Tab (Weeks 3-4)

**Objective**: Add "Earnings & ROI" tab to College Explorer with institution-level ROI analysis

**Tasks:**

2.1 **Update constants and configuration** (Day 1)
   - Add `COLLEGE_ROI_LABEL` to `src/config/constants.py`
   - Update `COLLEGE_EXPLORER_CHARTS` list
   - Export new constants in `src/config/__init__.py`
   - Update `NavigationConfig` in `src/config/navigation.py`

2.2 **Extend College Explorer section** (Days 2-4)
   - Modify `src/sections/college_explorer.py`:
     ```python
     def render_chart(self, chart_name: str) -> None:
         """Render specific chart based on selection."""
         if chart_name == COLLEGE_SUMMARY_LABEL:
             self._render_summary_tab()
         elif chart_name == COLLEGE_LOANS_PELL_LABEL:
             self._render_federal_aid_tab()
         elif chart_name == COLLEGE_GRAD_RATES_LABEL:
             self._render_graduation_rates_tab()
         elif chart_name == COLLEGE_ROI_LABEL:
             self._render_roi_tab()  # NEW
         else:
             st.error(f"Unknown chart: {chart_name}")

     def _render_roi_tab(self) -> None:
         """Render Earnings & ROI analysis tab."""
         selected_institution = self._get_selected_institution()
         if not selected_institution:
             st.warning("Please select an institution from the dropdown above.")
             return

         unitid = selected_institution['UnitID']
         roi_data = self.data_manager.get_institution_roi(unitid)

         if not roi_data or not roi_data.get('has_earnings_data'):
             st.info("Earnings data not available for this institution.")
             return

         self._render_earnings_overview(roi_data)
         st.divider()
         self._render_roi_metrics(roi_data)
         st.divider()
         self._render_earnings_comparison(roi_data)
     ```

2.3 **Create ROI visualization components** (Days 5-7)
   - Earnings overview metrics display:
     ```python
     def _render_earnings_overview(self, roi_data: Dict) -> None:
         """Display earnings metrics with visual indicators."""
         st.markdown("### Post-Graduation Earnings")

         col1, col2, col3 = st.columns(3)

         with col1:
             st.metric(
                 label="Median Earnings (6 years)",
                 value=f"${roi_data['median_earnings_6yr']:,.0f}",
             )

         with col2:
             st.metric(
                 label="Median Earnings (8 years)",
                 value=f"${roi_data['median_earnings_8yr']:,.0f}",
             )

         with col3:
             st.metric(
                 label="Median Earnings (10 years)",
                 value=f"${roi_data['median_earnings_10yr']:,.0f}",
             )

         st.caption(f"Based on {roi_data['earnings_count_10yr']:,} students who entered 10 years ago")
     ```

   - ROI metrics with visual comparisons:
     ```python
     def _render_roi_metrics(self, roi_data: Dict) -> None:
         """Display ROI calculations."""
         st.markdown("### Return on Investment Analysis")

         col1, col2 = st.columns(2)

         with col1:
             st.markdown("#### State Baseline Comparison")
             st.metric(
                 label="High School Baseline (State)",
                 value=f"${roi_data['hs_baseline_state']:,.0f}",
             )
             st.metric(
                 label="Earnings Premium",
                 value=f"${roi_data['earnings_premium_state']:,.0f}",
                 delta=f"{(roi_data['earnings_premium_state']/roi_data['hs_baseline_state']*100):.0f}% above HS grads"
             )

             if roi_data['roi_years_state'] < 999:
                 years = int(roi_data['roi_years_state'])
                 months = int(roi_data['roi_months_state']) % 12
                 st.metric(
                     label="Years to Recoup Investment",
                     value=f"{years} years, {months} months"
                 )
             else:
                 st.warning("Negative earnings premium - investment may not recoup")

         with col2:
             if roi_data.get('hs_baseline_county'):
                 st.markdown("#### County Baseline Comparison")
                 st.metric(
                     label="High School Baseline (County)",
                     value=f"${roi_data['hs_baseline_county']:,.0f}",
                 )
                 st.metric(
                     label="Earnings Premium",
                     value=f"${roi_data['earnings_premium_county']:,.0f}",
                 )
                 # ... similar ROI display
     ```

   - Comparison chart (earnings vs. cost with sector context):
     ```python
     def _render_earnings_comparison(self, roi_data: Dict) -> None:
         """Show how this institution compares to peers."""
         st.markdown("### Peer Comparison")

         # Get peer institutions (same sector and level)
         roi_df = self.data_manager.get_roi_metrics()
         peers = roi_df[
             (roi_df['sector'] == roi_data['sector']) &
             (roi_df['level'] == roi_data['level']) &
             (roi_df['has_earnings_data'])
         ]

         # Highlight this institution
         peers['is_selected'] = peers['UnitID'] == roi_data['UnitID']

         # Create scatter chart
         chart = alt.Chart(peers).mark_circle(size=100).encode(
             x=alt.X('annual_net_price:Q', title='Annual Net Price', scale=alt.Scale(zero=False)),
             y=alt.Y('median_earnings_10yr:Q', title='Median Earnings (10 years)', scale=alt.Scale(zero=False)),
             color=alt.condition(
                 alt.datum.is_selected,
                 alt.value('red'),
                 alt.value('lightgray')
             ),
             size=alt.condition(
                 alt.datum.is_selected,
                 alt.value(300),
                 alt.value(50)
             ),
             tooltip=['institution', 'annual_net_price', 'median_earnings_10yr', 'roi_years_state']
         )

         st.altair_chart(chart, use_container_width=True)
     ```

2.4 **Update College Explorer overview** (Day 8)
   - Add ROI description to overview page
   - Update "Three Ways to Explore" to "Four Ways to Explore"
   - Add bordered box for ROI analysis feature

2.5 **Testing and refinement** (Days 9-10)
   - Test with various institutions (with/without earnings data)
   - Verify calculations displayed correctly
   - Ensure graceful handling of missing data
   - Test responsiveness and layout
   - Gather feedback and iterate

**Deliverables:**
- Enhanced College Explorer with functional ROI tab
- ROI visualization components
- Updated documentation
- Test coverage for new components

**Success Criteria:**
- ROI tab displays correctly for institutions with earnings data
- Graceful degradation for institutions without earnings
- All calculations accurate
- UI consistent with existing College Explorer design
- Load time <2 seconds for ROI tab

---

### Phase 3: Aggregate ROI Section (Weeks 5-6)

**Objective**: Create standalone ROI section with cross-institutional analyses

**Tasks:**

3.1 **Design aggregate datasets** (Days 1-2)
   - Create `data/processed/roi_top_institutions.parquet`:
     - Top 25 institutions by ROI (4-year and 2-year separately)
     - Includes institution details, ROI metrics, sector
   - Create `data/processed/roi_by_sector.parquet`:
     - Aggregate statistics by sector and level
     - Mean, median, quartiles for ROI and earnings premium
   - Update `src/data/build_roi_metrics.py` to generate these datasets

3.2 **Implement ROI section** (Days 3-5)
   - Rewrite `src/sections/roi.py`:
     ```python
     class ROISection(BaseSection):
         """Handles the aggregate ROI analysis section."""

         def __init__(self, data_manager: DataManager):
             super().__init__(data_manager)
             self.roi_df = data_manager.get_roi_metrics()

         def render_overview(self) -> None:
             """Render ROI overview with methodology explanation."""
             self.render_section_header("ROI Analysis", "Overview")

             st.title("Return on Investment: Higher Education Value Analysis")

             st.info("**💡 Key Insight:** ROI analysis measures how long it takes for graduates' enhanced earnings to recover their educational investment, providing a comprehensive value metric beyond cost and completion alone.")

             # Methodology explanation
             # Data sources description
             # Key findings from aggregate data

         def render_chart(self, chart_name: str) -> None:
             """Render specific ROI chart."""
             if chart_name == ROI_QUADRANT_LABEL:
                 self._render_quadrant_analysis()
             elif chart_name == ROI_TOP_INSTITUTIONS_LABEL:
                 self._render_top_roi_institutions()
             elif chart_name == ROI_BY_SECTOR_LABEL:
                 self._render_sector_analysis()
             else:
                 st.error(f"Unknown chart: {chart_name}")

         def get_available_charts(self) -> List[str]:
             return ROI_CHARTS
     ```

3.3 **Create ROI chart modules** (Days 6-8)
   - `src/charts/roi_quadrant_chart.py`:
     - Scatter plot with median reference lines
     - Four quadrants: High ROI, Premium, Poor ROI, Budget
     - Color by sector, size by enrollment
     - Interactive tooltips with institution details

   - `src/charts/roi_rankings_chart.py`:
     - Horizontal bar chart of top 25 institutions by ROI
     - Separate charts for 4-year and 2-year (tab pattern)
     - Show years to recoup with color gradient
     - Include earnings premium and net price in tooltip

   - `src/charts/roi_sector_distribution_chart.py`:
     - Box plot showing ROI distribution by sector
     - Overlay with mean and median markers
     - Separate by level (4-year vs 2-year)
     - Summary statistics table below chart

3.4 **Implement chart rendering methods** (Days 9-10)
   - Complete all `_render_*` methods in ROISection
   - Implement tab-based pattern for 4-year/2-year splits
   - Add filtering options (sector, state, enrollment range)
   - Include download buttons for processed data

3.5 **Testing and documentation** (Days 11-12)
   - Comprehensive testing of all ROI charts
   - Verify data accuracy and visual correctness
   - Update user documentation
   - Create methodology guide for ROI calculations
   - Performance optimization (caching, data loading)

**Deliverables:**
- Complete ROI section with 3 main chart types
- ROI chart modules (`src/charts/roi_*.py`)
- Aggregate ROI datasets
- Methodology documentation
- User guide for ROI analysis

**Success Criteria:**
- All ROI charts render correctly
- Data calculations accurate
- Performance <3 seconds per chart
- Filtering and interactivity work smoothly
- Clear methodology documentation

---

### Phase 4: Testing, Validation, and Documentation (Week 7)

**Objective**: Comprehensive testing, validation, and documentation before launch

**Tasks:**

4.1 **Data validation and quality assurance** (Days 1-2)
   - Validate ROI metrics against epanalysis test cases
   - Spot-check calculations for sample institutions
   - Verify data coverage (earnings data availability)
   - Compare our IPEDS cost data vs. College Scorecard cost data
   - Document any discrepancies and resolution
   - Create data quality report

4.2 **User acceptance testing** (Days 3-4)
   - Test all ROI features with real user scenarios:
     - Student exploring college options
     - Researcher comparing institutional value
     - Policymaker analyzing ROI by sector
   - Identify usability issues and edge cases
   - Test with various browsers and screen sizes
   - Verify accessibility (screen reader compatibility)

4.3 **Performance optimization** (Day 5)
   - Profile data loading and chart rendering
   - Optimize Parquet queries
   - Ensure proper `@st.cache_data` usage
   - Reduce unnecessary data loads
   - Target: <2 second load time for all ROI features

4.4 **Documentation updates** (Days 6-7)
   - Update `CLAUDE.md` with ROI feature details
   - Update `LOG.md` with implementation timeline
   - Create `docs/ROI_METHODOLOGY.md` with detailed calculations
   - Update `README.md` with ROI feature description
   - Document API key setup in `.env.example`
   - Update data dictionary with all ROI fields

4.5 **Final integration testing** (Days 8-9)
   - Test navigation between sections
   - Verify session state management
   - Test data pipeline from raw to visualization
   - Ensure backward compatibility with existing features
   - Run full test suite
   - Fix any bugs discovered

4.6 **Launch preparation** (Day 10)
   - Create release notes for ROI feature
   - Prepare demo script for stakeholders
   - Set up monitoring and logging
   - Document known limitations
   - Create user FAQ

**Deliverables:**
- Data validation report
- User testing report
- Performance optimization report
- Complete documentation suite
- Release notes
- Bug-free, production-ready ROI feature

**Success Criteria:**
- All tests pass
- No critical bugs
- Performance meets targets
- Documentation complete
- Ready for production deployment

---

## 5. Technical Specifications

### 5.1 Data Model Enhancements

**New Model: `src/data/models.py` additions**

```python
from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum

class AwardLevel(Enum):
    """Educational award levels."""
    FOUR_YEAR_PLUS = 1
    TWO_YEAR = 2
    LESS_THAN_TWO_YEAR = 3

class Sector(Enum):
    """Institution sectors."""
    PUBLIC = 1
    PRIVATE_NONPROFIT = 2
    PRIVATE_FOR_PROFIT = 3

@dataclass(frozen=True)
class EarningsData:
    """Post-graduation earnings data from College Scorecard."""
    median_earnings_6yr: Optional[float]
    median_earnings_8yr: Optional[float]
    median_earnings_10yr: Optional[float]
    earnings_count_10yr: Optional[int]

    def has_valid_data(self) -> bool:
        """Check if earnings data is present and valid."""
        return (
            self.median_earnings_10yr is not None and
            self.median_earnings_10yr > 0 and
            self.earnings_count_10yr is not None and
            self.earnings_count_10yr >= 30  # Privacy threshold
        )

@dataclass(frozen=True)
class BaselineEarnings:
    """High school graduate baseline earnings."""
    state_baseline: float
    county_baseline: Optional[float]
    geography_name: str

    def get_baseline(self, use_county: bool = False) -> float:
        """Get appropriate baseline earnings."""
        if use_county and self.county_baseline is not None:
            return self.county_baseline
        return self.state_baseline

@dataclass(frozen=True)
class ROIMetrics:
    """Calculated return on investment metrics."""
    # Input data
    total_program_cost: float
    median_earnings_10yr: float
    baseline_earnings: BaselineEarnings

    # Calculated premiums
    earnings_premium_state: float
    earnings_premium_county: Optional[float]

    # Calculated ROI
    roi_years_state: float
    roi_years_county: Optional[float]
    roi_months_state: int
    roi_months_county: Optional[int]

    # Validation flags
    has_positive_premium: bool
    is_valid_roi: bool

    @classmethod
    def calculate(
        cls,
        total_program_cost: float,
        median_earnings_10yr: float,
        baseline_earnings: BaselineEarnings
    ) -> 'ROIMetrics':
        """Calculate ROI metrics from input data."""
        # Calculate premiums
        earnings_premium_state = median_earnings_10yr - baseline_earnings.state_baseline
        earnings_premium_county = (
            median_earnings_10yr - baseline_earnings.county_baseline
            if baseline_earnings.county_baseline is not None
            else None
        )

        # Calculate ROI years
        if earnings_premium_state > 0:
            roi_years_state = total_program_cost / earnings_premium_state
            roi_months_state = int(roi_years_state * 12)
        else:
            roi_years_state = 999.0  # Flag for negative premium
            roi_months_state = 999 * 12

        if earnings_premium_county is not None and earnings_premium_county > 0:
            roi_years_county = total_program_cost / earnings_premium_county
            roi_months_county = int(roi_years_county * 12)
        else:
            roi_years_county = None
            roi_months_county = None

        has_positive_premium = earnings_premium_state > 0
        is_valid_roi = has_positive_premium and roi_years_state < 50  # Reasonable upper bound

        return cls(
            total_program_cost=total_program_cost,
            median_earnings_10yr=median_earnings_10yr,
            baseline_earnings=baseline_earnings,
            earnings_premium_state=earnings_premium_state,
            earnings_premium_county=earnings_premium_county,
            roi_years_state=roi_years_state,
            roi_years_county=roi_years_county,
            roi_months_state=roi_months_state,
            roi_months_county=roi_months_county,
            has_positive_premium=has_positive_premium,
            is_valid_roi=is_valid_roi,
        )

@dataclass(frozen=True)
class InstitutionROI:
    """Complete ROI profile for an institution."""
    # Identity
    unitid: int
    institution: str
    state: str
    sector: Sector
    level: AwardLevel

    # Existing metrics
    enrollment: Optional[int]
    graduation_rate: Optional[float]
    annual_net_price: Optional[float]

    # New earnings data
    earnings_data: Optional[EarningsData]
    baseline_earnings: Optional[BaselineEarnings]

    # Calculated ROI
    roi_metrics: Optional[ROIMetrics]

    def has_complete_data(self) -> bool:
        """Check if institution has all required data for ROI analysis."""
        return (
            self.earnings_data is not None and
            self.earnings_data.has_valid_data() and
            self.baseline_earnings is not None and
            self.roi_metrics is not None and
            self.roi_metrics.is_valid_roi
        )

    def get_summary_dict(self) -> Dict:
        """Get summary dictionary for display."""
        return {
            'UnitID': self.unitid,
            'Institution': self.institution,
            'State': self.state,
            'Sector': self.sector.name,
            'Level': self.level.name,
            'Enrollment': self.enrollment,
            'Graduation Rate': self.graduation_rate,
            'Annual Net Price': self.annual_net_price,
            'Median Earnings (10yr)': self.earnings_data.median_earnings_10yr if self.earnings_data else None,
            'Earnings Premium': self.roi_metrics.earnings_premium_state if self.roi_metrics else None,
            'ROI (years)': self.roi_metrics.roi_years_state if self.roi_metrics else None,
            'Has Complete Data': self.has_complete_data(),
        }
```

### 5.2 Chart Module Specifications

**`src/charts/roi_quadrant_chart.py`**

```python
"""ROI Quadrant Chart: Cost vs Earnings scatter plot with median reference lines."""

from typing import Optional
import pandas as pd
import altair as alt
import streamlit as st

def create_roi_quadrant_chart(
    df: pd.DataFrame,
    level_filter: Optional[int] = None,
    sector_filter: Optional[str] = None,
    highlight_unitid: Optional[int] = None
) -> alt.Chart:
    """
    Create quadrant scatter plot showing cost vs earnings with ROI context.

    Args:
        df: DataFrame with ROI metrics
        level_filter: Filter by level (1=4-year, 2=2-year)
        sector_filter: Filter by sector name
        highlight_unitid: UnitID to highlight in red

    Returns:
        Altair chart object
    """
    # Filter data
    plot_df = df[df['has_earnings_data']].copy()

    if level_filter:
        plot_df = plot_df[plot_df['level'] == level_filter]

    if sector_filter:
        plot_df = plot_df[plot_df['sector_name'] == sector_filter]

    # Calculate medians for reference lines
    median_price = plot_df['annual_net_price'].median()
    median_earnings = plot_df['median_earnings_10yr'].median()

    # Add highlight flag
    if highlight_unitid:
        plot_df['is_highlighted'] = plot_df['UnitID'] == highlight_unitid
    else:
        plot_df['is_highlighted'] = False

    # Base scatter plot
    scatter = alt.Chart(plot_df).mark_circle().encode(
        x=alt.X(
            'annual_net_price:Q',
            title='Annual Net Price ($)',
            scale=alt.Scale(zero=False, padding=10)
        ),
        y=alt.Y(
            'median_earnings_10yr:Q',
            title='Median Earnings 10 Years After Entry ($)',
            scale=alt.Scale(zero=False, padding=10)
        ),
        color=alt.condition(
            alt.datum.is_highlighted,
            alt.value('#e74c3c'),  # Red for highlighted
            alt.Color('sector_name:N', legend=alt.Legend(title='Sector'))
        ),
        size=alt.condition(
            alt.datum.is_highlighted,
            alt.value(300),
            alt.Size('enrollment:Q', scale=alt.Scale(range=[50, 500]), legend=None)
        ),
        opacity=alt.condition(
            alt.datum.is_highlighted,
            alt.value(1.0),
            alt.value(0.6)
        ),
        tooltip=[
            alt.Tooltip('institution:N', title='Institution'),
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('sector_name:N', title='Sector'),
            alt.Tooltip('annual_net_price:Q', title='Annual Net Price', format='$,.0f'),
            alt.Tooltip('median_earnings_10yr:Q', title='Median Earnings', format='$,.0f'),
            alt.Tooltip('earnings_premium_state:Q', title='Earnings Premium', format='$,.0f'),
            alt.Tooltip('roi_years_state:Q', title='ROI (years)', format='.1f'),
            alt.Tooltip('graduation_rate:Q', title='Graduation Rate', format='.1%'),
        ]
    ).properties(
        width=700,
        height=520,
        title={
            "text": "Cost vs Earnings: ROI Quadrants",
            "subtitle": "Circle size represents enrollment. Hover for details."
        }
    )

    # Vertical median line (price)
    vline = alt.Chart(pd.DataFrame({'x': [median_price]})).mark_rule(
        strokeDash=[5, 5],
        color='gray',
        size=2
    ).encode(
        x='x:Q'
    )

    # Horizontal median line (earnings)
    hline = alt.Chart(pd.DataFrame({'y': [median_earnings]})).mark_rule(
        strokeDash=[5, 5],
        color='gray',
        size=2
    ).encode(
        y='y:Q'
    )

    # Quadrant labels
    quadrant_data = pd.DataFrame([
        {'x': median_price * 1.3, 'y': median_earnings * 1.15, 'label': 'High Cost, High Earnings', 'color': '#3498db'},
        {'x': median_price * 0.7, 'y': median_earnings * 1.15, 'label': 'Low Cost, High Earnings (Best ROI)', 'color': '#2ecc71'},
        {'x': median_price * 0.7, 'y': median_earnings * 0.85, 'label': 'Low Cost, Low Earnings', 'color': '#95a5a6'},
        {'x': median_price * 1.3, 'y': median_earnings * 0.85, 'label': 'High Cost, Low Earnings (Poor ROI)', 'color': '#e74c3c'},
    ])

    labels = alt.Chart(quadrant_data).mark_text(
        fontSize=11,
        fontStyle='italic',
        fontWeight='bold',
        opacity=0.5
    ).encode(
        x='x:Q',
        y='y:Q',
        text='label:N',
        color=alt.Color('color:N', scale=None)
    )

    # Combine layers
    chart = (scatter + vline + hline + labels).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_legend(
        titleFontSize=12,
        labelFontSize=11
    )

    return chart

def render_roi_quadrant_chart(df: pd.DataFrame, level_name: str) -> None:
    """
    Render ROI quadrant chart with Streamlit wrapper.

    Args:
        df: ROI metrics DataFrame
        level_name: "4-year" or "2-year"
    """
    level_map = {"4-year": 1, "2-year": 2}
    level_filter = level_map.get(level_name)

    st.markdown(f"### Cost vs Earnings: {level_name} Institutions")

    # Filter options
    col1, col2 = st.columns([3, 1])

    with col1:
        sectors = ['All'] + sorted(df['sector_name'].dropna().unique().tolist())
        sector_filter = st.selectbox(
            "Filter by Sector:",
            sectors,
            key=f"roi_quadrant_sector_{level_name}"
        )

    sector_filter = None if sector_filter == 'All' else sector_filter

    # Create and render chart
    chart = create_roi_quadrant_chart(df, level_filter, sector_filter)
    st.altair_chart(chart, use_container_width=True)

    # Interpretation guide
    with st.expander("How to Read This Chart"):
        st.markdown("""
        **Quadrant Interpretation:**

        - **Top Left (Green)**: Low cost, high earnings - **Best ROI**
        - **Top Right (Blue)**: High cost, high earnings - Premium institutions
        - **Bottom Left (Gray)**: Low cost, low earnings - Budget options
        - **Bottom Right (Red)**: High cost, low earnings - **Poor ROI**

        **Median Lines**: Gray dashed lines show the median cost and earnings across all institutions.

        **Circle Size**: Larger circles represent higher enrollment.
        """)
```

**`src/charts/roi_rankings_chart.py`**

```python
"""ROI Rankings Chart: Top institutions by years to recoup investment."""

from typing import Literal
import pandas as pd
import altair as alt
import streamlit as st

def create_roi_rankings_chart(
    df: pd.DataFrame,
    level_filter: int,
    top_n: int = 25,
    sort_order: Literal['best', 'worst'] = 'best'
) -> alt.Chart:
    """
    Create horizontal bar chart of institutions ranked by ROI.

    Args:
        df: DataFrame with ROI metrics
        level_filter: 1 for 4-year, 2 for 2-year
        top_n: Number of institutions to show
        sort_order: 'best' for shortest ROI, 'worst' for longest ROI

    Returns:
        Altair chart object
    """
    # Filter and prepare data
    plot_df = df[
        (df['level'] == level_filter) &
        (df['has_earnings_data']) &
        (df['roi_years_state'] < 999)  # Exclude negative premiums
    ].copy()

    # Sort
    ascending = (sort_order == 'best')
    plot_df = plot_df.sort_values('roi_years_state', ascending=ascending).head(top_n)

    # Create display name with ranking
    plot_df['rank'] = range(1, len(plot_df) + 1)
    plot_df['display_name'] = plot_df['rank'].astype(str) + '. ' + plot_df['institution']

    # Color scale (green for good ROI, red for poor ROI)
    color_scale = alt.Scale(
        domain=[0, 5, 10, 15, 20],
        range=['#2ecc71', '#27ae60', '#f39c12', '#e67e22', '#e74c3c']
    )

    # Create chart
    chart = alt.Chart(plot_df).mark_bar().encode(
        x=alt.X(
            'roi_years_state:Q',
            title='Years to Recoup Investment',
            scale=alt.Scale(domain=[0, plot_df['roi_years_state'].max() * 1.1])
        ),
        y=alt.Y(
            'display_name:N',
            title=None,
            sort=alt.EncodingSortField(field='roi_years_state', order='ascending' if ascending else 'descending')
        ),
        color=alt.Color(
            'roi_years_state:Q',
            scale=color_scale,
            legend=None
        ),
        tooltip=[
            alt.Tooltip('rank:O', title='Rank'),
            alt.Tooltip('institution:N', title='Institution'),
            alt.Tooltip('state:N', title='State'),
            alt.Tooltip('sector_name:N', title='Sector'),
            alt.Tooltip('roi_years_state:Q', title='ROI (years)', format='.1f'),
            alt.Tooltip('roi_months_state:Q', title='ROI (months)', format='d'),
            alt.Tooltip('median_earnings_10yr:Q', title='Median Earnings', format='$,.0f'),
            alt.Tooltip('earnings_premium_state:Q', title='Earnings Premium', format='$,.0f'),
            alt.Tooltip('total_program_cost:Q', title='Total Program Cost', format='$,.0f'),
            alt.Tooltip('graduation_rate:Q', title='Graduation Rate', format='.1%'),
        ]
    ).properties(
        width=700,
        height=max(400, top_n * 20),
        title={
            "text": f"Top {top_n} Institutions by ROI ({'Shortest' if ascending else 'Longest'} Time to Recoup)",
            "subtitle": "Lower values indicate faster return on investment"
        }
    )

    # Add value labels
    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        fontSize=10,
        fontWeight='bold'
    ).encode(
        text=alt.Text('roi_years_state:Q', format='.1f'),
        color=alt.value('black')
    )

    combined = (chart + text).configure_axis(
        labelFontSize=10,
        titleFontSize=12
    )

    return combined

def render_roi_rankings_chart_with_tabs(df: pd.DataFrame) -> None:
    """
    Render ROI rankings with 4-year/2-year tabs.

    Args:
        df: ROI metrics DataFrame
    """
    st.markdown("### Top Institutions by Return on Investment")

    # Options
    col1, col2 = st.columns([2, 2])

    with col1:
        sort_order = st.radio(
            "Show institutions with:",
            options=['best', 'worst'],
            format_func=lambda x: 'Best ROI (shortest time to recoup)' if x == 'best' else 'Worst ROI (longest time to recoup)',
            horizontal=True,
            key='roi_rankings_sort'
        )

    with col2:
        top_n = st.slider(
            "Number of institutions:",
            min_value=10,
            max_value=50,
            value=25,
            step=5,
            key='roi_rankings_topn'
        )

    # Tabs
    tab1, tab2 = st.tabs(["4-year", "2-year"])

    with tab1:
        chart_4yr = create_roi_rankings_chart(df, level_filter=1, top_n=top_n, sort_order=sort_order)
        st.altair_chart(chart_4yr, use_container_width=True)

    with tab2:
        chart_2yr = create_roi_rankings_chart(df, level_filter=2, top_n=top_n, sort_order=sort_order)
        st.altair_chart(chart_2yr, use_container_width=True)

    # Summary statistics
    st.markdown("#### Key Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**4-Year Institutions**")
        df_4yr = df[(df['level'] == 1) & (df['has_earnings_data']) & (df['roi_years_state'] < 999)]
        if not df_4yr.empty:
            st.metric("Median ROI", f"{df_4yr['roi_years_state'].median():.1f} years")
            st.metric("Best ROI", f"{df_4yr['roi_years_state'].min():.1f} years")
            st.metric("Median Earnings Premium", f"${df_4yr['earnings_premium_state'].median():,.0f}")

    with col2:
        st.markdown("**2-Year Institutions**")
        df_2yr = df[(df['level'] == 2) & (df['has_earnings_data']) & (df['roi_years_state'] < 999)]
        if not df_2yr.empty:
            st.metric("Median ROI", f"{df_2yr['roi_years_state'].median():.1f} years")
            st.metric("Best ROI", f"{df_2yr['roi_years_state'].min():.1f} years")
            st.metric("Median Earnings Premium", f"${df_2yr['earnings_premium_state'].median():,.0f}")
```

### 5.3 Data Loading Enhancements

**`src/core/data_manager.py` additions:**

```python
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
import streamlit as st

from src.config.data_sources import (
    ROI_METRICS_PATH,
    ROI_BY_SECTOR_PATH,
    ROI_TOP_INSTITUTIONS_PATH,
)

class DataManager:
    """Enhanced DataManager with ROI data support."""

    # ... existing methods ...

    @st.cache_data(ttl=3600)
    def get_roi_metrics(_self) -> pd.DataFrame:
        """
        Load ROI metrics dataset with earnings and calculated ROI.

        Returns:
            DataFrame with institution-level ROI metrics
        """
        try:
            df = pd.read_parquet(ROI_METRICS_PATH)
            _self._logger.info(f"Loaded ROI metrics: {len(df)} institutions")
            return df
        except FileNotFoundError:
            _self._logger.error(f"ROI metrics not found at {ROI_METRICS_PATH}")
            return pd.DataFrame()
        except Exception as e:
            _self._logger.error(f"Error loading ROI metrics: {e}")
            return pd.DataFrame()

    def get_institution_roi(self, unitid: int) -> Optional[Dict]:
        """
        Get ROI metrics for a specific institution.

        Args:
            unitid: Institution UnitID

        Returns:
            Dictionary with ROI metrics, or None if not found
        """
        roi_df = self.get_roi_metrics()

        if roi_df.empty:
            return None

        institution_roi = roi_df[roi_df['UnitID'] == unitid]

        if institution_roi.empty:
            return None

        return institution_roi.iloc[0].to_dict()

    @st.cache_data(ttl=3600)
    def get_roi_by_sector(_self) -> pd.DataFrame:
        """
        Load aggregate ROI statistics by sector and level.

        Returns:
            DataFrame with sector-level statistics
        """
        try:
            df = pd.read_parquet(ROI_BY_SECTOR_PATH)
            return df
        except FileNotFoundError:
            _self._logger.warning(f"ROI by sector data not found at {ROI_BY_SECTOR_PATH}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_roi_top_institutions(_self, top_n: int = 25) -> pd.DataFrame:
        """
        Load top institutions by ROI.

        Args:
            top_n: Number of top institutions to load

        Returns:
            DataFrame with top ROI institutions
        """
        try:
            df = pd.read_parquet(ROI_TOP_INSTITUTIONS_PATH)
            return df.head(top_n)
        except FileNotFoundError:
            # Fallback: calculate from full ROI metrics
            roi_df = _self.get_roi_metrics()
            if not roi_df.empty:
                return roi_df[
                    (roi_df['has_earnings_data']) &
                    (roi_df['roi_years_state'] < 999)
                ].nsmallest(top_n, 'roi_years_state')
            return pd.DataFrame()
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Test Suite: `tests/test_roi_calculations.py`**

```python
"""Unit tests for ROI calculation logic."""

import pytest
import pandas as pd
from src.data.models import ROIMetrics, BaselineEarnings, EarningsData

class TestROICalculations:
    """Test ROI calculation methods."""

    def test_positive_premium_roi(self):
        """Test ROI calculation with positive earnings premium."""
        baseline = BaselineEarnings(
            state_baseline=30000,
            county_baseline=28000,
            geography_name="Test State"
        )

        roi = ROIMetrics.calculate(
            total_program_cost=40000,
            median_earnings_10yr=50000,
            baseline_earnings=baseline
        )

        # Earnings premium: 50000 - 30000 = 20000
        # ROI years: 40000 / 20000 = 2.0 years
        assert roi.earnings_premium_state == 20000
        assert roi.roi_years_state == 2.0
        assert roi.roi_months_state == 24
        assert roi.has_positive_premium is True
        assert roi.is_valid_roi is True

    def test_negative_premium_roi(self):
        """Test ROI calculation with negative earnings premium (earnings below HS grads)."""
        baseline = BaselineEarnings(
            state_baseline=35000,
            county_baseline=None,
            geography_name="Test State"
        )

        roi = ROIMetrics.calculate(
            total_program_cost=40000,
            median_earnings_10yr=30000,  # Below baseline!
            baseline_earnings=baseline
        )

        assert roi.earnings_premium_state == -5000
        assert roi.roi_years_state == 999.0  # Flag value
        assert roi.has_positive_premium is False
        assert roi.is_valid_roi is False

    def test_zero_cost_roi(self):
        """Test ROI calculation with zero cost (scholarships)."""
        baseline = BaselineEarnings(
            state_baseline=30000,
            county_baseline=None,
            geography_name="Test State"
        )

        roi = ROIMetrics.calculate(
            total_program_cost=0,
            median_earnings_10yr=50000,
            baseline_earnings=baseline
        )

        assert roi.roi_years_state == 0.0
        assert roi.has_positive_premium is True

    def test_county_baseline_roi(self):
        """Test ROI calculation with county-level baseline."""
        baseline = BaselineEarnings(
            state_baseline=30000,
            county_baseline=25000,  # Lower cost of living county
            geography_name="Test County"
        )

        roi = ROIMetrics.calculate(
            total_program_cost=40000,
            median_earnings_10yr=50000,
            baseline_earnings=baseline
        )

        # State: (50000 - 30000) = 20000 premium, 40000/20000 = 2.0 years
        # County: (50000 - 25000) = 25000 premium, 40000/25000 = 1.6 years
        assert roi.roi_years_state == 2.0
        assert roi.roi_years_county == 1.6
        assert roi.earnings_premium_county == 25000

    def test_earnings_data_validation(self):
        """Test earnings data validity checks."""
        # Valid data (above privacy threshold)
        valid_earnings = EarningsData(
            median_earnings_6yr=35000,
            median_earnings_8yr=42000,
            median_earnings_10yr=50000,
            earnings_count_10yr=50
        )
        assert valid_earnings.has_valid_data() is True

        # Invalid: below privacy threshold
        invalid_count = EarningsData(
            median_earnings_6yr=35000,
            median_earnings_8yr=42000,
            median_earnings_10yr=50000,
            earnings_count_10yr=20  # Below 30
        )
        assert invalid_count.has_valid_data() is False

        # Invalid: missing earnings
        missing_earnings = EarningsData(
            median_earnings_6yr=None,
            median_earnings_8yr=None,
            median_earnings_10yr=None,
            earnings_count_10yr=50
        )
        assert missing_earnings.has_valid_data() is False

class TestDataPipelineIntegration:
    """Integration tests for ROI data pipeline."""

    @pytest.fixture
    def sample_institutions(self):
        """Sample institution data for testing."""
        return pd.DataFrame({
            'UnitID': [100654, 100663, 100690],
            'institution': ['University A', 'College B', 'Institute C'],
            'state': ['CA', 'CA', 'TX'],
            'fips': ['06037', '06073', '48201'],
            'sector': [1, 2, 3],
            'level': [1, 2, 1],
            'annual_net_price': [15000, 8000, 25000],
            'enrollment': [20000, 5000, 3000],
            'graduation_rate': [0.75, 0.40, 0.55],
        })

    @pytest.fixture
    def sample_earnings(self):
        """Sample earnings data from College Scorecard."""
        return pd.DataFrame({
            'UnitID': [100654, 100663],  # Note: 100690 missing (typical scenario)
            'median_earnings_10yr': [60000, 45000],
            'earnings_count_10yr': [500, 150],
        })

    @pytest.fixture
    def sample_baselines(self):
        """Sample high school baseline earnings."""
        return {
            'CA': {'state_baseline': 32000, 'county_baselines': {'06037': 34000, '06073': 30000}},
            'TX': {'state_baseline': 28000, 'county_baselines': {'48201': 29000}},
        }

    def test_data_merge(self, sample_institutions, sample_earnings, sample_baselines):
        """Test merging of institutions, earnings, and baselines."""
        # Simulate merge
        merged = sample_institutions.merge(sample_earnings, on='UnitID', how='left')

        # Check that all institutions preserved
        assert len(merged) == 3

        # Check that missing earnings are NaN
        assert pd.isna(merged.loc[merged['UnitID'] == 100690, 'median_earnings_10yr'].values[0])

        # Check that present earnings are correct
        assert merged.loc[merged['UnitID'] == 100654, 'median_earnings_10yr'].values[0] == 60000

    def test_roi_calculation_pipeline(self, sample_institutions, sample_earnings, sample_baselines):
        """Test end-to-end ROI calculation pipeline."""
        # Merge data
        df = sample_institutions.merge(sample_earnings, on='UnitID', how='left')

        # Add baselines
        df['hs_baseline_state'] = df['state'].map(lambda s: sample_baselines[s]['state_baseline'])

        # Calculate program cost
        df['years'] = df['level'].map({1: 4, 2: 2, 3: 2})
        df['total_program_cost'] = df['annual_net_price'] * df['years']

        # Calculate ROI
        df['earnings_premium_state'] = df['median_earnings_10yr'] - df['hs_baseline_state']
        df['roi_years_state'] = df.apply(
            lambda row: row['total_program_cost'] / row['earnings_premium_state']
                if pd.notna(row['earnings_premium_state']) and row['earnings_premium_state'] > 0
                else 999.0,
            axis=1
        )

        # Verify calculations
        # University A: 4-year, $15k/yr = $60k total, $60k earnings, $32k baseline
        # Premium: $28k, ROI: 60k/28k = 2.14 years
        uni_a = df[df['UnitID'] == 100654].iloc[0]
        assert abs(uni_a['roi_years_state'] - 2.14) < 0.01

        # College B: 2-year, $8k/yr = $16k total, $45k earnings, $32k baseline
        # Premium: $13k, ROI: 16k/13k = 1.23 years
        college_b = df[df['UnitID'] == 100663].iloc[0]
        assert abs(college_b['roi_years_state'] - 1.23) < 0.01

        # Institute C: Missing earnings data
        inst_c = df[df['UnitID'] == 100690].iloc[0]
        assert inst_c['roi_years_state'] == 999.0
```

### 6.2 Integration Tests

**Test Suite: `tests/test_roi_section.py`**

```python
"""Integration tests for ROI section rendering."""

import pytest
from unittest.mock import Mock, MagicMock
import pandas as pd
from src.sections.roi import ROISection
from src.sections.college_explorer import CollegeExplorerSection

@pytest.fixture
def mock_data_manager():
    """Mock DataManager with ROI data."""
    manager = Mock()

    # Mock ROI metrics
    manager.get_roi_metrics.return_value = pd.DataFrame({
        'UnitID': [100654, 100663, 100690],
        'institution': ['University A', 'College B', 'Institute C'],
        'state': ['CA', 'CA', 'TX'],
        'sector_name': ['Public', 'Private nonprofit', 'Private for-profit'],
        'level': [1, 2, 1],
        'annual_net_price': [15000, 8000, 25000],
        'median_earnings_10yr': [60000, 45000, 50000],
        'earnings_premium_state': [28000, 13000, 22000],
        'roi_years_state': [2.14, 1.23, 4.55],
        'roi_months_state': [26, 15, 55],
        'has_earnings_data': [True, True, True],
        'graduation_rate': [0.75, 0.40, 0.55],
        'enrollment': [20000, 5000, 3000],
    })

    # Mock institution ROI
    manager.get_institution_roi.return_value = {
        'UnitID': 100654,
        'institution': 'University A',
        'median_earnings_10yr': 60000,
        'earnings_premium_state': 28000,
        'roi_years_state': 2.14,
        'roi_months_state': 26,
        'has_earnings_data': True,
        'hs_baseline_state': 32000,
    }

    return manager

def test_roi_section_initialization(mock_data_manager):
    """Test ROI section initializes correctly."""
    section = ROISection(mock_data_manager)
    assert section.data_manager == mock_data_manager
    assert not section.roi_df.empty

def test_roi_section_available_charts(mock_data_manager):
    """Test ROI section returns correct chart list."""
    section = ROISection(mock_data_manager)
    charts = section.get_available_charts()

    assert 'Cost vs Earnings Quadrant' in charts
    assert 'Top 25 by ROI' in charts
    assert 'ROI by Sector & Level' in charts

def test_college_explorer_roi_tab(mock_data_manager):
    """Test College Explorer ROI tab integration."""
    # Add required mock data for College Explorer
    mock_data_manager.institutions_df = pd.DataFrame({
        'UnitID': [100654],
        'INSTITUTION': ['University A'],
    })
    mock_data_manager.get_distance_data.return_value = pd.DataFrame()
    mock_data_manager.pellgradrates_df = pd.DataFrame()

    section = CollegeExplorerSection(mock_data_manager)

    # Test that ROI chart is available
    charts = section.get_available_charts()
    assert 'Earnings & ROI' in charts

def test_roi_metrics_with_missing_data(mock_data_manager):
    """Test handling of institutions without earnings data."""
    # Override mock to include institution without earnings
    mock_data_manager.get_institution_roi.return_value = {
        'UnitID': 999999,
        'institution': 'No Earnings College',
        'has_earnings_data': False,
        'median_earnings_10yr': None,
    }

    roi_data = mock_data_manager.get_institution_roi(999999)

    assert roi_data['has_earnings_data'] is False
    assert roi_data['median_earnings_10yr'] is None
```

### 6.3 Data Validation Tests

**Test Suite: `tests/test_roi_data_quality.py`**

```python
"""Data quality tests for ROI datasets."""

import pytest
import pandas as pd
from pathlib import Path

ROI_METRICS_PATH = Path("data/processed/roi_metrics.parquet")

@pytest.mark.skipif(not ROI_METRICS_PATH.exists(), reason="ROI data not yet generated")
class TestROIDataQuality:
    """Test data quality of ROI datasets."""

    @pytest.fixture(scope='class')
    def roi_df(self):
        """Load ROI metrics for testing."""
        return pd.read_parquet(ROI_METRICS_PATH)

    def test_schema_completeness(self, roi_df):
        """Test that all required fields are present."""
        required_fields = [
            'UnitID', 'institution', 'state', 'sector', 'level',
            'annual_net_price', 'median_earnings_10yr', 'hs_baseline_state',
            'earnings_premium_state', 'roi_years_state', 'has_earnings_data'
        ]

        for field in required_fields:
            assert field in roi_df.columns, f"Missing required field: {field}"

    def test_unitid_uniqueness(self, roi_df):
        """Test that UnitID is unique."""
        assert roi_df['UnitID'].is_unique, "UnitID should be unique primary key"

    def test_earnings_coverage(self, roi_df):
        """Test that earnings data coverage is reasonable."""
        coverage = roi_df['has_earnings_data'].mean()

        assert coverage >= 0.50, f"Earnings coverage {coverage:.1%} is below 50%"
        assert coverage <= 0.90, f"Earnings coverage {coverage:.1%} is unexpectedly high"

        print(f"Earnings data coverage: {coverage:.1%} ({roi_df['has_earnings_data'].sum():,} institutions)")

    def test_earnings_value_ranges(self, roi_df):
        """Test that earnings values are within reasonable ranges."""
        earnings = roi_df[roi_df['has_earnings_data']]['median_earnings_10yr']

        assert earnings.min() >= 10000, "Minimum earnings too low"
        assert earnings.max() <= 200000, "Maximum earnings unexpectedly high"
        assert earnings.median() > 25000, "Median earnings too low"

    def test_net_price_ranges(self, roi_df):
        """Test that net price values are reasonable."""
        prices = roi_df['annual_net_price'].dropna()

        assert prices.min() >= 0, "Negative net price found"
        assert prices.max() <= 80000, "Net price unexpectedly high"

    def test_roi_calculation_consistency(self, roi_df):
        """Test that ROI calculations are mathematically consistent."""
        # For institutions with earnings data and positive premium
        valid_roi = roi_df[
            (roi_df['has_earnings_data']) &
            (roi_df['earnings_premium_state'] > 0)
        ].copy()

        # Recalculate ROI and compare
        valid_roi['recalc_roi'] = valid_roi['total_program_cost'] / valid_roi['earnings_premium_state']

        # Allow small floating point differences
        diff = (valid_roi['roi_years_state'] - valid_roi['recalc_roi']).abs()

        assert (diff < 0.01).all(), "ROI calculations inconsistent with source data"

    def test_negative_premium_handling(self, roi_df):
        """Test that negative premiums are flagged correctly."""
        negative_premium = roi_df[roi_df['earnings_premium_state'] < 0]

        # All negative premiums should have ROI = 999
        assert (negative_premium['roi_years_state'] == 999.0).all(), "Negative premiums not properly flagged"

    def test_baseline_coverage(self, roi_df):
        """Test that baseline earnings are populated."""
        assert roi_df['hs_baseline_state'].notna().all(), "Missing state baseline data"

        # Baselines should be reasonable
        baselines = roi_df['hs_baseline_state'].unique()
        assert baselines.min() >= 20000, "Baseline earnings too low"
        assert baselines.max() <= 50000, "Baseline earnings too high"

    def test_sector_distribution(self, roi_df):
        """Test that data covers all sectors."""
        sectors = roi_df['sector'].unique()

        assert 1 in sectors, "Missing public institutions"
        assert 2 in sectors, "Missing private nonprofit institutions"
        assert 3 in sectors, "Missing private for-profit institutions"

    def test_level_distribution(self, roi_df):
        """Test that data covers different institution levels."""
        levels = roi_df['level'].unique()

        assert 1 in levels, "Missing 4-year institutions"
        assert 2 in levels, "Missing 2-year institutions"
```

### 6.4 End-to-End User Acceptance Tests

**Manual Test Plan:**

**Test Case 1: College Explorer ROI Tab**
1. Navigate to College Explorer section
2. Select an institution with earnings data (e.g., "University of California-Berkeley")
3. Click on "Earnings & ROI" tab
4. **Verify**:
   - Earnings metrics display (6yr, 8yr, 10yr)
   - ROI calculation shown with years and months
   - Earnings premium calculated correctly
   - Peer comparison chart loads
   - Institution is highlighted in comparison chart
   - Tooltips work on all interactive elements

**Test Case 2: College Explorer - Missing Earnings Data**
1. Navigate to College Explorer section
2. Select an institution without earnings data (e.g., small institution)
3. Click on "Earnings & ROI" tab
4. **Verify**:
   - Friendly message displayed: "Earnings data not available for this institution"
   - No error messages or broken charts
   - User can navigate back to other tabs

**Test Case 3: ROI Section - Quadrant Analysis**
1. Navigate to ROI Analysis section
2. Select "Cost vs Earnings Quadrant" chart
3. Toggle between "4-year" and "2-year" tabs
4. Use sector filter dropdown
5. **Verify**:
   - Chart renders quickly (<2 seconds)
   - Median reference lines displayed
   - Quadrant labels visible
   - Tooltips show all metrics
   - Sector filtering works correctly
   - Chart updates when switching tabs

**Test Case 4: ROI Section - Top Rankings**
1. Navigate to ROI Analysis section
2. Select "Top 25 by ROI" chart
3. Toggle "Best ROI" vs "Worst ROI" radio buttons
4. Adjust slider for number of institutions
5. **Verify**:
   - Bar chart renders with correct institutions
   - Ranking numbers displayed (1, 2, 3...)
   - Color gradient reflects ROI quality
   - Value labels show years to recoup
   - Tooltips show comprehensive metrics
   - Chart updates smoothly when changing options

**Test Case 5: Performance**
1. Navigate through all ROI features
2. **Measure**:
   - Initial data load time (<5 seconds)
   - Chart rendering time (<2 seconds)
   - Tab switching responsiveness (<1 second)
   - Filter/interaction responsiveness (<1 second)
3. **Verify**:
   - No lag or freezing
   - Smooth transitions
   - Data cached appropriately (second visit faster)

**Test Case 6: Data Accuracy**
1. Select institution with known data (e.g., from College Scorecard website)
2. **Verify**:
   - Median earnings matches College Scorecard
   - Net price matches IPEDS data
   - ROI calculation: cost / (earnings - baseline) matches manual calculation
   - Graduation rate consistent with other sections

**Test Case 7: Edge Cases**
1. Test with institution that has:
   - Very high cost, low earnings (poor ROI)
   - Very low cost, high earnings (excellent ROI)
   - Earnings below high school baseline (negative premium)
   - Zero enrollment
   - Missing graduation rate
2. **Verify**:
   - All cases handled gracefully
   - No errors or crashes
   - Appropriate messaging for edge cases

---

## 7. Risks and Mitigation Strategies

### 7.1 Technical Risks

**Risk 1: College Scorecard API Availability and Limits**
- **Probability**: Medium
- **Impact**: High (blocks data acquisition)
- **Mitigation**:
  - Register for API key early in Phase 1
  - Implement caching and rate limiting in API client
  - Download and cache full dataset rather than real-time API calls
  - Fallback: Use downloadable CSV files from College Scorecard website
  - Monitor API status and have backup download URLs

**Risk 2: Data Coverage Gaps**
- **Probability**: High (inherent in College Scorecard data)
- **Impact**: Medium (reduces analysis scope)
- **Context**: Only 60-70% of institutions have earnings data due to privacy suppression
- **Mitigation**:
  - Design UI to gracefully handle missing data
  - Provide clear messaging about data availability
  - Focus analysis on institutions with complete data
  - Document coverage limitations in methodology
  - Consider supplemental earnings data sources (e.g., state workforce data)

**Risk 3: Data Synchronization Complexity**
- **Probability**: Medium
- **Impact**: Medium (data quality issues)
- **Context**: Matching institutions across IPEDS, College Scorecard, and Census data
- **Mitigation**:
  - Use UnitID as primary join key (standard across IPEDS and Scorecard)
  - Implement fuzzy matching for institution names as backup
  - Validate merge results with test cases
  - Document any institutions that can't be matched
  - Manual review of merge results for top institutions

**Risk 4: Calculation Errors**
- **Probability**: Low (with proper testing)
- **Impact**: High (incorrect analysis undermines credibility)
- **Mitigation**:
  - Comprehensive unit tests for all ROI formulas
  - Validate against epanalysis test cases
  - Manual spot-checks of calculated values
  - Compare our calculations with published College Scorecard ROI metrics (if available)
  - Peer review of calculation logic

**Risk 5: Performance Degradation**
- **Probability**: Low
- **Impact**: Medium (poor user experience)
- **Context**: Adding large earnings dataset and complex calculations
- **Mitigation**:
  - Pre-calculate ROI metrics in data pipeline (don't calculate on-the-fly)
  - Use Parquet format with Snappy compression
  - Implement proper `@st.cache_data` decorators
  - Load only necessary columns for specific visualizations
  - Profile and optimize bottlenecks

### 7.2 Data Quality Risks

**Risk 6: Earnings Data Staleness**
- **Probability**: High (inherent lag in earnings data)
- **Impact**: Low to Medium
- **Context**: 10-year earnings data is from 2009-10 entry cohorts (now 15+ years old)
- **Mitigation**:
  - Clearly document data vintage in UI
  - Update annually when new College Scorecard data released
  - Consider using 6-year or 8-year earnings for more recent data
  - Acknowledge limitations in methodology documentation
  - Plan for future enhancements with more recent data

**Risk 7: Baseline Earnings Accuracy**
- **Probability**: Medium
- **Impact**: Medium (affects ROI calculations)
- **Context**: High school graduate earnings vary by state/county and over time
- **Mitigation**:
  - Use most recent ACS 5-year estimates (more stable than 1-year)
  - Provide both statewide and county-level baselines for comparison
  - Document baseline sources and assumptions
  - Update baselines annually with new ACS data
  - Sensitivity analysis: show how ROI changes with different baselines

**Risk 8: Cost Data Discrepancies**
- **Probability**: Medium
- **Impact**: Low to Medium
- **Context**: IPEDS net price may differ from College Scorecard average net price
- **Mitigation**:
  - Validate IPEDS cost data against Scorecard cost data
  - Use IPEDS as primary (already in our system)
  - Document any significant discrepancies
  - Provide data source attribution in UI
  - Allow users to see both cost metrics if available

### 7.3 Scope and Timeline Risks

**Risk 9: Scope Creep**
- **Probability**: Medium
- **Impact**: High (delays launch)
- **Context**: Temptation to add field-of-study ROI, debt metrics, etc.
- **Mitigation**:
  - Strict adherence to phased implementation plan
  - Focus on institution-level ROI first (defer program-level)
  - Document future enhancements separately
  - Get stakeholder buy-in on MVP scope
  - Use "Future Enhancements" section for ideas

**Risk 10: Resource Availability**
- **Probability**: Low to Medium
- **Impact**: High (blocks progress)
- **Context**: Developer availability, API access, computing resources
- **Mitigation**:
  - Buffer timeline with 10-15% contingency
  - Identify blockers early and escalate
  - Have backup contributors identified
  - Ensure API keys obtained before starting
  - Test data pipeline on small subset first

**Risk 11: Integration Complexity**
- **Probability**: Medium
- **Impact**: Medium
- **Context**: Integrating ROI into existing College Explorer section
- **Mitigation**:
  - Follow established patterns (tabs, chart modules, data loading)
  - Extensive testing of navigation and state management
  - Backward compatibility with existing College Explorer features
  - Code review with original College Explorer implementer
  - Staged rollout: College Explorer tab first, standalone section second

### 7.4 User Experience Risks

**Risk 12: Misinterpretation of ROI Metrics**
- **Probability**: High
- **Impact**: High (incorrect decisions based on misunderstanding)
- **Context**: ROI is complex metric with many caveats and assumptions
- **Mitigation**:
  - Prominent methodology documentation link
  - Tooltips explaining calculations
  - Warning messages for edge cases (negative premium, missing data)
  - Clear labeling: "Years to recoup investment" vs just "ROI"
  - Comparison with multiple baselines to show sensitivity
  - Educational content in overview pages

**Risk 13: Overemphasis on ROI at Expense of Other Metrics**
- **Probability**: Medium
- **Impact**: Medium
- **Context**: ROI is one dimension of college value, not the only one
- **Mitigation**:
  - Integrate ROI alongside graduation rates, cost, aid in College Explorer
  - Emphasize ROI as complementary to existing metrics
  - Overview documentation discusses limitations of ROI
  - Show multiple perspectives (quadrant analysis includes both cost and earnings)
  - Don't auto-sort by ROI; let users choose sorting

### 7.5 Mitigation Summary

**Proactive Measures:**
1. **Early Validation**: Implement and test data pipeline in Phase 1 before UI work
2. **Incremental Rollout**: College Explorer tab first, standalone section second
3. **Comprehensive Testing**: Unit tests, integration tests, UAT, data validation
4. **Clear Documentation**: Methodology docs, data sources, limitations, assumptions
5. **Stakeholder Communication**: Regular updates, demo sessions, feedback loops

**Contingency Plans:**
1. **API Failure**: Fallback to downloadable CSV files from College Scorecard website
2. **Data Quality Issues**: Document and exclude problematic institutions rather than blocking launch
3. **Performance Problems**: Reduce dataset size (e.g., top 1000 institutions) or simplify visualizations
4. **Timeline Delays**: Defer standalone ROI section to post-MVP, launch College Explorer tab only
5. **Integration Issues**: Revert to standalone ROI section if College Explorer integration proves too complex

---

## 8. Future Enhancements

### 8.1 Short-Term Enhancements (Post-Launch, 3-6 months)

**1. Program-Level (Field of Study) ROI**
- **Description**: ROI analysis by major/program (e.g., Engineering vs. Education)
- **Data Source**: College Scorecard Field of Study API
- **Value**: More granular analysis for student decision-making
- **Complexity**: High (many institutions x many programs = large dataset)
- **Implementation**: New section "ROI by Program" with institution + program drill-down

**2. Debt-Adjusted ROI**
- **Description**: Incorporate student loan debt into ROI calculation
- **Formula**: `(earnings_premium - annual_debt_payment) / net_cost`
- **Data Source**: College Scorecard debt fields, federal loan data we already have
- **Value**: More realistic ROI accounting for loan burden
- **Complexity**: Medium (requires debt data integration and payment calculations)

**3. Lifetime Earnings Projections**
- **Description**: Project total lifetime earnings difference (not just 10-year)
- **Formula**: Extrapolate earnings over 40-year career with wage growth assumptions
- **Value**: Show total financial impact of degree, not just payback period
- **Complexity**: Medium (requires economic modeling and assumptions)
- **Visualization**: Bar chart comparing lifetime earnings by institution

**4. ROI by Demographic Subgroup**
- **Description**: ROI analysis by race/ethnicity, gender, Pell status
- **Data Source**: College Scorecard has some subgroup earnings data
- **Value**: Equity analysis - identify institutions with equitable outcomes
- **Complexity**: High (sparse data, privacy suppression issues)
- **Implementation**: Conditional rendering based on data availability

**5. Regional Economic Context**
- **Description**: Incorporate local cost of living, labor market conditions
- **Data Source**: BLS regional price parities, state unemployment rates
- **Value**: More nuanced ROI that accounts for where graduates live/work
- **Complexity**: Medium (additional API integrations)

### 8.2 Medium-Term Enhancements (6-12 months)

**6. Interactive ROI Calculator**
- **Description**: User inputs their state, intended major, financial aid → personalized ROI estimate
- **Implementation**: Streamlit form with sliders/dropdowns
- **Value**: Prospective student tool for decision-making
- **Complexity**: Low to Medium (UI work, calculation logic already exists)

**7. ROI Trends Over Time**
- **Description**: Show how ROI has changed over multiple cohorts (if data available)
- **Data Source**: Historical College Scorecard releases
- **Value**: Identify improving vs declining value institutions
- **Complexity**: High (requires historical data acquisition and normalization)
- **Visualization**: Multi-line trend chart with cohort selection

**8. Peer Comparison Tool**
- **Description**: Select multiple institutions and compare ROI side-by-side
- **Implementation**: Multi-select dropdown with comparison table
- **Value**: Direct comparison for student decision-making
- **Complexity**: Low (UI enhancement)

**9. Export and Reporting**
- **Description**: Generate PDF reports with institution ROI analysis
- **Implementation**: Use Streamlit's download button with matplotlib/reportlab
- **Value**: Shareable analysis for advisors, policymakers
- **Complexity**: Medium (report generation logic)

**10. State-Level Policy Analysis**
- **Description**: Aggregate ROI metrics by state with policy recommendations
- **Value**: State policymaker tool for higher ed investment decisions
- **Complexity**: Medium (aggregation logic, policy framework)

### 8.3 Long-Term Enhancements (12+ months)

**11. Machine Learning ROI Predictions**
- **Description**: Predict ROI for institutions/programs without earnings data
- **Approach**: Train model on institutions with earnings data, predict for others
- **Features**: Institution characteristics, location, sector, graduation rates
- **Value**: Expand coverage beyond 60-70% with earnings data
- **Complexity**: High (ML development, validation, explainability)

**12. Alternative Outcome Metrics**
- **Description**: Beyond earnings - job satisfaction, graduate school enrollment, community impact
- **Data Source**: External surveys, state workforce data, NSF graduate enrollment data
- **Value**: Holistic value assessment beyond pure financial ROI
- **Complexity**: Very High (data acquisition, integration challenges)

**13. Real-Time Data Updates**
- **Description**: Automated pipeline to refresh data when College Scorecard updates
- **Implementation**: Scheduled jobs, data versioning, change detection
- **Value**: Always current data without manual updates
- **Complexity**: High (infrastructure, testing, monitoring)

**14. API for External Access**
- **Description**: Provide API for other applications to access our ROI calculations
- **Value**: Enable broader ecosystem of college value tools
- **Complexity**: Very High (API design, authentication, rate limiting, documentation)

**15. International Institution Comparisons**
- **Description**: Extend ROI analysis to international universities
- **Data Source**: Country-specific education databases (limited availability)
- **Value**: Global comparison for international students
- **Complexity**: Very High (data heterogeneity, currency conversion, cultural differences)

### 8.4 Enhancement Prioritization

**Priority 1 (High Value, Low Complexity):**
- Interactive ROI Calculator
- Peer Comparison Tool
- Export and Reporting

**Priority 2 (High Value, Medium Complexity):**
- Debt-Adjusted ROI
- Lifetime Earnings Projections
- Regional Economic Context

**Priority 3 (High Value, High Complexity):**
- Program-Level ROI
- ROI Trends Over Time
- ML ROI Predictions

**Priority 4 (Medium Value):**
- ROI by Demographic Subgroup
- State-Level Policy Analysis
- Alternative Outcome Metrics

**Priority 5 (Infrastructure):**
- Real-Time Data Updates
- API for External Access
- International Comparisons

---

## 9. Conclusion and Next Steps

### 9.1 Summary

This comprehensive integration strategy provides a roadmap for adding Return on Investment (ROI) analysis to the College Accountability Dashboard by adapting methodologies from the epanalysis repository. The key highlights:

**Strategic Approach:**
- Integrate ROI into College Explorer as "Earnings & ROI" tab for institution-level analysis
- Create standalone ROI section for aggregate cross-institution comparisons
- Follow established architectural patterns (sections, charts, data pipeline, governance)

**Data Requirements:**
- College Scorecard median earnings data (10-year post-entry) via API
- Census ACS high school graduate baseline earnings by state/county
- Merge with existing IPEDS cost, enrollment, and graduation data

**Core Methodology:**
- Calculate earnings premium: graduate earnings - high school baseline
- Calculate ROI: total program cost / earnings premium
- Provide both statewide and county-level baselines for comparison
- Handle missing data and negative premiums gracefully

**Implementation Timeline:**
- **Phase 1 (Weeks 1-2)**: Foundation and data acquisition
- **Phase 2 (Weeks 3-4)**: College Explorer ROI tab
- **Phase 3 (Weeks 5-6)**: Standalone ROI section with aggregate analysis
- **Phase 4 (Week 7)**: Testing, validation, documentation
- **Total: 7 weeks to production-ready ROI feature**

**Technical Specifications:**
- Enhanced data models with ROI metrics classes
- Three new chart modules (quadrant, rankings, sector distribution)
- API clients for College Scorecard and Census ACS
- Comprehensive test suite (unit, integration, data validation)

**Risk Management:**
- Proactive mitigation strategies for API availability, data coverage, calculation accuracy
- Contingency plans for technical and timeline risks
- Clear documentation of limitations and assumptions

**Future Vision:**
- Program-level ROI, debt-adjusted ROI, lifetime earnings
- Interactive calculators, peer comparison tools
- ML predictions, real-time updates, international comparisons

### 9.2 Immediate Next Steps

**For Project Lead/Decision Makers:**
1. **Review and Approve Strategy** (Day 1)
   - Review this document with stakeholders
   - Decide on College Explorer integration vs. standalone section
   - Approve 7-week timeline and resource allocation
   - Identify any additional requirements or constraints

2. **Secure API Access** (Day 2)
   - Register for College Scorecard API key at api.data.gov
   - Register for Census ACS API key at api.census.gov
   - Add API keys to `.env` file (ensure `.gitignore` includes `.env`)
   - Test API access with sample queries

3. **Assign Development Resources** (Day 3)
   - Assign developer(s) to Phase 1 (foundation and data acquisition)
   - Schedule kickoff meeting with development team
   - Set up project tracking (GitHub project board, milestones)
   - Establish communication cadence (daily standups, weekly demos)

**For Development Team:**
4. **Set Up Development Environment** (Week 1, Day 1)
   - Pull latest code from main branch
   - Create feature branch: `feature/roi-analysis`
   - Install any new dependencies (add to `pyproject.toml` if needed)
   - Verify existing test suite passes

5. **Implement API Clients** (Week 1, Days 2-3)
   - Create `src/data/college_scorecard_api.py` with fetch function
   - Create `src/data/census_acs_api.py` with baseline fetch function
   - Write unit tests for API clients
   - Test API calls with real keys and validate responses

6. **Build Data Pipeline** (Week 1, Days 4-5)
   - Create `src/data/build_roi_metrics.py` script
   - Implement merge logic (institutions + cost + enrollment + earnings + baselines)
   - Calculate ROI metrics with all formulas
   - Generate `data/processed/roi_metrics.parquet`
   - Validate output with test cases

7. **Update Data Models** (Week 1, Day 6)
   - Add ROI classes to `src/data/models.py` (EarningsData, BaselineEarnings, ROIMetrics)
   - Update schema.json with ROI fields
   - Write unit tests for ROI model classes

8. **Documentation and Governance** (Week 1, Day 7)
   - Update `data/dictionary/sources.yaml` with College Scorecard and Census ACS
   - Create `data/raw/college_scorecard/metadata.yaml`
   - Create `data/raw/census/metadata.yaml`
   - Document ROI methodology in `docs/ROI_METHODOLOGY.md`

9. **Phase 1 Testing and Validation** (Week 2, Days 8-10)
   - Run data pipeline end-to-end
   - Validate ROI calculations against epanalysis test cases
   - Check data coverage (should be 60-70% of institutions)
   - Create data quality report
   - Demo to stakeholders for approval to proceed to Phase 2

**For Ongoing Success:**
10. **Regular Check-ins**
   - Daily: Stand-up to share progress and blockers
   - Weekly: Demo working features to stakeholders
   - Bi-weekly: Review and adjust timeline based on progress

11. **Quality Assurance**
   - Code review for all commits
   - Test coverage >80% for new code
   - Performance profiling at each phase
   - User testing with representative stakeholders

12. **Documentation**
   - Update `CLAUDE.md` as architecture evolves
   - Update `LOG.md` with implementation milestones
   - Keep this ROI-Feature.md current as plan adjusts
   - Create user-facing help documentation

### 9.3 Success Metrics

**Phase 1 Success Criteria:**
- [ ] College Scorecard API successfully fetching earnings for 60%+ of institutions
- [ ] Census ACS API fetching baseline earnings for all 50 states
- [ ] ROI metrics calculated correctly (validated against test cases)
- [ ] `data/processed/roi_metrics.parquet` generated with ~6,000 institutions
- [ ] All unit tests passing
- [ ] Data pipeline runs in <5 minutes

**Phase 2 Success Criteria:**
- [ ] College Explorer "Earnings & ROI" tab functional
- [ ] ROI metrics display for institutions with earnings data
- [ ] Graceful handling of missing earnings data
- [ ] Peer comparison chart rendering correctly
- [ ] UI consistent with existing College Explorer design
- [ ] Load time <2 seconds for ROI tab

**Phase 3 Success Criteria:**
- [ ] Standalone ROI section with 3 chart types implemented
- [ ] Quadrant analysis with 4-year/2-year tabs functional
- [ ] Top 25 rankings with filtering and sorting
- [ ] Sector distribution analysis with summary statistics
- [ ] All ROI charts render in <3 seconds
- [ ] Navigation between sections seamless

**Phase 4 Success Criteria:**
- [ ] All tests passing (unit, integration, data validation, UAT)
- [ ] Performance meets targets (<2-3 second load times)
- [ ] Documentation complete (methodology, user guide, data dictionary)
- [ ] No critical bugs identified
- [ ] Stakeholder approval for production launch

**Post-Launch Success Metrics:**
- User engagement: % of users visiting ROI section/tab
- Data completeness: % of institutions with earnings data (monitor over time)
- Performance: 95th percentile load time <5 seconds
- User feedback: satisfaction scores, feature requests
- Data freshness: update pipeline runs successfully after College Scorecard releases

### 9.4 Final Recommendations

**Recommendation 1: Start with College Explorer Integration**
The hybrid approach (College Explorer tab + standalone ROI section) is ideal, but if resources are constrained, prioritize the College Explorer "Earnings & ROI" tab. This provides immediate value to users exploring specific institutions and fits naturally into the existing user journey.

**Recommendation 2: Invest in Data Quality**
The credibility of ROI analysis depends entirely on data accuracy. Allocate sufficient time in Phase 1 for validation, testing, and spot-checking calculations. Consider manual review of ROI calculations for top 100 institutions before launch.

**Recommendation 3: Communicate Limitations Clearly**
ROI is inherently complex with many assumptions (baseline earnings, program length, cohort timing). Prominent methodology documentation and clear UI messaging will prevent misinterpretation and build user trust.

**Recommendation 4: Plan for Annual Updates**
College Scorecard releases new earnings data annually. Build the data pipeline with automation in mind, even if initial implementation is manual. Document the update process thoroughly for future maintainers.

**Recommendation 5: Gather User Feedback Early**
Once Phase 2 is complete (College Explorer ROI tab), conduct user testing with representative stakeholders (students, counselors, researchers). Use feedback to refine Phase 3 (standalone section) before implementation.

### 9.5 Contact and Support

For questions, feedback, or support during implementation:

**Project Documentation:**
- This document: `ROI-Feature.md`
- Methodology: `docs/ROI_METHODOLOGY.md` (to be created in Phase 1)
- Architecture: `CLAUDE.md` (update as ROI features are added)
- Change log: `LOG.md` (document milestones and major changes)

**Key Resources:**
- epanalysis repository: https://github.com/malpasocodes/epanalysis
- College Scorecard API: https://collegescorecard.ed.gov/data/api-documentation/
- Census ACS API: https://www.census.gov/data/developers/data-sets/acs-5year.html
- IPEDS Data Center: https://nces.ed.gov/ipeds/datacenter/

**Development Support:**
- Code review: Request PR review from original College Explorer implementer
- Architecture questions: Reference `CLAUDE.md` and existing section patterns
- Data questions: Consult data dictionary and sources.yaml
- Testing: Follow existing test patterns in `tests/` directory

---

**Document End**

This comprehensive integration strategy is ready for review and implementation. The phased approach, detailed technical specifications, and risk mitigation strategies provide a clear path from research to production-ready ROI analysis feature. With 7 weeks of focused development, the College Accountability Dashboard will offer students, counselors, and policymakers unprecedented insight into the return on investment of higher education institutions across the United States.
