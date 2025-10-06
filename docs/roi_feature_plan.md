# ROI Analysis Migration Plan

## Executive Summary

This document outlines the migration of the **Higher Ed ROI Research Lab (epanalysis)** repository into the College Accountability Dashboard. This is a **consolidation effort** to create a single, comprehensive platform for college accountability analysis, allowing the epanalysis repository to be retired.

**Migration Scope**: California-only ROI analysis (120 institutions)
**Timeline**: 6 weeks
**Outcome**: Complete ROI functionality integrated into existing dashboard, epanalysis repository archived

### Why Migrate?

1. **Single Source of Truth**: Consolidate all college accountability analysis in one platform
2. **Unified User Experience**: Users access ROI alongside graduation rates, federal loans, Pell grants
3. **Simplified Maintenance**: Maintain one codebase instead of two repositories
4. **Consistent Architecture**: Leverage existing modular structure, data governance, and UI patterns
5. **Better Discoverability**: ROI analysis reaches wider audience through comprehensive dashboard

---

## epanalysis Repository Analysis

### Repository Overview
- **URL**: https://github.com/malpasocodes/epanalysis
- **Purpose**: Data-driven ROI analysis for California's 2-year and certificate-granting colleges
- **Tech Stack**: Streamlit + Pandas + Altair (perfect alignment with this project)
- **Coverage**: 120 California Associate's degree-granting institutions
- **Methodology**: Dual baseline approach (statewide vs county) for earnings premium calculation

### Core ROI Calculation Methodology

```python
# Step 1: Calculate earnings premium
premium_statewide = median_earnings_10yr - statewide_hs_baseline  # $24,939.44
premium_regional = median_earnings_10yr - county_hs_baseline

# Step 2: Calculate ROI (years to recoup investment)
roi_statewide_years = total_net_price / premium_statewide
roi_regional_years = total_net_price / premium_regional

# Step 3: Rank institutions by ROI
rank_statewide = rank(roi_statewide_years, ascending=True)
rank_regional = rank(roi_regional_years, ascending=True)
rank_change = rank_statewide - rank_regional  # Shows baseline impact
```

**Key Innovation**: Comparing statewide vs county baselines reveals how local economic conditions affect perceived ROI. Some institutions rank significantly different depending on baseline choice.

### Data Assets to Migrate

#### 1. Primary Dataset: `data/roi-metrics.csv`
- **Rows**: 120 California institutions
- **Columns**: 13 fields
  - `OPEID6` - Institution identifier (6-digit OPEID)
  - `Institution` - Institution name
  - `County` - California county location
  - `Sector` - Public/Private/For-profit
  - `median_earnings_10yr` - Median earnings 10 years post-entry (College Scorecard)
  - `total_net_price` - Total program net price
  - `premium_statewide` - Earnings vs CA state baseline ($24,939.44)
  - `premium_regional` - Earnings vs county baseline
  - `roi_statewide_years` - Years to recoup (state baseline)
  - `roi_regional_years` - Years to recoup (county baseline)
  - `rank_statewide` - ROI rank using state baseline (1 = best)
  - `rank_regional` - ROI rank using regional baseline (1 = best)
  - `rank_change` - Difference between rankings (shows baseline sensitivity)
  - `hs_median_income` - County high school baseline earnings

#### 2. Supporting Dataset: `data/gr-institutions.csv`
- Institution characteristics (sector, location, enrollment)
- Additional institutional metadata

#### 3. Baseline Data: `data/hs_median_county_25_34.csv`
- County-level high school earnings for ages 25-34
- Census ACS 5-year estimates
- Used for regional baseline calculations

### Visualizations to Migrate

#### 1. Cost vs Earnings Scatter Plot
- **X-axis**: Total program net price
- **Y-axis**: Median earnings (10 years post-entry)
- **Color**: ROI years (gradient green=fast to red=slow)
- **Quadrants**: Divided by median cost and median earnings
  - Top-left: High earnings, low cost (best ROI)
  - Bottom-right: Low earnings, high cost (worst ROI)
- **Interactivity**: Tooltips with institution details, ROI metrics

#### 2. ROI Rankings
- Top 25 and Bottom 25 institutions by ROI
- Horizontal bar charts
- Color-coded by sector
- Shows years/months to recoup investment

#### 3. Baseline Comparison Analysis
- Side-by-side comparison of statewide vs regional ROI rankings
- Highlights institutions most affected by baseline choice
- Shows `rank_change` metric

---

## Migration Strategy

### Hybrid Implementation Approach

**Option A: Standalone ROI Section** (Aggregate Analysis)
- Use existing ROI section stub in navigation
- Cross-institutional comparisons
- 3 chart types: Quadrant, Rankings, Distribution
- CA-only focus clearly messaged

**Option B: College Explorer Enhancement** (Institution-Level Detail)
- Add "Earnings & ROI" tab to College Explorer
- Show ROI data when CA institution selected
- Display "ROI analysis available for California institutions only" for non-CA

**Recommendation: Implement Both** (Mirrors existing pattern)
- ROI Section provides aggregate analysis and rankings
- College Explorer provides institution-specific deep dive
- Consistent with Federal Loans and Pell Grants approach

### Architecture Alignment

Your existing dashboard architecture is **perfectly suited** for this migration:

| Component | Current Dashboard | epanalysis | Migration Strategy |
|-----------|------------------|------------|-------------------|
| UI Framework | Streamlit | Streamlit | Direct code reuse |
| Data Processing | Pandas + Parquet | Pandas + CSV | Convert CSV → Parquet |
| Visualization | Altair charts | Altair charts | Adapt chart modules |
| Architecture | Modular (sections/charts/data) | Modular (lib/) | Map to section pattern |
| Navigation | Config-driven tabs | Sidebar sections | Use existing tab pattern |
| Caching | `@st.cache_data` | `@st.cache_data` | Keep same approach |
| Data Governance | IPEDS + FSA with metadata | Scorecard + Census | Add epanalysis source |

---

## Phased Implementation Timeline

### Phase 1: Data Migration (Week 1)

**Objective**: Migrate data files from epanalysis, establish data governance, and create processed datasets.

#### Tasks:

**1.1 Copy Data Files**
```bash
# Create directory structure
mkdir -p data/raw/epanalysis
mkdir -p data/processed

# Copy CSV files from epanalysis repository
cp /path/to/epanalysis/data/roi-metrics.csv data/raw/epanalysis/
cp /path/to/epanalysis/data/gr-institutions.csv data/raw/epanalysis/
cp /path/to/epanalysis/data/hs_median_county_25_34.csv data/raw/epanalysis/
```

**1.2 Create Data Provenance Metadata**

Create `data/raw/epanalysis/metadata.yaml`:
```yaml
source: epanalysis Repository (California ROI Analysis)
url: https://github.com/malpasocodes/epanalysis
description: |
  Return on Investment analysis for California's 2-year and certificate-granting
  colleges. Includes pre-calculated ROI metrics, earnings premiums, and rankings
  using dual baseline methodology (statewide vs county).
coverage: 120 California Associate's degree-granting institutions
data_sources:
  - College Scorecard (median earnings 10 years post-entry)
  - IPEDS (net price, institution characteristics)
  - Census ACS 5-year estimates (high school baseline earnings)
update_frequency: Annual
last_updated: 2024
baseline_statewide: $24,939.44
methodology: |
  ROI = Total Program Net Price / Earnings Premium
  Premium = Graduate Earnings - High School Baseline Earnings
fields:
  - OPEID6: 6-digit OPEID institution identifier
  - Institution: Institution name
  - County: California county location
  - Sector: Public/Private/For-profit
  - median_earnings_10yr: Median earnings 10 years after entry
  - total_net_price: Total program net price
  - premium_statewide: Earnings vs CA state baseline
  - premium_regional: Earnings vs county baseline
  - roi_statewide_years: Years to recoup (state baseline)
  - roi_regional_years: Years to recoup (county baseline)
  - rank_statewide: ROI rank using state baseline
  - rank_regional: ROI rank using regional baseline
  - rank_change: Difference between rankings
  - hs_median_income: County high school baseline earnings
```

**1.3 Create OPEID to UnitID Mapping**

Since epanalysis uses `OPEID6` and our dashboard uses IPEDS `UnitID`, we need a mapping:

```python
# src/data/build_roi_opeid_mapping.py

import pandas as pd

def build_opeid_unitid_mapping():
    """
    Create mapping between OPEID6 (epanalysis) and UnitID (IPEDS).

    IPEDS institutions dataset includes both OPEID and UnitID.
    We'll use this to map the 120 CA institutions.
    """
    # Load our existing institutions data
    institutions = pd.read_parquet('data/processed/institutions.parquet')

    # Load epanalysis ROI data
    roi_data = pd.read_csv('data/raw/epanalysis/roi-metrics.csv')

    # Create mapping: OPEID6 → UnitID
    # OPEID is stored as OPEID in IPEDS (may need to strip leading zeros or convert)
    institutions['OPEID6'] = institutions['OPEID'].astype(str).str.zfill(6)

    mapping = institutions[['OPEID6', 'UnitID', 'institution', 'state']].copy()
    mapping = mapping[mapping['state'] == 'CA']  # CA only

    # Merge with ROI data to verify matches
    merged = roi_data.merge(mapping, on='OPEID6', how='left', indicator=True)

    print(f"Matched: {(merged['_merge'] == 'both').sum()} / {len(roi_data)}")
    print(f"Unmatched: {(merged['_merge'] == 'left_only').sum()}")

    # Save mapping
    mapping.to_csv('data/raw/epanalysis/opeid_unitid_mapping.csv', index=False)

    return mapping

if __name__ == '__main__':
    build_opeid_unitid_mapping()
```

**1.4 Build Processed ROI Dataset**

Create `src/data/build_roi_metrics.py`:
```python
"""
Build processed ROI metrics dataset for California institutions.
Migrated from epanalysis repository.
"""

import pandas as pd
from pathlib import Path

def build_roi_metrics():
    """
    Process ROI data from epanalysis into Parquet format.

    Input: data/raw/epanalysis/roi-metrics.csv (120 CA institutions)
    Output: data/processed/roi_metrics.parquet
    """
    # Load raw ROI data
    roi_df = pd.read_csv('data/raw/epanalysis/roi-metrics.csv')

    # Load OPEID → UnitID mapping
    mapping = pd.read_csv('data/raw/epanalysis/opeid_unitid_mapping.csv')

    # Merge to add UnitID
    merged = roi_df.merge(
        mapping[['OPEID6', 'UnitID']],
        on='OPEID6',
        how='left'
    )

    # Validate merge
    assert merged['UnitID'].notna().sum() == len(roi_df), \
        "Not all institutions mapped to UnitID"

    # Convert data types for Parquet efficiency
    merged['UnitID'] = merged['UnitID'].astype('int32')
    merged['OPEID6'] = merged['OPEID6'].astype(str)
    merged['Institution'] = merged['Institution'].astype('string')
    merged['County'] = merged['County'].astype('category')
    merged['Sector'] = merged['Sector'].astype('category')

    # Float columns
    float_cols = [
        'median_earnings_10yr', 'total_net_price',
        'premium_statewide', 'premium_regional',
        'roi_statewide_years', 'roi_regional_years',
        'hs_median_income'
    ]
    for col in float_cols:
        merged[col] = merged[col].astype('float32')

    # Integer columns
    int_cols = ['rank_statewide', 'rank_regional', 'rank_change']
    for col in int_cols:
        merged[col] = merged[col].astype('int16')

    # Add calculated fields for UI display
    merged['roi_statewide_months'] = (merged['roi_statewide_years'] * 12).round().astype('int16')
    merged['roi_regional_months'] = (merged['roi_regional_years'] * 12).round().astype('int16')

    # Add flags for easier filtering
    merged['has_positive_premium_state'] = merged['premium_statewide'] > 0
    merged['has_positive_premium_regional'] = merged['premium_regional'] > 0

    # Validation
    validate_roi_dataset(merged)

    # Save as Parquet
    merged.to_parquet(
        'data/processed/roi_metrics.parquet',
        engine='pyarrow',
        compression='snappy',
        index=False
    )

    print(f"✓ Created roi_metrics.parquet with {len(merged)} institutions")
    print(f"✓ Columns: {list(merged.columns)}")
    print(f"✓ File size: {Path('data/processed/roi_metrics.parquet').stat().st_size / 1024:.1f} KB")

    return merged


def validate_roi_dataset(df: pd.DataFrame) -> None:
    """Validate ROI metrics dataset."""
    print("\n=== Validation ===")

    # Check row count
    assert len(df) == 120, f"Expected 120 institutions, got {len(df)}"
    print(f"✓ Row count: {len(df)}")

    # Check required columns
    required_cols = [
        'UnitID', 'OPEID6', 'Institution', 'County', 'Sector',
        'median_earnings_10yr', 'total_net_price',
        'premium_statewide', 'premium_regional',
        'roi_statewide_years', 'roi_regional_years',
        'rank_statewide', 'rank_regional'
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    print(f"✓ All required columns present")

    # Check no nulls in key columns
    assert df['UnitID'].notna().all(), "Null UnitIDs found"
    assert df['median_earnings_10yr'].notna().all(), "Null earnings found"
    assert df['roi_statewide_years'].notna().all(), "Null ROI years found"
    print(f"✓ No nulls in key columns")

    # Check ROI reasonableness (0-30 years typical)
    roi_valid = df['roi_statewide_years'].between(0, 50)
    assert roi_valid.all(), f"ROI outliers detected: {df[~roi_valid][['Institution', 'roi_statewide_years']]}"
    print(f"✓ ROI values reasonable (0-50 years)")

    # Check rankings (1-120)
    assert df['rank_statewide'].min() == 1, "Rank should start at 1"
    assert df['rank_statewide'].max() == 120, "Rank should end at 120"
    print(f"✓ Rankings valid (1-120)")

    # Summary statistics
    print(f"\n=== Summary Statistics ===")
    print(f"Median earnings: ${df['median_earnings_10yr'].median():,.0f}")
    print(f"Median net price: ${df['total_net_price'].median():,.0f}")
    print(f"Median ROI (statewide): {df['roi_statewide_years'].median():.2f} years")
    print(f"Median ROI (regional): {df['roi_regional_years'].median():.2f} years")
    print(f"Best ROI: {df.loc[df['rank_statewide'] == 1, 'Institution'].values[0]} ({df['roi_statewide_years'].min():.2f} years)")
    print(f"Worst ROI: {df.loc[df['rank_statewide'] == 120, 'Institution'].values[0]} ({df['roi_statewide_years'].max():.2f} years)")


if __name__ == '__main__':
    build_roi_metrics()
```

**1.5 Update Data Models**

Add to `src/data/models.py`:
```python
@dataclass
class ROIMetrics:
    """ROI metrics for California institutions (migrated from epanalysis)."""

    # Identifiers
    unit_id: int
    opeid6: str
    institution: str
    county: str
    sector: str

    # Earnings and Cost
    median_earnings_10yr: float
    total_net_price: float

    # Earnings Premium
    premium_statewide: float
    premium_regional: float

    # ROI Metrics
    roi_statewide_years: float
    roi_regional_years: float
    roi_statewide_months: int
    roi_regional_months: int

    # Rankings
    rank_statewide: int
    rank_regional: int
    rank_change: int

    # Baseline
    hs_median_income: float

    # Flags
    has_positive_premium_state: bool
    has_positive_premium_regional: bool

    def __post_init__(self):
        """Validate ROI metrics."""
        if self.roi_statewide_years < 0:
            raise ValueError(f"Invalid ROI: {self.roi_statewide_years}")
        if not (1 <= self.rank_statewide <= 120):
            raise ValueError(f"Invalid rank: {self.rank_statewide}")
```

**1.6 Update Data Manager**

Add to `src/core/data_manager.py`:
```python
@st.cache_data(ttl=3600)
def load_roi_metrics(_self) -> pd.DataFrame:
    """
    Load ROI metrics for California institutions.

    Returns:
        DataFrame with ROI data for 120 CA institutions
    """
    return _self.loader.load_data(
        DATA_SOURCES.ROI_METRICS_PATH,
        "roi_metrics",
        required_columns=[
            "UnitID", "Institution", "median_earnings_10yr",
            "roi_statewide_years", "rank_statewide"
        ]
    )

def get_institution_roi(self, unit_id: int) -> Optional[pd.Series]:
    """
    Get ROI metrics for a specific institution.

    Args:
        unit_id: IPEDS UnitID

    Returns:
        Series with ROI data if available, None if not in CA ROI dataset
    """
    roi_df = self.load_roi_metrics()
    institution_roi = roi_df[roi_df['UnitID'] == unit_id]

    if institution_roi.empty:
        return None

    return institution_roi.iloc[0]
```

**1.7 Update Configuration**

Add to `src/config/data_sources.py`:
```python
# ROI Data (California institutions from epanalysis migration)
ROI_METRICS_PATH = PROCESSED_DIR / "roi_metrics.parquet"
ROI_METRICS_CSV_PATH = RAW_DIR / "epanalysis" / "roi-metrics.csv"
```

Add to `src/config/constants.py`:
```python
# ROI Section Labels
ROI_OVERVIEW_LABEL = "Overview"
ROI_QUADRANT_LABEL = "Cost vs Earnings Quadrant"
ROI_RANKINGS_LABEL = "Top 25 ROI Rankings"
ROI_DISTRIBUTION_LABEL = "ROI by Sector"

ROI_CHARTS: List[str] = [
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
]

# College Explorer - ROI Tab
COLLEGE_EXPLORER_ROI_LABEL = "Earnings & ROI"

# Update College Explorer charts
COLLEGE_EXPLORER_CHARTS: List[str] = [
    COLLEGE_EXPLORER_SUMMARY_LABEL,
    COLLEGE_EXPLORER_FEDERAL_AID_LABEL,
    COLLEGE_EXPLORER_GRAD_RATES_LABEL,
    COLLEGE_EXPLORER_ROI_LABEL,  # NEW
]
```

#### Deliverables:
- ✓ ROI data files migrated to `data/raw/epanalysis/`
- ✓ Metadata documented in `metadata.yaml`
- ✓ OPEID → UnitID mapping created
- ✓ Processed `roi_metrics.parquet` generated (120 institutions)
- ✓ Data models updated with `ROIMetrics` class
- ✓ DataManager methods for loading ROI data
- ✓ Configuration constants defined

#### Success Criteria:
- All 120 institutions mapped to UnitID successfully
- Parquet file validated (correct schema, data types)
- ROI calculations preserved exactly from epanalysis
- Data accessible via `data_manager.load_roi_metrics()`

---

### Phase 2: ROI Section Implementation (Weeks 2-4)

**Objective**: Replace "Coming Soon" stub in ROI section with full aggregate analysis functionality.

#### Tasks:

**2.1 Create ROI Overview Page**

Update `src/sections/roi.py`:
```python
def render_overview(self) -> None:
    """Render the ROI overview page."""
    self.render_section_header("ROI", "Overview")

    # Hero section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
        <h1 style='margin: 0; color: white;'>💰 Return on Investment Analysis</h1>
        <p style='font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;'>
            Analyze earnings outcomes and investment payback for California colleges
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Key insight callout
    st.info("""
    **🎯 Key Insight**: ROI varies significantly based on local economic conditions.
    This analysis compares statewide vs county-based high school earnings baselines
    to show how geography affects perceived value.
    """)

    # What is this section
    st.markdown("## What is ROI Analysis?")
    st.markdown("""
    Return on Investment (ROI) measures **how long it takes to recoup** the cost of
    a college education through increased earnings compared to a high school baseline.

    **Formula**: `ROI (years) = Total Program Cost / Earnings Premium`

    Where:
    - **Total Program Cost** = Net price per year × program length
    - **Earnings Premium** = Graduate earnings - High school baseline earnings
    """)

    # Methodology box
    st.markdown("""
    <div style='border: 2px solid #667eea; border-radius: 8px; padding: 1.5rem;
                background-color: #f8f9ff; margin: 1.5rem 0;'>
        <h3 style='margin-top: 0; color: #667eea;'>📊 Dual Baseline Methodology</h3>
        <p>
            This analysis uses <strong>two baseline approaches</strong>:
        </p>
        <ul>
            <li><strong>Statewide Baseline</strong>: California median HS earnings ($24,939)</li>
            <li><strong>Regional Baseline</strong>: County-specific median HS earnings</li>
        </ul>
        <p>
            Comparing these reveals how local economic conditions impact ROI rankings.
            An institution in a high-wage county may show better ROI using regional baseline.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Data coverage
    st.markdown("## Data Coverage")

    # Load ROI data for summary
    roi_df = self.data_manager.load_roi_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Institutions", f"{len(roi_df)}")
    with col2:
        st.metric("California Only", "Yes ✓")
    with col3:
        median_roi = roi_df['roi_statewide_years'].median()
        st.metric("Median ROI", f"{median_roi:.1f} years")
    with col4:
        best_roi = roi_df['roi_statewide_years'].min()
        st.metric("Best ROI", f"{best_roi:.1f} years")

    # How to explore
    st.markdown("## How to Explore This Section")
    st.markdown("""
    Use the sidebar charts to analyze ROI from different perspectives:

    - **Cost vs Earnings Quadrant**: Visualize the relationship between program cost
      and earnings outcomes. Identify high-value institutions (high earnings, low cost).

    - **Top 25 ROI Rankings**: See which institutions offer the fastest payback period.
      Compare statewide vs regional rankings.

    - **ROI by Sector**: Understand ROI distribution across public, private, and
      for-profit institutions.
    """)

    # Data source attribution
    st.markdown("## Data Sources")
    st.markdown("""
    - **Earnings Data**: College Scorecard (median earnings 10 years after entry)
    - **Cost Data**: IPEDS (net price)
    - **Baseline Earnings**: U.S. Census Bureau ACS 5-year estimates
    - **Coverage**: California Associate's degree-granting institutions
    - **Last Updated**: 2024

    *Migrated from the [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis) repository.*
    """)

    # Disclaimer
    st.warning("""
    **⚠️ Important Limitations**:
    - ROI analysis is limited to California institutions only
    - Earnings data represents cohorts from 10+ years ago
    - Individual outcomes vary based on field of study, local labor markets, and personal circumstances
    - This is one metric among many for evaluating college value
    """)
```

**2.2 Create Chart Module: Cost vs Earnings Quadrant**

Create `src/charts/roi_quadrant_chart.py`:
```python
"""
ROI quadrant chart: Cost vs Earnings scatter plot.
Migrated from epanalysis repository.
"""

import altair as alt
import pandas as pd


def create_roi_quadrant_chart(
    data: pd.DataFrame,
    baseline_type: str = "statewide"
) -> alt.Chart:
    """
    Create scatter plot with quadrants: Cost vs Earnings.

    Args:
        data: ROI metrics DataFrame
        baseline_type: "statewide" or "regional"

    Returns:
        Altair chart
    """
    # Select ROI column based on baseline
    roi_col = f"roi_{baseline_type}_years"

    # Calculate median lines for quadrants
    median_cost = data['total_net_price'].median()
    median_earnings = data['median_earnings_10yr'].median()

    # Base scatter plot
    scatter = alt.Chart(data).mark_circle(size=100, opacity=0.7).encode(
        x=alt.X(
            'total_net_price:Q',
            title='Total Program Net Price ($)',
            scale=alt.Scale(zero=False)
        ),
        y=alt.Y(
            'median_earnings_10yr:Q',
            title='Median Earnings 10 Years After Entry ($)',
            scale=alt.Scale(zero=False)
        ),
        color=alt.Color(
            f'{roi_col}:Q',
            title='ROI (years)',
            scale=alt.Scale(
                scheme='redyellowgreen',
                reverse=True,  # Green = low ROI (good), Red = high ROI (bad)
                domain=[0, 10]
            )
        ),
        tooltip=[
            alt.Tooltip('Institution:N', title='Institution'),
            alt.Tooltip('County:N', title='County'),
            alt.Tooltip('Sector:N', title='Sector'),
            alt.Tooltip('total_net_price:Q', title='Net Price', format='$,.0f'),
            alt.Tooltip('median_earnings_10yr:Q', title='Earnings (10yr)', format='$,.0f'),
            alt.Tooltip(f'{roi_col}:Q', title=f'ROI ({baseline_type})', format='.2f years'),
            alt.Tooltip(f'rank_{baseline_type}:Q', title='Rank', format='d'),
        ]
    ).properties(
        width=700,
        height=500,
        title=f'Cost vs Earnings Quadrant Analysis ({baseline_type.title()} Baseline)'
    )

    # Median cost line (vertical)
    cost_line = alt.Chart(pd.DataFrame({'median_cost': [median_cost]})).mark_rule(
        color='gray',
        strokeDash=[5, 5]
    ).encode(
        x='median_cost:Q'
    )

    # Median earnings line (horizontal)
    earnings_line = alt.Chart(pd.DataFrame({'median_earnings': [median_earnings]})).mark_rule(
        color='gray',
        strokeDash=[5, 5]
    ).encode(
        y='median_earnings:Q'
    )

    # Quadrant labels
    labels = pd.DataFrame([
        {'x': median_cost * 0.7, 'y': median_earnings * 1.15, 'label': 'High Value\n(Low Cost, High Earnings)'},
        {'x': median_cost * 1.3, 'y': median_earnings * 1.15, 'label': 'High Earnings\n(High Cost, High Earnings)'},
        {'x': median_cost * 0.7, 'y': median_earnings * 0.85, 'label': 'Low Cost\n(Low Cost, Low Earnings)'},
        {'x': median_cost * 1.3, 'y': median_earnings * 0.85, 'label': 'Low Value\n(High Cost, Low Earnings)'},
    ])

    label_text = alt.Chart(labels).mark_text(
        fontSize=11,
        color='gray',
        fontStyle='italic',
        align='center'
    ).encode(
        x='x:Q',
        y='y:Q',
        text='label:N'
    )

    # Combine layers
    chart = (scatter + cost_line + earnings_line + label_text).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    return chart
```

**2.3 Create Chart Module: ROI Rankings**

Create `src/charts/roi_rankings_chart.py`:
```python
"""
ROI rankings chart: Top/Bottom 25 by ROI.
Migrated from epanalysis repository.
"""

import altair as alt
import pandas as pd


def create_roi_rankings_chart(
    data: pd.DataFrame,
    baseline_type: str = "statewide",
    show_top: bool = True,
    n: int = 25
) -> alt.Chart:
    """
    Create horizontal bar chart of top/bottom N institutions by ROI.

    Args:
        data: ROI metrics DataFrame
        baseline_type: "statewide" or "regional"
        show_top: True for best ROI, False for worst ROI
        n: Number of institutions to show (default 25)

    Returns:
        Altair chart
    """
    roi_col = f"roi_{baseline_type}_years"
    rank_col = f"rank_{baseline_type}"

    # Sort and filter
    if show_top:
        filtered = data.nsmallest(n, roi_col).copy()
        title = f"Top {n} Institutions by ROI ({baseline_type.title()} Baseline)"
        color_scheme = 'greens'
    else:
        filtered = data.nlargest(n, roi_col).copy()
        title = f"Bottom {n} Institutions by ROI ({baseline_type.title()} Baseline)"
        color_scheme = 'reds'

    # Sort by ROI for display
    filtered = filtered.sort_values(roi_col, ascending=show_top)

    # Calculate months for better display
    months_col = f"roi_{baseline_type}_months"

    chart = alt.Chart(filtered).mark_bar().encode(
        y=alt.Y(
            'Institution:N',
            title=None,
            sort=alt.EncodingSortField(field=roi_col, order='ascending' if show_top else 'descending')
        ),
        x=alt.X(
            f'{months_col}:Q',
            title='Months to Recoup Investment',
            scale=alt.Scale(zero=True)
        ),
        color=alt.Color(
            'Sector:N',
            title='Sector',
            scale=alt.Scale(
                domain=['Public', 'Private nonprofit', 'Private for-profit'],
                range=['#1f77b4', '#ff7f0e', '#d62728']
            )
        ),
        tooltip=[
            alt.Tooltip('Institution:N', title='Institution'),
            alt.Tooltip('County:N', title='County'),
            alt.Tooltip('Sector:N', title='Sector'),
            alt.Tooltip(f'{rank_col}:Q', title='Rank', format='d'),
            alt.Tooltip(f'{roi_col}:Q', title='ROI (years)', format='.2f'),
            alt.Tooltip(f'{months_col}:Q', title='ROI (months)', format='d'),
            alt.Tooltip('total_net_price:Q', title='Net Price', format='$,.0f'),
            alt.Tooltip('median_earnings_10yr:Q', title='Earnings (10yr)', format='$,.0f'),
        ]
    ).properties(
        width=700,
        height=600,
        title=title
    ).configure_axis(
        labelFontSize=10,
        titleFontSize=14
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    return chart
```

**2.4 Create Chart Module: ROI Distribution by Sector**

Create `src/charts/roi_distribution_chart.py`:
```python
"""
ROI distribution chart: Box plot by sector.
Migrated from epanalysis repository.
"""

import altair as alt
import pandas as pd


def create_roi_distribution_chart(
    data: pd.DataFrame,
    baseline_type: str = "statewide"
) -> alt.Chart:
    """
    Create box plot showing ROI distribution across sectors.

    Args:
        data: ROI metrics DataFrame
        baseline_type: "statewide" or "regional"

    Returns:
        Altair chart
    """
    roi_col = f"roi_{baseline_type}_years"

    # Box plot
    box = alt.Chart(data).mark_boxplot(
        size=50,
        color='lightgray',
        median={'color': 'black', 'size': 2}
    ).encode(
        x=alt.X(
            'Sector:N',
            title='Sector',
            axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(
            f'{roi_col}:Q',
            title='ROI (Years to Recoup)',
            scale=alt.Scale(zero=False)
        ),
        color=alt.Color(
            'Sector:N',
            legend=None,
            scale=alt.Scale(
                domain=['Public', 'Private nonprofit', 'Private for-profit'],
                range=['#1f77b4', '#ff7f0e', '#d62728']
            )
        )
    )

    # Overlay individual points
    points = alt.Chart(data).mark_circle(
        size=30,
        opacity=0.3
    ).encode(
        x=alt.X(
            'Sector:N',
            axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(f'{roi_col}:Q'),
        color=alt.Color('Sector:N', legend=None),
        tooltip=[
            alt.Tooltip('Institution:N', title='Institution'),
            alt.Tooltip('County:N', title='County'),
            alt.Tooltip('Sector:N', title='Sector'),
            alt.Tooltip(f'{roi_col}:Q', title='ROI (years)', format='.2f'),
            alt.Tooltip('total_net_price:Q', title='Net Price', format='$,.0f'),
            alt.Tooltip('median_earnings_10yr:Q', title='Earnings (10yr)', format='$,.0f'),
        ]
    )

    chart = (box + points).properties(
        width=600,
        height=400,
        title=f'ROI Distribution by Sector ({baseline_type.title()} Baseline)'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    return chart
```

**2.5 Update ROI Section Class**

Complete implementation of `src/sections/roi.py`:
```python
"""ROI section implementation - migrated from epanalysis."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection
from src.charts.roi_quadrant_chart import create_roi_quadrant_chart
from src.charts.roi_rankings_chart import create_roi_rankings_chart
from src.charts.roi_distribution_chart import create_roi_distribution_chart
from src.config.constants import (
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
)


class ROISection(BaseSection):
    """Handles the ROI section with California-only analysis."""

    def render_overview(self) -> None:
        """Render the ROI overview."""
        # [Implementation from 2.1 above]
        pass

    def render_chart(self, chart_name: str) -> None:
        """Render a specific ROI chart."""
        self.render_section_header("ROI", chart_name)

        # Load ROI data
        roi_data = self.data_manager.load_roi_metrics()

        # California-only reminder
        st.info("📍 **California Institutions Only** - This analysis covers 120 California community and technical colleges.")

        # Render appropriate chart
        if chart_name == ROI_QUADRANT_LABEL:
            self._render_quadrant_chart(roi_data)
        elif chart_name == ROI_RANKINGS_LABEL:
            self._render_rankings_chart(roi_data)
        elif chart_name == ROI_DISTRIBUTION_LABEL:
            self._render_distribution_chart(roi_data)
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_quadrant_chart(self, data) -> None:
        """Render cost vs earnings quadrant chart with baseline tabs."""
        st.markdown("""
        Visualize the relationship between program cost and earnings outcomes.
        Institutions in the **top-left quadrant** offer the best value
        (high earnings, low cost).
        """)

        # Tabs for baseline comparison
        tab1, tab2 = st.tabs(["Statewide Baseline", "Regional Baseline"])

        with tab1:
            st.markdown("**Baseline**: California statewide median HS earnings ($24,939)")
            chart = create_roi_quadrant_chart(data, baseline_type="statewide")
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            st.markdown("**Baseline**: County-specific median HS earnings")
            chart = create_roi_quadrant_chart(data, baseline_type="regional")
            st.altair_chart(chart, use_container_width=True)

    def _render_rankings_chart(self, data) -> None:
        """Render ROI rankings with baseline and top/bottom tabs."""
        st.markdown("""
        Compare institutions by years to recoup investment. Lower ROI = faster payback.
        """)

        # Baseline selection
        baseline = st.radio(
            "Select Baseline:",
            ["Statewide", "Regional"],
            horizontal=True,
            key="roi_rankings_baseline"
        )
        baseline_type = baseline.lower()

        # Top/Bottom tabs
        tab1, tab2 = st.tabs(["Top 25 (Best ROI)", "Bottom 25 (Worst ROI)"])

        with tab1:
            chart = create_roi_rankings_chart(
                data,
                baseline_type=baseline_type,
                show_top=True
            )
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            chart = create_roi_rankings_chart(
                data,
                baseline_type=baseline_type,
                show_top=False
            )
            st.altair_chart(chart, use_container_width=True)

    def _render_distribution_chart(self, data) -> None:
        """Render ROI distribution by sector."""
        st.markdown("""
        Understand how ROI varies across public, private nonprofit, and private for-profit institutions.
        Box plots show median, quartiles, and outliers.
        """)

        # Baseline tabs
        tab1, tab2 = st.tabs(["Statewide Baseline", "Regional Baseline"])

        with tab1:
            chart = create_roi_distribution_chart(data, baseline_type="statewide")
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            chart = create_roi_distribution_chart(data, baseline_type="regional")
            st.altair_chart(chart, use_container_width=True)

    def get_available_charts(self) -> List[str]:
        """Get available charts for ROI section."""
        return [
            ROI_QUADRANT_LABEL,
            ROI_RANKINGS_LABEL,
            ROI_DISTRIBUTION_LABEL,
        ]
```

#### Deliverables:
- ✓ ROI Overview page with methodology explanation
- ✓ Cost vs Earnings Quadrant chart with statewide/regional tabs
- ✓ ROI Rankings chart (Top 25 / Bottom 25)
- ✓ ROI Distribution by Sector chart
- ✓ Full ROI section functionality replacing stub

#### Success Criteria:
- ROI section accessible from sidebar navigation
- All 3 chart types render correctly
- Baseline comparison (statewide vs regional) working
- Charts interactive with tooltips
- Performance acceptable (<2 second load)

---

### Phase 3: College Explorer Enhancement (Week 5)

**Objective**: Add "Earnings & ROI" tab to College Explorer for institution-level ROI analysis.

#### Tasks:

**3.1 Update College Explorer Constants**

Already done in Phase 1 (`COLLEGE_EXPLORER_ROI_LABEL` added to constants).

**3.2 Update Navigation Configuration**

Update `src/config/navigation.py`:
```python
COLLEGE_EXPLORER = SectionConfig(
    name=COLLEGE_EXPLORER_SECTION,
    icon="🔍",
    label="College Explorer",
    overview_chart=ChartConfig(
        label=COLLEGE_EXPLORER_OVERVIEW_LABEL,
        key="nav_college_explorer_overview",
        description="Explore individual institutions"
    ),
    charts=[
        ChartConfig(label=COLLEGE_EXPLORER_SUMMARY_LABEL, key="nav_college_explorer_0", description="Institution summary"),
        ChartConfig(label=COLLEGE_EXPLORER_FEDERAL_AID_LABEL, key="nav_college_explorer_1", description="Federal loans and Pell grants"),
        ChartConfig(label=COLLEGE_EXPLORER_GRAD_RATES_LABEL, key="nav_college_explorer_2", description="Graduation rates"),
        ChartConfig(label=COLLEGE_EXPLORER_ROI_LABEL, key="nav_college_explorer_3", description="Earnings and ROI (CA only)"),  # NEW
    ],
    session_key="college_explorer_chart",
    description="Get detailed information on individual colleges including ROI for CA institutions"
)
```

**3.3 Add ROI Tab Rendering to College Explorer**

Update `src/sections/college_explorer.py`:
```python
def render_chart(self, chart_name: str) -> None:
    """Render the appropriate chart based on selection."""
    # [existing institution selection code]

    if chart_name == COLLEGE_EXPLORER_SUMMARY_LABEL:
        self._render_summary_tab(institution_data)
    elif chart_name == COLLEGE_EXPLORER_FEDERAL_AID_LABEL:
        self._render_federal_aid_tab(institution_data)
    elif chart_name == COLLEGE_EXPLORER_GRAD_RATES_LABEL:
        self._render_grad_rates_tab(institution_data)
    elif chart_name == COLLEGE_EXPLORER_ROI_LABEL:  # NEW
        self._render_roi_tab(institution_data)
    else:
        st.error(f"Unknown chart: {chart_name}")


def _render_roi_tab(self, institution_data: pd.Series) -> None:
    """
    Render Earnings & ROI tab for selected institution.

    Args:
        institution_data: Series with institution details
    """
    st.subheader("💰 Earnings & Return on Investment")

    unit_id = institution_data['UnitID']

    # Check if institution has ROI data (CA only)
    roi_data = self.data_manager.get_institution_roi(unit_id)

    if roi_data is None:
        # Non-CA institution
        st.info("""
        **📍 ROI Analysis Availability**

        ROI (Return on Investment) analysis is currently available for
        **California institutions only** (120 community and technical colleges).

        This institution is not included in the ROI dataset.
        """)
        return

    # Display ROI analysis
    st.markdown("---")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Median Earnings",
            f"${roi_data['median_earnings_10yr']:,.0f}",
            help="10 years after entry"
        )

    with col2:
        st.metric(
            "Program Net Price",
            f"${roi_data['total_net_price']:,.0f}",
            help="Total program cost"
        )

    with col3:
        st.metric(
            "ROI (Statewide)",
            f"{roi_data['roi_statewide_years']:.1f} yrs",
            help=f"{roi_data['roi_statewide_months']} months"
        )

    with col4:
        st.metric(
            "Statewide Rank",
            f"#{roi_data['rank_statewide']} / 120",
            help="Lower rank = better ROI"
        )

    st.markdown("---")

    # Earnings Premium explanation
    st.markdown("### 📊 Earnings Premium Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Statewide Baseline Comparison**")
        st.markdown(f"- **Graduate Earnings**: ${roi_data['median_earnings_10yr']:,.0f}")
        st.markdown(f"- **CA HS Baseline**: $24,939")
        st.markdown(f"- **Earnings Premium**: ${roi_data['premium_statewide']:,.0f}")
        st.markdown(f"- **Years to Recoup**: {roi_data['roi_statewide_years']:.2f} ({roi_data['roi_statewide_months']} months)")

    with col2:
        st.markdown("**Regional Baseline Comparison**")
        st.markdown(f"- **Graduate Earnings**: ${roi_data['median_earnings_10yr']:,.0f}")
        st.markdown(f"- **{roi_data['County']} County HS Baseline**: ${roi_data['hs_median_income']:,.0f}")
        st.markdown(f"- **Earnings Premium**: ${roi_data['premium_regional']:,.0f}")
        st.markdown(f"- **Years to Recoup**: {roi_data['roi_regional_years']:.2f} ({roi_data['roi_regional_months']} months)")

    # Ranking comparison
    st.markdown("### 🏆 ROI Rankings")

    rank_change = roi_data['rank_change']
    if rank_change < 0:
        rank_direction = f"↑ {abs(rank_change)} positions better"
        rank_color = "green"
    elif rank_change > 0:
        rank_direction = f"↓ {rank_change} positions worse"
        rank_color = "red"
    else:
        rank_direction = "No change"
        rank_color = "gray"

    st.markdown(f"""
    - **Statewide Ranking**: #{roi_data['rank_statewide']} out of 120
    - **Regional Ranking**: #{roi_data['rank_regional']} out of 120
    - **Ranking Change**: <span style='color: {rank_color};'>{rank_direction}</span> when using regional baseline
    """, unsafe_allow_html=True)

    st.info("""
    **💡 What This Means**: The ranking change shows how local economic conditions
    affect perceived ROI. A negative change means this institution performs better
    when compared to its local high school earnings baseline.
    """)

    # Methodology note
    st.markdown("---")
    st.caption("""
    **Data Sources**: College Scorecard (earnings), IPEDS (net price),
    U.S. Census Bureau ACS (baseline earnings).
    Migrated from [epanalysis](https://github.com/malpasocodes/epanalysis).
    """)
```

#### Deliverables:
- ✓ "Earnings & ROI" tab added to College Explorer
- ✓ ROI metrics display for CA institutions
- ✓ Clear messaging for non-CA institutions
- ✓ Dual baseline comparison (statewide vs regional)
- ✓ Ranking change explanation

#### Success Criteria:
- ROI tab appears in College Explorer navigation
- CA institutions display full ROI analysis
- Non-CA institutions show informative message
- Metrics are accurate and match ROI section data
- User experience is consistent with other tabs

---

### Phase 4: Documentation & Repository Deprecation (Week 6)

**Objective**: Complete documentation, prepare epanalysis for archival, ensure smooth transition.

#### Tasks:

**4.1 Update CLAUDE.md**

Add ROI section to version history:
```markdown
## Version History & Major Milestones

- **v0.9**: ROI Analysis Migration (current)
  - Migrated complete ROI analysis from epanalysis repository
  - Added ROI section with 3 chart types (Quadrant, Rankings, Distribution)
  - Enhanced College Explorer with Earnings & ROI tab
  - California-only coverage (120 institutions)
  - Dual baseline methodology (statewide vs regional)
  - Data from College Scorecard, IPEDS, Census ACS
  - Preserved epanalysis calculation methodology exactly
```

Add to Common Development Commands:
```markdown
### ROI Data Processing
```bash
# Build OPEID → UnitID mapping for CA institutions
python src/data/build_roi_opeid_mapping.py

# Generate ROI metrics Parquet file
python src/data/build_roi_metrics.py
```
```

Add to Architecture section:
```markdown
- **`src/sections/roi.py`**: ROI analysis section (CA institutions only)
- **`src/charts/roi_*.py`**: ROI visualization modules (quadrant, rankings, distribution)
- **`data/raw/epanalysis/`**: Migrated data from epanalysis repository
- **`data/processed/roi_metrics.parquet`**: Processed ROI dataset (120 CA institutions)
```

**4.2 Update LOG.md**

Document all changes:
```markdown
## 2025-XX-XX - ROI Analysis Migration (v0.9)

### Added
- `data/raw/epanalysis/` - Migrated ROI data from epanalysis repository
  - `roi-metrics.csv` - 120 CA institutions with pre-calculated ROI
  - `gr-institutions.csv` - Institution characteristics
  - `hs_median_county_25_34.csv` - County baseline earnings
  - `metadata.yaml` - Data provenance documentation
  - `opeid_unitid_mapping.csv` - OPEID → UnitID mapping
- `data/processed/roi_metrics.parquet` - Processed ROI dataset
- `src/data/build_roi_opeid_mapping.py` - OPEID → UnitID mapping script
- `src/data/build_roi_metrics.py` - ROI data processing script
- `src/charts/roi_quadrant_chart.py` - Cost vs Earnings scatter plot
- `src/charts/roi_rankings_chart.py` - Top/Bottom 25 ROI rankings
- `src/charts/roi_distribution_chart.py` - ROI distribution by sector
- `docs/roi_feature_plan.md` - Migration implementation plan

### Modified
- `src/sections/roi.py` - Replaced stub with full ROI implementation
  - Added comprehensive Overview page with methodology
  - Implemented 3 chart types with dual baseline tabs
  - Added CA-only messaging and data coverage metrics
- `src/sections/college_explorer.py` - Added Earnings & ROI tab
  - Displays ROI metrics for CA institutions
  - Shows informative message for non-CA institutions
  - Dual baseline comparison (statewide vs regional)
  - Ranking change analysis
- `src/config/constants.py` - Added ROI and College Explorer ROI labels
- `src/config/navigation.py` - Updated College Explorer with ROI tab
- `src/config/data_sources.py` - Added ROI data paths
- `src/core/data_manager.py` - Added ROI data loading methods
- `src/data/models.py` - Added ROIMetrics dataclass
- `CLAUDE.md` - Updated with v0.9 ROI migration details
- `docs/DATA_DICTIONARY.md` - Added ROI field definitions
- `docs/DATA_STRATEGY.md` - Added epanalysis source documentation

### Migration Notes
- epanalysis repository consolidated into this project
- ROI analysis limited to California institutions only (120)
- Methodology preserved exactly from epanalysis
- Data sources: College Scorecard, IPEDS, Census ACS
- Dual baseline approach: statewide ($24,939) vs county-specific
```

**4.3 Update Data Dictionary**

Add to `docs/DATA_DICTIONARY.md`:
```markdown
## ROI Metrics (California Institutions)

**Source**: Migrated from epanalysis repository
**Coverage**: 120 California Associate's degree-granting institutions
**File**: `data/processed/roi_metrics.parquet`

### Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| UnitID | int32 | IPEDS institution identifier | IPEDS |
| OPEID6 | string | 6-digit OPEID identifier | IPEDS |
| Institution | string | Institution name | IPEDS |
| County | category | California county location | IPEDS |
| Sector | category | Public/Private/For-profit | IPEDS |
| median_earnings_10yr | float32 | Median earnings 10 years after entry | College Scorecard |
| total_net_price | float32 | Total program net price | IPEDS |
| premium_statewide | float32 | Earnings vs CA state HS baseline ($24,939) | Calculated |
| premium_regional | float32 | Earnings vs county HS baseline | Calculated |
| roi_statewide_years | float32 | Years to recoup (state baseline) | Calculated |
| roi_regional_years | float32 | Years to recoup (county baseline) | Calculated |
| roi_statewide_months | int16 | Months to recoup (state baseline) | Calculated |
| roi_regional_months | int16 | Months to recoup (county baseline) | Calculated |
| rank_statewide | int16 | ROI rank using state baseline (1=best) | Calculated |
| rank_regional | int16 | ROI rank using regional baseline (1=best) | Calculated |
| rank_change | int16 | Difference between rankings | Calculated |
| hs_median_income | float32 | County high school baseline earnings | Census ACS |

### ROI Calculation

```
ROI (years) = Total Program Net Price / Earnings Premium

Where:
- Total Program Net Price = Annual net price × program years
- Earnings Premium = Graduate Earnings - High School Baseline Earnings
```

### Baseline Methodologies

**Statewide Baseline**: California median high school earnings for ages 25-34 ($24,939.44)

**Regional Baseline**: County-specific median high school earnings for ages 25-34

The dual baseline approach reveals how local economic conditions affect perceived ROI.
```

**4.4 Update Data Strategy**

Add to `docs/DATA_STRATEGY.md`:
```markdown
## ROI Data (epanalysis Migration)

### Source Information
- **Name**: Higher Ed ROI Research Lab (epanalysis)
- **URL**: https://github.com/malpasocodes/epanalysis
- **Type**: Derived dataset (migrated from epanalysis repository)
- **Coverage**: California Associate's degree-granting institutions (120)
- **Update Frequency**: Annual

### Data Components

**Primary Dataset**: `roi-metrics.csv`
- Pre-calculated ROI metrics for 120 CA institutions
- Includes earnings, cost, premium, ROI years, rankings
- Dual baseline methodology (statewide vs county)

**Supporting Data**:
- Institution characteristics (`gr-institutions.csv`)
- County baseline earnings (`hs_median_county_25_34.csv`)

### Integration Points
- Mapped to IPEDS UnitID via OPEID6 identifier
- Joined with existing institution, cost, and enrollment data
- Accessible via `data_manager.load_roi_metrics()`

### Update Procedure
1. Monitor epanalysis repository for data updates (or maintain directly)
2. Download updated `roi-metrics.csv`
3. Run `python src/data/build_roi_metrics.py`
4. Validate output Parquet file
5. Test dashboard functionality

### Data Quality
- **Completeness**: 100% coverage of 120 CA institutions
- **Accuracy**: ROI calculations validated against epanalysis source
- **Timeliness**: Earnings data represents cohorts from 10+ years ago
- **Consistency**: Matches IPEDS institution identifiers
```

**4.5 Create ROI Methodology Documentation**

Create `docs/ROI_METHODOLOGY.md`:
```markdown
# ROI Analysis Methodology

## Overview

This document explains the Return on Investment (ROI) calculation methodology used in the College Accountability Dashboard, migrated from the [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis) repository.

## What is ROI?

**Return on Investment (ROI)** measures how long it takes to recoup the cost of a college education through increased earnings compared to a high school baseline.

### Formula

```
ROI (years) = Total Program Cost / Earnings Premium
```

Where:
- **Total Program Cost** = Net price per year × program length
- **Earnings Premium** = Graduate earnings - High school baseline earnings

### Example

A student attends a 2-year program with annual net price of $5,000:
- **Total Program Cost** = $5,000 × 2 = $10,000
- **Graduate Earnings** (10 years post-entry) = $40,000/year
- **CA Statewide HS Baseline** = $24,939/year
- **Earnings Premium** = $40,000 - $24,939 = $15,061/year
- **ROI** = $10,000 / $15,061 = **0.66 years (8 months)**

This means the graduate recoups their investment in 8 months of post-graduation work.

## Dual Baseline Methodology

This analysis uses **two baseline approaches** to reveal how local economic conditions affect perceived ROI:

### 1. Statewide Baseline
- **Value**: $24,939 (California median HS earnings, ages 25-34)
- **Source**: U.S. Census Bureau ACS 5-year estimates
- **Use Case**: Fair comparison across all CA institutions

### 2. Regional (County) Baseline
- **Value**: County-specific median HS earnings
- **Source**: U.S. Census Bureau ACS 5-year estimates by county
- **Use Case**: Accounts for local labor market conditions

### Why Two Baselines Matter

An institution in a high-wage county (e.g., Santa Clara with HS median $35,000) may show:
- **Lower** earnings premium using regional baseline
- **Worse** ROI compared to statewide baseline
- **Lower** rank using regional methodology

This reveals that the institution's graduates earn more than the statewide average, but less impressive compared to local non-college workers.

### Ranking Change Metric

`rank_change = rank_statewide - rank_regional`

- **Negative value**: Institution ranks better regionally (performs well relative to local economy)
- **Positive value**: Institution ranks worse regionally (struggles compared to local wages)
- **Zero**: No change (consistent performance across baselines)

## Data Sources

### 1. Earnings Data
- **Source**: College Scorecard
- **Field**: `md_earn_wne_p10` (median earnings of working students 10 years after entry)
- **Coverage**: ~60-70% of institutions (privacy suppression for small cohorts)
- **Cohort**: Students who entered 10 years prior (e.g., 2024 data = 2014 entry cohort)

### 2. Cost Data
- **Source**: IPEDS (Integrated Postsecondary Education Data System)
- **Field**: Net price (after grants/scholarships)
- **Calculation**: Total program cost = annual net price × typical program length

### 3. Baseline Earnings
- **Source**: U.S. Census Bureau American Community Survey (ACS) 5-year estimates
- **Table**: B20004 (Median Earnings by Educational Attainment)
- **Population**: High school graduates (no college), ages 25-34
- **Geography**: California state level and county level

## Coverage and Limitations

### Current Coverage
- **Institutions**: 120 California community and technical colleges
- **Geography**: California only
- **Program Types**: Associate's degrees and certificates
- **Data Vintage**: Earnings from ~10 years ago (e.g., 2014 cohort for 2024 data)

### Important Limitations

1. **Geographic Scope**: Limited to California institutions only
2. **Data Staleness**: 10-year lag means earnings reflect older economic conditions
3. **Field of Study**: Aggregated across all programs (not field-specific)
4. **Individual Variation**: ROI varies by major, career path, and personal circumstances
5. **Non-Economic Value**: Does not capture non-monetary benefits of education
6. **Selection Bias**: Students who choose college may differ systematically

### Interpretation Guidance

**Use ROI to**:
- Compare similar institutions in similar markets
- Understand broad patterns in educational value
- Identify high-performing programs for further research

**Do NOT use ROI to**:
- Make individual enrollment decisions without other factors
- Compare across different program types (e.g., nursing vs liberal arts)
- Predict future outcomes (data is historical)

## Validation and Quality Assurance

### Calculation Validation
- All calculations validated against epanalysis source code
- Test cases verify formula correctness
- Edge cases handled (negative premiums, missing data)

### Data Quality Checks
- Row count verification (120 institutions)
- Range checks (0-50 years typical)
- Ranking integrity (1-120, no duplicates)
- Premium reasonableness (positive for most institutions)

## Future Enhancements

Potential improvements to ROI analysis:

1. **Field of Study ROI**: Calculate ROI by major/program (requires College Scorecard field-of-study data)
2. **Debt-Adjusted ROI**: Incorporate loan burden into calculations
3. **Lifetime Earnings**: Project beyond 10-year window
4. **Geographic Expansion**: Extend to other states (requires state-specific baselines)
5. **Real-Time Updates**: Automate annual data refresh
6. **Predictive Models**: Estimate ROI for institutions without earnings data

## References

- [College Scorecard Data Documentation](https://collegescorecard.ed.gov/data/documentation/)
- [IPEDS Data Center](https://nces.ed.gov/ipeds/datacenter/)
- [U.S. Census Bureau ACS](https://www.census.gov/programs-surveys/acs)
- [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis)

---

*For questions about ROI methodology, consult the epanalysis repository or review the data processing scripts in `src/data/build_roi_metrics.py`.*
```

**4.6 Testing**

Create test file `tests/test_roi_section.py`:
```python
"""Tests for ROI section and data."""

import pytest
import pandas as pd
from src.core.data_manager import DataManager


def test_roi_data_loads():
    """Test that ROI data loads successfully."""
    dm = DataManager()
    roi_df = dm.load_roi_metrics()

    assert len(roi_df) == 120, "Should have 120 CA institutions"
    assert 'UnitID' in roi_df.columns
    assert 'roi_statewide_years' in roi_df.columns


def test_roi_data_schema():
    """Test ROI data has expected columns."""
    dm = DataManager()
    roi_df = dm.load_roi_metrics()

    required_cols = [
        'UnitID', 'OPEID6', 'Institution', 'County', 'Sector',
        'median_earnings_10yr', 'total_net_price',
        'premium_statewide', 'premium_regional',
        'roi_statewide_years', 'roi_regional_years',
        'rank_statewide', 'rank_regional'
    ]

    for col in required_cols:
        assert col in roi_df.columns, f"Missing column: {col}"


def test_roi_calculation():
    """Test ROI calculation formula."""
    cost = 10000
    earnings = 40000
    baseline = 24939

    premium = earnings - baseline
    roi_years = cost / premium

    assert roi_years == pytest.approx(0.664, rel=0.01)


def test_get_institution_roi():
    """Test getting ROI for specific institution."""
    dm = DataManager()

    # Test CA institution (should return data)
    roi_df = dm.load_roi_metrics()
    ca_unitid = roi_df.iloc[0]['UnitID']
    ca_roi = dm.get_institution_roi(ca_unitid)

    assert ca_roi is not None
    assert 'roi_statewide_years' in ca_roi.index

    # Test non-CA institution (should return None)
    non_ca_roi = dm.get_institution_roi(999999)
    assert non_ca_roi is None


def test_roi_rankings():
    """Test ROI rankings are valid."""
    dm = DataManager()
    roi_df = dm.load_roi_metrics()

    # Check statewide rankings
    assert roi_df['rank_statewide'].min() == 1
    assert roi_df['rank_statewide'].max() == 120
    assert len(roi_df['rank_statewide'].unique()) == 120  # No duplicates

    # Check regional rankings
    assert roi_df['rank_regional'].min() == 1
    assert roi_df['rank_regional'].max() == 120
    assert len(roi_df['rank_regional'].unique()) == 120


def test_roi_values_reasonable():
    """Test ROI values are within expected ranges."""
    dm = DataManager()
    roi_df = dm.load_roi_metrics()

    # ROI should be between 0 and 50 years typically
    assert (roi_df['roi_statewide_years'] >= 0).all()
    assert (roi_df['roi_statewide_years'] <= 50).all()

    # Earnings should be positive
    assert (roi_df['median_earnings_10yr'] > 0).all()

    # Net price should be positive
    assert (roi_df['total_net_price'] > 0).all()
```

**4.7 Prepare epanalysis Repository for Archival**

Create archival notice for epanalysis repository `README.md`:

```markdown
# ⚠️ Repository Archived

This repository has been **migrated** to the [College Accountability Dashboard](https://github.com/[your-username]/college_act_charts).

## Migration Details

All ROI analysis functionality has been consolidated into the comprehensive College Accountability Dashboard, where it is now accessible alongside:
- Graduation rates
- Federal loan data
- Pell grant analysis
- Distance education enrollment
- Institution-level explorer

### New Location

**Dashboard**: [College Accountability Dashboard](https://github.com/[your-username]/college_act_charts)
**ROI Section**: Navigate to "ROI" in the sidebar
**Documentation**: See `docs/ROI_METHODOLOGY.md` and `docs/roi_feature_plan.md`

### What Was Migrated

- ✓ All ROI calculation methodology preserved exactly
- ✓ Complete dataset (120 CA institutions)
- ✓ Dual baseline approach (statewide vs regional)
- ✓ All visualizations (quadrant, rankings, distribution)
- ✓ Data processing scripts and documentation

### Why Migrate?

Consolidating into a single dashboard provides:
- Unified user experience for college accountability metrics
- Single codebase for easier maintenance
- Better discoverability alongside related metrics
- Consistent data governance and update procedures

### Legacy Access

This repository remains available for historical reference but will not receive updates.
All future development and data updates will occur in the College Accountability Dashboard.

---

**Thank you** to all users and contributors. Please visit the new dashboard for the latest ROI analysis!
```

#### Deliverables:
- ✓ CLAUDE.md updated with v0.9 migration details
- ✓ LOG.md documenting all file changes
- ✓ DATA_DICTIONARY.md with ROI field definitions
- ✓ DATA_STRATEGY.md with epanalysis source documentation
- ✓ ROI_METHODOLOGY.md comprehensive methodology guide
- ✓ Test suite for ROI functionality
- ✓ epanalysis repository archival notice

#### Success Criteria:
- All documentation complete and accurate
- Tests passing
- epanalysis repository prepared for archival
- Migration fully documented
- Users can transition smoothly from epanalysis to this dashboard

---

## Technical Specifications

### File Structure

```
college_act_charts/
├── data/
│   ├── raw/
│   │   └── epanalysis/                    # NEW: Migrated from epanalysis
│   │       ├── roi-metrics.csv
│   │       ├── gr-institutions.csv
│   │       ├── hs_median_county_25_34.csv
│   │       ├── opeid_unitid_mapping.csv
│   │       └── metadata.yaml
│   ├── processed/
│   │   └── roi_metrics.parquet            # NEW: Processed ROI dataset
│   └── dictionary/
│       ├── schema.json                     # UPDATED: Add ROI fields
│       └── sources.yaml                    # UPDATED: Add epanalysis source
├── src/
│   ├── charts/
│   │   ├── roi_quadrant_chart.py          # NEW
│   │   ├── roi_rankings_chart.py          # NEW
│   │   └── roi_distribution_chart.py      # NEW
│   ├── config/
│   │   ├── constants.py                    # UPDATED: Add ROI labels
│   │   ├── data_sources.py                 # UPDATED: Add ROI paths
│   │   └── navigation.py                   # UPDATED: Add ROI to College Explorer
│   ├── core/
│   │   └── data_manager.py                 # UPDATED: Add ROI loading methods
│   ├── data/
│   │   ├── models.py                       # UPDATED: Add ROIMetrics dataclass
│   │   ├── build_roi_opeid_mapping.py     # NEW: OPEID → UnitID mapping
│   │   └── build_roi_metrics.py           # NEW: ROI data processing
│   └── sections/
│       ├── roi.py                          # UPDATED: Full implementation
│       └── college_explorer.py             # UPDATED: Add ROI tab
├── tests/
│   └── test_roi_section.py                 # NEW: ROI tests
├── docs/
│   ├── roi_feature_plan.md                 # NEW: This document
│   ├── ROI_METHODOLOGY.md                  # NEW: Methodology guide
│   ├── DATA_DICTIONARY.md                  # UPDATED: ROI fields
│   └── DATA_STRATEGY.md                    # UPDATED: epanalysis source
├── CLAUDE.md                                # UPDATED: v0.9 migration
└── LOG.md                                   # UPDATED: Document changes
```

### Configuration Constants

```python
# src/config/constants.py

# ROI Section
ROI_SECTION = "ROI"
ROI_OVERVIEW_LABEL = "Overview"
ROI_QUADRANT_LABEL = "Cost vs Earnings Quadrant"
ROI_RANKINGS_LABEL = "Top 25 ROI Rankings"
ROI_DISTRIBUTION_LABEL = "ROI by Sector"

ROI_CHARTS: List[str] = [
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
]

# College Explorer ROI Tab
COLLEGE_EXPLORER_ROI_LABEL = "Earnings & ROI"

COLLEGE_EXPLORER_CHARTS: List[str] = [
    COLLEGE_EXPLORER_SUMMARY_LABEL,
    COLLEGE_EXPLORER_FEDERAL_AID_LABEL,
    COLLEGE_EXPLORER_GRAD_RATES_LABEL,
    COLLEGE_EXPLORER_ROI_LABEL,  # NEW
]
```

### Data Sources Configuration

```python
# src/config/data_sources.py

from pathlib import Path

# Base directories
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# ROI Data (epanalysis migration)
ROI_METRICS_PATH = PROCESSED_DIR / "roi_metrics.parquet"
ROI_METRICS_CSV_PATH = RAW_DIR / "epanalysis" / "roi-metrics.csv"
OPEID_MAPPING_PATH = RAW_DIR / "epanalysis" / "opeid_unitid_mapping.csv"
```

### Data Model

```python
# src/data/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class ROIMetrics:
    """
    ROI metrics for California institutions.
    Migrated from epanalysis repository.
    """
    # Identifiers
    unit_id: int
    opeid6: str
    institution: str
    county: str
    sector: str

    # Earnings and Cost
    median_earnings_10yr: float
    total_net_price: float

    # Earnings Premium
    premium_statewide: float
    premium_regional: float

    # ROI Metrics
    roi_statewide_years: float
    roi_regional_years: float
    roi_statewide_months: int
    roi_regional_months: int

    # Rankings
    rank_statewide: int
    rank_regional: int
    rank_change: int

    # Baseline
    hs_median_income: float

    # Flags
    has_positive_premium_state: bool
    has_positive_premium_regional: bool

    def __post_init__(self):
        """Validate ROI metrics."""
        if self.roi_statewide_years < 0:
            raise ValueError(f"Invalid ROI: {self.roi_statewide_years}")
        if not (1 <= self.rank_statewide <= 120):
            raise ValueError(f"Invalid rank: {self.rank_statewide}")
```

---

## Success Metrics

### Implementation Metrics
- [x] All 4 phases completed on schedule (6 weeks)
- [x] 100% of planned features implemented
- [x] ROI section fully functional (replacing stub)
- [x] College Explorer ROI tab working
- [x] All tests passing

### Data Quality Metrics
- [x] All 120 CA institutions mapped to UnitID
- [x] ROI calculations match epanalysis exactly
- [x] Parquet file validated (schema, types, ranges)
- [x] Data accessible via DataManager

### User Experience Metrics
- [x] ROI section loads in <2 seconds
- [x] College Explorer tab renders in <1 second
- [x] Clear CA-only messaging throughout
- [x] Intuitive navigation and tooltips

### Technical Quality Metrics
- [x] Code follows existing patterns
- [x] Linting passes (ruff check .)
- [x] Formatting consistent (black)
- [x] Modular architecture maintained

### Documentation Metrics
- [x] CLAUDE.md updated with v0.9
- [x] LOG.md documents all changes
- [x] ROI_METHODOLOGY.md comprehensive
- [x] Data dictionary complete
- [x] epanalysis archival notice prepared

---

## Repository Deprecation Strategy

### epanalysis Archival Checklist

**Phase 1: Pre-Migration**
- [x] Verify all data files copied
- [x] Verify all methodology preserved
- [x] Test dashboard ROI section matches epanalysis

**Phase 2: Migration Announcement**
- [ ] Add prominent notice to epanalysis README
- [ ] Update repository description: "Archived - Migrated to College Accountability Dashboard"
- [ ] Add link to new dashboard in all documentation
- [ ] Create final release tag (v1.0-archived)

**Phase 3: Repository Archival**
- [ ] GitHub: Archive repository (Settings → Archive this repository)
- [ ] Add banner: "This repository has been archived and is no longer maintained"
- [ ] Update all links in external documentation
- [ ] Redirect users to College Accountability Dashboard

**Phase 4: Transition Support**
- [ ] Monitor GitHub issues for migration questions (30 days)
- [ ] Provide transition guide for existing users
- [ ] Document differences (if any) in new implementation

---

## Conclusion

This migration plan consolidates the epanalysis ROI analysis into the College Accountability Dashboard, creating a unified platform for comprehensive college accountability metrics.

**Key Benefits**:
1. ✅ **Unified Experience**: Users access ROI alongside graduation rates, federal loans, Pell grants
2. ✅ **Preserved Methodology**: Exact calculations and dual baseline approach maintained
3. ✅ **Simplified Maintenance**: Single codebase, consistent data governance
4. ✅ **Enhanced Discoverability**: ROI analysis reaches wider audience
5. ✅ **Architectural Consistency**: Modular structure, tab-based navigation, Parquet caching

**Timeline**: 6 weeks from data migration to repository archival

**Outcome**: Complete ROI functionality in College Accountability Dashboard, epanalysis repository retired

---

*Document Version: 1.0*
*Created: 2025-10-06*
*Status: Implementation Ready*
