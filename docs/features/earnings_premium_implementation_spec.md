# Earnings Premium Institutional Analysis - Implementation Specification

## Project Overview

Add a new Section 8 to the edu-accountability.com dashboard that provides institutional-level Earnings Premium (EP) risk assessment for all U.S. colleges and universities. This feature will help institutions prepare for the July 1, 2026 Earnings Premium requirements established by the "Big Beautiful Bill."

## Background Context

### Regulatory Context
- **Effective Date:** July 1, 2026
- **Requirement:** All undergraduate and graduate degree programs must demonstrate that graduates earn MORE than the median earnings of high school graduates (aged 25-34) in their state
- **Consequence:** Programs that fail the earnings premium test for 2 out of 3 consecutive years lose Title IV federal aid eligibility
- **Scope:** Affects 6,000+ institutions nationwide

### What This Feature Provides
- **Institution-level risk screening** (not program-level, which requires data not publicly available)
- **Comparative analysis** across states, sectors, and peer institutions
- **Early warning system** for institutions to identify potential compliance issues
- **Strategic planning tool** for institutional leadership

### Key Limitation to Communicate
This analysis uses institution-level median earnings (aggregated across all programs) compared to state thresholds. Actual EP testing will occur at the individual program level using IRS/SSA data not publicly available. This tool provides directional risk assessment for planning purposes.

---

## Data Requirements

### Required Datasets

#### 1. State Earnings Premium Thresholds
**Source:** Federal Register (December 31, 2024)
**Data Points:** All 50 states + DC + national threshold

```
State,Threshold
Alabama,27836
Alaska,35457
Arizona,32284
Arkansas,28502
California,32476
Colorado,35571
Connecticut,33286
Delaware,31316
District of Columbia,32592
Florida,29609
Georgia,29609
Hawaii,34203
Idaho,33397
Illinois,30793
Indiana,31316
Iowa,34203
Kansas,30782
Kentucky,28996
Louisiana,28996
Maine,32311
Maryland,33397
Massachusetts,35438
Michigan,28996
Minnesota,34795
Mississippi,27362
Missouri,30156
Montana,30058
Nebraska,31316
Nevada,33172
New Hampshire,37850
New Jersey,32832
New Mexico,27836
New York,30793
North Carolina,29344
North Dakota,34203
Ohio,30793
Oklahoma,29810
Oregon,31695
Pennsylvania,31727
Rhode Island,34203
South Carolina,30156
South Dakota,31385
Tennessee,29609
Texas,31171
Utah,34795
Vermont,33397
Virginia,33043
Washington,35027
West Virginia,28996
Wisconsin,33397
Wyoming,36480
United States (National),31269
```

#### 2. Institution Data from College Scorecard
**Source:** College Scorecard API or data files (https://collegescorecard.ed.gov/data/)

**Key Fields Needed:**
- `UNITID` - Institution identifier (links to IPEDS)
- `INSTNM` - Institution name
- `STABBR` - State abbreviation
- `MD_EARN_WNE_P10` - Median earnings 10 years after entry (primary metric)
- `MD_EARN_WNE_P6` - Median earnings 6 years after entry (backup/additional metric)

**Notes:**
- Earnings are for students who received federal aid
- Measured as years after enrollment entry, not completion
- Use 10-year earnings as primary metric (most stable, complete data)

#### 3. Institution Characteristics from IPEDS
**Source:** IPEDS data center (https://nces.ed.gov/ipeds/)

**Key Fields Needed:**
- `UNITID` - Institution identifier
- `INSTNM` - Institution name
- `STABBR` - State abbreviation
- `SECTOR` - Institutional sector/control
  - 1 = Public, 4-year or above
  - 2 = Private nonprofit, 4-year or above
  - 3 = Private for-profit, 4-year or above
  - 4 = Public, 2-year
  - 5 = Private nonprofit, 2-year
  - 6 = Private for-profit, 2-year
  - 7 = Public, less than 2-year
  - 8 = Private nonprofit, less than 2-year
  - 9 = Private for-profit, less than 2-year
- `LOCALE` - Urbanization code (optional, for additional analysis)
- `LATITUDE` - Latitude (for mapping)
- `LONGITUDE` - Longitude (for mapping)

#### 4. Additional Context Data (From Existing Dashboard)
These should already be available in the current dashboard:
- Enrollment data (for sizing visualizations)
- Graduation rates (for vulnerability score)
- Federal aid dependency (for vulnerability score)
- Institution costs (for vulnerability score)

### Data Integration Steps

1. **Load State Thresholds**
   - Create a lookup table: `state_code -> threshold_amount`

2. **Load College Scorecard Data**
   - Filter to institutions with valid earnings data
   - Extract median earnings (10-year preferred)

3. **Load IPEDS Data**
   - Get institution characteristics
   - Link to Scorecard data via UNITID

4. **Merge Datasets**
   ```python
   institutions = scorecard_data
       .merge(ipeds_data, on='UNITID', how='left')
       .merge(state_thresholds, left_on='state', right_on='state_code', how='left')
   ```

5. **Calculate Risk Metrics**
   ```python
   institutions['earnings_margin'] = (
       (institutions['median_earnings'] - institutions['state_threshold']) 
       / institutions['state_threshold']
   )
   
   institutions['risk_level'] = institutions['earnings_margin'].apply(categorize_risk)
   ```

---

## Feature Specifications

### Section 8: Earnings Premium Institutional Analysis

Create a new major section in the dashboard navigation.

#### Navigation Structure
```
├── Section 8: Earnings Premium Analysis 🎯
    ├── 8.1 Overview & Risk Map
    ├── 8.2 Institution Lookup
    ├── 8.3 State Analysis
    ├── 8.4 Sector Comparison
    └── 8.5 Methodology & Limitations
```

---

### 8.1 Overview & Risk Map

**Purpose:** Provide a high-level national view of institutional EP readiness

#### Components

##### A. Summary Statistics Cards (Top of Page)

Display 4 cards in a row:

```
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  Total Institutions │  │   At Risk (High +   │  │  Critical Risk      │  │   Avg Earnings      │
│                     │  │     Critical)        │  │  (Below Threshold)  │  │     Margin          │
│      6,234          │  │      1,247 (20%)    │  │      312 (5%)       │  │      +42%           │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

**Metrics to Calculate:**
- Total institutions with earnings data
- Number and percentage in each risk category
- Number and percentage below threshold
- Average earnings margin across all institutions

##### B. Interactive National Scatter Plot

**Visualization Type:** Plotly scatter plot

**Axes:**
- X-axis: State EP Threshold (dollars)
- Y-axis: Institution Median Earnings (dollars)
- Range: $25,000 to $80,000 for both axes (adjust based on data)

**Visual Elements:**
- **Each dot** = one institution
- **Color** = risk level
  - Green: Low Risk (margin > 50%)
  - Yellow: Moderate Risk (margin 20-50%)
  - Orange: High Risk (margin 0-20%)
  - Red: Critical Risk (margin < 0%, below threshold)
- **Size** = enrollment (optional, or keep uniform size for clarity)
- **Reference line** = diagonal line from origin at 45° (where earnings = threshold)

**Interactivity:**
- Hover tooltip shows:
  - Institution name
  - State
  - Median earnings
  - State threshold
  - Earnings margin (%)
  - Risk level
- Click on dot to navigate to institution detail page
- Filter controls (see below)

**Filter Controls (Side Panel or Top):**
- **Risk Level:** Multi-select dropdown (Low, Moderate, High, Critical)
- **Sector:** Multi-select (Public 4-year, Private nonprofit 4-year, For-profit, Public 2-year, etc.)
- **State:** Multi-select dropdown with all states
- **Region:** Dropdown (Northeast, Southeast, Midwest, Southwest, West)
- **Earnings Range:** Slider (min to max institutional earnings)
- **Enrollment Range:** Slider (small, medium, large)

**Download Options:**
- "Download filtered data as CSV" button
- Include all visible institutions with key metrics

##### C. Risk Distribution Summary

**Visualization Type:** Horizontal bar chart or stacked bar chart

Show distribution of institutions across risk levels:

```
Low Risk      ████████████████████████████ 53% (3,305 institutions)
Moderate Risk ███████████████ 30% (1,870 institutions)
High Risk     ██████ 12% (748 institutions)
Critical Risk ██ 5% (311 institutions)
```

**Table Below Chart:**

| Risk Level | # Institutions | % of Total | Avg Earnings | Avg State Threshold | Avg Margin |
|------------|----------------|------------|--------------|---------------------|------------|
| Low Risk | 3,305 | 53% | $58,200 | $31,500 | +85% |
| Moderate Risk | 1,870 | 30% | $42,100 | $31,800 | +32% |
| High Risk | 748 | 12% | $34,400 | $32,200 | +7% |
| Critical Risk | 311 | 5% | $27,800 | $31,400 | -11% |

**Calculations:**
```python
def categorize_risk(margin):
    if margin > 0.50:
        return 'Low Risk'
    elif margin > 0.20:
        return 'Moderate Risk'
    elif margin > 0:
        return 'High Risk'
    else:
        return 'Critical Risk'
```

##### D. Key Findings / Insights Section

Text box with 3-5 automatically generated insights based on the data:

```
📊 KEY FINDINGS

• XX% of institutions have median earnings below their state threshold, 
  placing them at critical risk for EP compliance issues.

• For-profit institutions show the highest risk concentration, with XX% 
  in high or critical risk categories.

• [State with most critical institutions] has the highest number of 
  at-risk institutions (XX), while [state] has the lowest (XX).

• The average earnings margin is lowest in [region] (XX%) and highest 
  in [region] (XX%).

• Public 2-year institutions face particular challenges, with XX% 
  below their state thresholds.
```

---

### 8.2 Institution Lookup

**Purpose:** Allow users to search for specific institutions and see detailed risk assessment

#### Components

##### A. Search Interface

**Search Box:**
- Autocomplete search field
- Search by institution name
- Shows top 10 matching results as user types
- Clicking result loads institution card

##### B. Institution Risk Card

When institution is selected, display a prominent card:

```
┌─────────────────────────────────────────────────────────────────┐
│ UCLA (University of California-Los Angeles)                     │
│ Los Angeles, CA • Public 4-year • 31,068 undergraduates        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ EARNINGS PREMIUM RISK ASSESSMENT                                │
│                                                                 │
│ Median Earnings (10 years): $70,700                            │
│ California State Threshold:  $32,476                           │
│ Earnings Margin:             +$38,224 (118%)                   │
│                                                                 │
│ Risk Level: ● LOW RISK                                         │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │     [====================================|           ]    │   │
│ │   Critical  High   Moderate      Low    ↑               │   │
│ │                                       UCLA              │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ PEER COMPARISON (Public 4-year institutions in California)     │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Institution              Earnings    Margin    Risk       │  │
│ │ UC Berkeley             $76,200      +135%     Low       │  │
│ │ USC                     $74,000      +128%     Low       │  │
│ │ UCLA (You)              $70,700      +118%     Low       │  │
│ │ UC San Diego            $68,400      +111%     Low       │  │
│ │ Cal Poly SLO            $65,200      +101%     Low       │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ADDITIONAL CONTEXT                                              │
│ • Graduation Rate: 91% (vs 53% national avg)                  │
│ • Federal Aid Dependency: 45% of students receive Title IV     │
│ • Median Debt: $19,500                                         │
│                                                                 │
│ ⚠️  IMPORTANT LIMITATION                                        │
│ This assessment uses institution-level earnings data. Individual│
│ programs may vary significantly. Actual EP testing will assess  │
│ each degree program separately.                                 │
│                                                                 │
│ [View Full Institution Profile in Section 5] →                 │
└─────────────────────────────────────────────────────────────────┘
```

**Card Sections:**

1. **Header:** Institution name, location, sector, enrollment
2. **Risk Assessment:** Core EP metrics with visual indicator
3. **Risk Level Indicator:** Visual scale showing position
4. **Peer Comparison Table:** 5-10 similar institutions for context
5. **Additional Context:** Other relevant metrics from existing dashboard
6. **Limitation Notice:** Clear disclaimer about data limitations
7. **Link:** Connect to existing Institution Deep Dive (Section 5)

**Peer Institution Selection Logic:**
```python
def get_peer_institutions(institution, n=5):
    # Filter to same state and sector
    peers = institutions[
        (institutions['state'] == institution['state']) &
        (institutions['sector'] == institution['sector']) &
        (institutions['UNITID'] != institution['UNITID'])
    ]
    
    # Sort by enrollment similarity, take top n
    peers['enrollment_diff'] = abs(peers['enrollment'] - institution['enrollment'])
    peers = peers.nsmallest(n, 'enrollment_diff')
    
    # Add the selected institution
    comparison = pd.concat([institution, peers])
    comparison = comparison.sort_values('median_earnings', ascending=False)
    
    return comparison
```

##### C. Bulk Lookup Option

**Feature:** Allow users to enter multiple institutions at once
- Text area input: paste list of institution names (one per line)
- Or upload CSV file with institution names
- Returns table with key metrics for all institutions
- Download results as CSV

---

### 8.3 State Analysis

**Purpose:** Show EP risk landscape for each state

#### Components

##### A. State Selector

Dropdown menu with all 50 states + DC + "National Overview"

##### B. State Summary Card

When state is selected:

```
┌─────────────────────────────────────────────────────────────────┐
│ CALIFORNIA Earnings Premium Analysis                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ State EP Threshold: $32,476 (ranked #8 highest nationally)     │
│                                                                 │
│ Institutions in State: 412                                      │
│ • Low Risk:        198 (48%)                                   │
│ • Moderate Risk:   124 (30%)                                   │
│ • High Risk:        67 (16%)                                   │
│ • Critical Risk:    23 (6%)                                    │
│                                                                 │
│ Median Institutional Earnings: $42,100                          │
│ Average Margin: +30%                                            │
└─────────────────────────────────────────────────────────────────┘
```

##### C. State Institutions Table

**Sortable, filterable table showing all institutions in the state:**

| Institution | Sector | Median Earnings | Margin | Risk Level | Enrollment |
|-------------|--------|-----------------|--------|------------|------------|
| Stanford University | Private nonprofit 4-yr | $94,000 | +189% | Low | 7,087 |
| UC Berkeley | Public 4-yr | $76,200 | +135% | Low | 31,780 |
| ... | ... | ... | ... | ... | ... |
| [At-risk institution] | For-profit 4-yr | $28,400 | -13% | Critical | 1,234 |

**Features:**
- Sort by any column
- Filter by sector
- Filter by risk level
- Search within state
- Highlight institutions below threshold
- Download state data as CSV

##### D. State Comparison Section

**Bar chart comparing the selected state to national averages:**

Show side-by-side comparison:
- State threshold vs national threshold
- % at risk in state vs national %
- Median institutional earnings in state vs national

##### E. State Map Position

Small U.S. map showing:
- Selected state highlighted
- Color gradient showing threshold levels across all states
- Click other states to navigate

---

### 8.4 Sector Comparison

**Purpose:** Compare EP risk across institutional types

#### Components

##### A. Sector Overview Cards

Grid of cards (2x3 or 3x2 layout):

```
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ Public 4-year            │  │ Private Nonprofit 4-year │  │ For-Profit 4-year        │
│                          │  │                          │  │                          │
│ Institutions: 732        │  │ Institutions: 1,584      │  │ Institutions: 489        │
│ At Risk: 15%             │  │ At Risk: 12%             │  │ At Risk: 58%             │
│ Avg Margin: +65%         │  │ Avg Margin: +71%         │  │ Avg Margin: +8%          │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│ Public 2-year            │  │ Private Nonprofit 2-year │  │ For-Profit 2-year        │
│                          │  │                          │  │                          │
│ Institutions: 968        │  │ Institutions: 87         │  │ Institutions: 234        │
│ At Risk: 42%             │  │ At Risk: 28%             │  │ At Risk: 71%             │
│ Avg Margin: +12%         │  │ Avg Margin: +35%         │  │ Avg Margin: -5%          │
└──────────────────────────┘  └──────────────────────────┘  └──────────────────────────┘
```

##### B. Sector Comparison Chart

**Visualization Type:** Grouped bar chart

X-axis: Sector types
Y-axis: Percentage
Bars grouped by risk level (Low, Moderate, High, Critical)

Shows distribution of risk across sectors visually.

##### C. Sector Deep Dive Tables

For each sector, provide a table of institutions:

**Dropdown selector:** Choose sector to explore

**Table:** Top and bottom performers in that sector
- Top 10 by earnings margin (success stories)
- Bottom 10 by earnings margin (highest risk)

**Columns:**
- Institution name
- State
- Median earnings
- State threshold
- Margin
- Risk level
- Enrollment

---

### 8.5 Methodology & Limitations

**Purpose:** Transparency about data sources, calculations, and limitations

#### Content Sections

##### A. Introduction

Text explaining what this tool does and doesn't do:

```markdown
## What This Tool Provides

This Earnings Premium Analysis provides **institutional-level risk assessment** 
to help colleges and universities prepare for the July 1, 2026 Earnings Premium 
requirements. It uses publicly available data to estimate which institutions may 
face compliance challenges.

## What This Tool Does NOT Provide

This tool **does not** provide program-level determinations, which is how the 
actual EP regulations will assess institutions. Individual degree programs within 
an institution may perform very differently from the institutional average.
```

##### B. Data Sources

Detailed table:

| Data Element | Source | Update Frequency | Notes |
|--------------|--------|------------------|-------|
| State EP Thresholds | Federal Register (12/31/2024) | Annual | Based on Census ACS data |
| Institution Median Earnings | College Scorecard | Annual | 10 years after enrollment entry |
| Institution Characteristics | IPEDS | Annual | Sector, location, enrollment |
| Graduation Rates | IPEDS | Annual | Used in vulnerability score |
| Federal Aid Data | FSA Data Center | Annual | Used in vulnerability score |

##### C. Calculation Methodology

```markdown
## Risk Level Calculation

For each institution, we calculate the **Earnings Margin**:

Earnings Margin = (Institution Median Earnings - State Threshold) / State Threshold

Risk levels are assigned as follows:
- **Low Risk:** Margin > 50%
- **Moderate Risk:** Margin between 20% and 50%
- **High Risk:** Margin between 0% and 20%
- **Critical Risk:** Margin < 0% (below threshold)

## Example Calculation

Institution: UCLA
- Median Earnings (10 years): $70,700
- California Threshold: $32,476
- Earnings Margin: ($70,700 - $32,476) / $32,476 = 1.18 = 118%
- Risk Level: Low Risk

## Vulnerability Score (Optional Advanced Feature)

The vulnerability score combines multiple risk factors:
- EP Risk Level: 40% weight
- Federal Aid Dependency: 25% weight
- Graduation Rate: 20% weight
- Cost Level: 15% weight

Institutions with high EP risk AND high federal aid dependency AND low 
graduation rates face the greatest overall vulnerability.
```

##### D. Key Limitations

**Prominent callout box:**

```
⚠️ CRITICAL LIMITATIONS

1. PROGRAM vs. INSTITUTION LEVEL
   This analysis uses institution-level median earnings (all programs combined).
   Actual EP testing will assess INDIVIDUAL PROGRAMS separately. An institution
   with strong overall earnings may still have specific programs that fail.

2. DATA TIMING
   College Scorecard measures earnings 10 years after enrollment ENTRY, not
   completion. EP regulations measure earnings 2, 3, and 4 years after COMPLETION.
   These timeframes differ significantly.

3. DATA SOURCE
   This analysis uses College Scorecard data. The Department of Education will
   use IRS and Social Security Administration wage records for actual EP
   determinations. These sources may yield different results.

4. EARNINGS PREMIUM ONLY
   This tool only assesses the Earnings Premium test. Programs must ALSO pass
   the Debt-to-Earnings ratio test to maintain Title IV eligibility.

5. COHORT COVERAGE
   College Scorecard data only includes students who received federal aid.
   EP regulations will assess all program completers who received Title IV funds.

This tool provides DIRECTIONAL GUIDANCE for institutional planning. It is NOT
a substitute for detailed program-level analysis or official ED determinations.
```

##### E. FAQs

Common questions with answers:

```markdown
## Frequently Asked Questions

**Q: Why does my institution show "No Data Available"?**
A: Some institutions don't have earnings data in College Scorecard due to small 
cohort sizes or privacy suppression requirements.

**Q: Our institution shows Low Risk, but we have programs we're concerned about. 
What should we do?**
A: This tool shows institutional average. You should conduct internal program-level 
analysis using your own graduate tracking data to identify specific at-risk programs.

**Q: When will the Department of Education release official determinations?**
A: ED will begin publishing official EP metrics in early 2025. The first year 
programs may become ineligible is 2026.

**Q: Can I use this data for external reporting or board presentations?**
A: Yes, but please include appropriate disclaimers about data limitations. We 
recommend using phrases like "preliminary risk assessment" or "directional indicator."

**Q: How often is this data updated?**
A: We update the analysis annually when new College Scorecard data is released, 
typically in September/October.
```

##### F. Additional Resources

Links to:
- Federal Register notice with official thresholds
- Department of Education GE/FVT resources
- College Scorecard data dictionary
- IPEDS data center
- Contact email for questions

---

## Technical Implementation Notes

### Technology Stack

Based on existing dashboard (assume Streamlit + Python):
- **Frontend:** Streamlit
- **Visualizations:** Plotly (interactive charts), Matplotlib/Seaborn (static charts)
- **Data Processing:** Pandas, NumPy
- **Data Storage:** Parquet files (consistent with existing dashboard)
- **Deployment:** Render (consistent with current hosting)

### File Structure

Suggested organization within existing dashboard:

```
college_act_charts/
├── src/
│   ├── sections/
│   │   ├── earnings_premium/          # NEW
│   │   │   ├── __init__.py
│   │   │   ├── overview.py           # 8.1 Overview & Risk Map
│   │   │   ├── institution_lookup.py  # 8.2 Institution Lookup
│   │   │   ├── state_analysis.py      # 8.3 State Analysis
│   │   │   ├── sector_comparison.py   # 8.4 Sector Comparison
│   │   │   └── methodology.py         # 8.5 Methodology
│   │   └── [existing sections...]
│   ├── charts/
│   │   ├── ep_visualizations.py       # NEW - EP-specific charts
│   │   └── [existing chart modules...]
│   ├── core/
│   │   ├── ep_data_loader.py          # NEW - EP data loading
│   │   ├── ep_calculations.py         # NEW - Risk metrics
│   │   └── [existing core modules...]
│   └── config/
│       ├── navigation.py              # UPDATE - Add Section 8
│       └── [existing config...]
├── data/
│   ├── raw/
│   │   ├── ep_thresholds/             # NEW
│   │   │   └── state_thresholds_2024.csv
│   │   ├── college_scorecard/
│   │   │   └── [earnings data]
│   │   └── [existing raw data...]
│   ├── processed/
│   │   ├── ep_analysis.parquet        # NEW - Processed EP data
│   │   └── [existing processed data...]
│   └── dictionary/
│       ├── ep_data_dictionary.yaml    # NEW
│       └── [existing dictionaries...]
└── app.py                              # UPDATE - Add Section 8 routing
```

### Data Processing Pipeline

Create a new data processing script: `src/data/build_ep_metrics.py`

```python
"""
Build Earnings Premium analysis dataset
Run this script to regenerate processed EP data from raw sources
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_state_thresholds():
    """Load state EP thresholds from CSV"""
    df = pd.read_csv('data/raw/ep_thresholds/state_thresholds_2024.csv')
    return df

def load_scorecard_earnings():
    """Load institution earnings from College Scorecard"""
    # Adjust path based on actual Scorecard data location
    df = pd.read_csv('data/raw/college_scorecard/earnings_data.csv')
    
    # Select relevant columns
    df = df[[
        'UNITID',
        'INSTNM', 
        'STABBR',
        'MD_EARN_WNE_P10',  # Median earnings 10 years after entry
        'MD_EARN_WNE_P6'    # Median earnings 6 years after entry
    ]]
    
    # Convert to numeric, handling missing/suppressed data
    df['MD_EARN_WNE_P10'] = pd.to_numeric(df['MD_EARN_WNE_P10'], errors='coerce')
    df['MD_EARN_WNE_P6'] = pd.to_numeric(df['MD_EARN_WNE_P6'], errors='coerce')
    
    return df

def load_ipeds_characteristics():
    """Load institution characteristics from IPEDS"""
    # Adjust path based on actual IPEDS data location
    df = pd.read_csv('data/raw/ipeds/institution_characteristics.csv')
    
    # Select relevant columns
    df = df[[
        'UNITID',
        'INSTNM',
        'STABBR',
        'SECTOR',
        'LOCALE',
        'LATITUDE',
        'LONGITUDE',
        'ENROLLMENT'  # Total enrollment
    ]]
    
    return df

def merge_datasets():
    """Merge all datasets"""
    thresholds = load_state_thresholds()
    earnings = load_scorecard_earnings()
    characteristics = load_ipeds_characteristics()
    
    # Merge earnings and characteristics
    df = earnings.merge(
        characteristics,
        on=['UNITID', 'INSTNM', 'STABBR'],
        how='left'
    )
    
    # Merge with state thresholds
    df = df.merge(
        thresholds,
        left_on='STABBR',
        right_on='State',
        how='left'
    )
    
    # Use 10-year earnings as primary, fall back to 6-year if missing
    df['median_earnings'] = df['MD_EARN_WNE_P10'].fillna(df['MD_EARN_WNE_P6'])
    
    return df

def calculate_risk_metrics(df):
    """Calculate EP risk metrics"""
    
    # Earnings margin
    df['earnings_margin'] = (
        (df['median_earnings'] - df['Threshold']) / df['Threshold']
    )
    
    # Earnings margin percentage (for display)
    df['earnings_margin_pct'] = df['earnings_margin'] * 100
    
    # Risk level categorization
    def categorize_risk(margin):
        if pd.isna(margin):
            return 'No Data'
        elif margin > 0.50:
            return 'Low Risk'
        elif margin > 0.20:
            return 'Moderate Risk'
        elif margin > 0:
            return 'High Risk'
        else:
            return 'Critical Risk'
    
    df['risk_level'] = df['earnings_margin'].apply(categorize_risk)
    
    # Risk level numeric (for sorting/filtering)
    risk_level_map = {
        'Low Risk': 1,
        'Moderate Risk': 2,
        'High Risk': 3,
        'Critical Risk': 4,
        'No Data': 5
    }
    df['risk_level_numeric'] = df['risk_level'].map(risk_level_map)
    
    # Sector name (readable labels)
    sector_map = {
        1: 'Public 4-year',
        2: 'Private nonprofit 4-year',
        3: 'For-profit 4-year',
        4: 'Public 2-year',
        5: 'Private nonprofit 2-year',
        6: 'For-profit 2-year',
        7: 'Public less-than-2-year',
        8: 'Private nonprofit less-than-2-year',
        9: 'For-profit less-than-2-year'
    }
    df['sector_name'] = df['SECTOR'].map(sector_map)
    
    return df

def add_additional_metrics(df):
    """Add metrics from existing dashboard sections"""
    # Load graduation rates
    grad_rates = pd.read_parquet('data/processed/graduation_rates.parquet')
    df = df.merge(
        grad_rates[['UNITID', 'graduation_rate']],
        on='UNITID',
        how='left'
    )
    
    # Load federal aid dependency
    fed_aid = pd.read_parquet('data/processed/federal_aid.parquet')
    df = df.merge(
        fed_aid[['UNITID', 'fed_aid_pct', 'total_fed_aid']],
        on='UNITID',
        how='left'
    )
    
    # Load cost data
    costs = pd.read_parquet('data/processed/costs.parquet')
    df = df.merge(
        costs[['UNITID', 'net_price']],
        on='UNITID',
        how='left'
    )
    
    return df

def calculate_vulnerability_score(df):
    """
    Calculate composite vulnerability score
    Combines multiple risk factors
    """
    # Normalize each component to 0-100 scale
    
    # EP risk (0 = low risk, 100 = critical risk)
    risk_scores = {
        'Low Risk': 0,
        'Moderate Risk': 33,
        'High Risk': 66,
        'Critical Risk': 100,
        'No Data': 50  # Assume moderate uncertainty
    }
    df['ep_risk_score'] = df['risk_level'].map(risk_scores)
    
    # Federal aid dependency (0 = low dependency, 100 = high dependency)
    df['fed_aid_score'] = df['fed_aid_pct'].fillna(50)
    
    # Graduation rate (invert: 0 = high grad rate, 100 = low grad rate)
    df['grad_rate_score'] = 100 - df['graduation_rate'].fillna(50)
    
    # Cost level (normalize to 0-100, higher cost = higher score)
    df['cost_score'] = (
        (df['net_price'] - df['net_price'].min()) / 
        (df['net_price'].max() - df['net_price'].min()) * 100
    ).fillna(50)
    
    # Weighted average
    df['vulnerability_score'] = (
        df['ep_risk_score'] * 0.40 +
        df['fed_aid_score'] * 0.25 +
        df['grad_rate_score'] * 0.20 +
        df['cost_score'] * 0.15
    )
    
    # Vulnerability level
    def categorize_vulnerability(score):
        if pd.isna(score):
            return 'Unknown'
        elif score < 25:
            return 'Low'
        elif score < 50:
            return 'Moderate'
        elif score < 75:
            return 'High'
        else:
            return 'Critical'
    
    df['vulnerability_level'] = df['vulnerability_score'].apply(categorize_vulnerability)
    
    return df

def optimize_dtypes(df):
    """Optimize data types for efficient storage"""
    
    # Integer columns
    int_cols = ['UNITID', 'SECTOR', 'risk_level_numeric']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype('Int32')
    
    # Float columns
    float_cols = ['median_earnings', 'Threshold', 'earnings_margin', 
                  'earnings_margin_pct', 'LATITUDE', 'LONGITUDE',
                  'graduation_rate', 'fed_aid_pct', 'vulnerability_score']
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].astype('float32')
    
    # Category columns (for memory efficiency)
    cat_cols = ['STABBR', 'State', 'risk_level', 'sector_name', 
                'vulnerability_level', 'LOCALE']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # String columns
    string_cols = ['INSTNM']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype('string')
    
    return df

def main():
    """Main processing pipeline"""
    print("Loading datasets...")
    df = merge_datasets()
    
    print("Calculating risk metrics...")
    df = calculate_risk_metrics(df)
    
    print("Adding additional metrics...")
    df = add_additional_metrics(df)
    
    print("Calculating vulnerability scores...")
    df = calculate_vulnerability_score(df)
    
    print("Optimizing data types...")
    df = optimize_dtypes(df)
    
    print("Saving processed data...")
    output_path = Path('data/processed/ep_analysis.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(
        output_path,
        compression='snappy',
        index=False
    )
    
    print(f"Processed {len(df)} institutions")
    print(f"Saved to {output_path}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total institutions: {len(df)}")
    print(f"\nRisk Level Distribution:")
    print(df['risk_level'].value_counts().sort_index())
    print(f"\nMissing earnings data: {df['median_earnings'].isna().sum()}")
    
    return df

if __name__ == '__main__':
    df = main()
```

### Streamlit Component Examples

#### Overview Page (8.1)

```python
# src/sections/earnings_premium/overview.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.core.ep_data_loader import load_ep_data

def render():
    """Render the EP Overview & Risk Map section"""
    
    st.title("Earnings Premium Institutional Analysis")
    st.markdown("""
    Assess institutional readiness for the July 1, 2026 Earnings Premium requirements. 
    This analysis compares institutional median earnings to state thresholds for 6,000+ colleges.
    """)
    
    # Load data
    df = load_ep_data()
    
    # Filter out institutions with no data
    df_valid = df[df['risk_level'] != 'No Data'].copy()
    
    # Summary statistics cards
    render_summary_cards(df_valid)
    
    # Main scatter plot
    render_scatter_plot(df_valid)
    
    # Risk distribution
    render_risk_distribution(df_valid)
    
    # Key findings
    render_key_findings(df_valid)

def render_summary_cards(df):
    """Render summary statistics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Institutions",
            value=f"{len(df):,}"
        )
    
    with col2:
        at_risk = len(df[df['risk_level'].isin(['High Risk', 'Critical Risk'])])
        at_risk_pct = at_risk / len(df) * 100
        st.metric(
            label="At Risk (High + Critical)",
            value=f"{at_risk:,}",
            delta=f"{at_risk_pct:.1f}%"
        )
    
    with col3:
        critical = len(df[df['risk_level'] == 'Critical Risk'])
        critical_pct = critical / len(df) * 100
        st.metric(
            label="Critical Risk (Below Threshold)",
            value=f"{critical:,}",
            delta=f"{critical_pct:.1f}%"
        )
    
    with col4:
        avg_margin = df['earnings_margin_pct'].mean()
        st.metric(
            label="Avg Earnings Margin",
            value=f"+{avg_margin:.0f}%"
        )

def render_scatter_plot(df):
    """Render interactive scatter plot"""
    
    st.subheader("Institution Earnings vs. State Thresholds")
    
    # Filters in sidebar
    with st.sidebar:
        st.header("Filters")
        
        # Risk level filter
        risk_levels = st.multiselect(
            "Risk Level",
            options=['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk'],
            default=['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk']
        )
        
        # Sector filter
        sectors = st.multiselect(
            "Sector",
            options=df['sector_name'].unique().tolist(),
            default=df['sector_name'].unique().tolist()
        )
        
        # State filter
        states = st.multiselect(
            "State",
            options=sorted(df['STABBR'].unique().tolist()),
            default=[]
        )
    
    # Apply filters
    df_filtered = df[df['risk_level'].isin(risk_levels)]
    df_filtered = df_filtered[df_filtered['sector_name'].isin(sectors)]
    if states:
        df_filtered = df_filtered[df_filtered['STABBR'].isin(states)]
    
    # Create scatter plot
    color_map = {
        'Low Risk': 'green',
        'Moderate Risk': 'yellow',
        'High Risk': 'orange',
        'Critical Risk': 'red'
    }
    
    fig = px.scatter(
        df_filtered,
        x='Threshold',
        y='median_earnings',
        color='risk_level',
        color_discrete_map=color_map,
        hover_name='INSTNM',
        hover_data={
            'STABBR': True,
            'median_earnings': ':$,.0f',
            'Threshold': ':$,.0f',
            'earnings_margin_pct': ':.1f%',
            'sector_name': True,
            'risk_level': True
        },
        labels={
            'Threshold': 'State EP Threshold',
            'median_earnings': 'Institution Median Earnings',
            'earnings_margin_pct': 'Earnings Margin'
        }
    )
    
    # Add reference line (y = x)
    max_val = max(df_filtered['Threshold'].max(), df_filtered['median_earnings'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='gray', dash='dash'),
            name='Earnings = Threshold',
            showlegend=True
        )
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="State EP Threshold ($)",
        yaxis_title="Institution Median Earnings ($)",
        legend_title="Risk Level"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Download button
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="ep_analysis_filtered.csv",
        mime="text/csv"
    )

def render_risk_distribution(df):
    """Render risk distribution chart and table"""
    
    st.subheader("Risk Distribution")
    
    # Count by risk level
    risk_counts = df['risk_level'].value_counts().sort_index()
    risk_pcts = (risk_counts / len(df) * 100).round(1)
    
    # Horizontal bar chart
    fig = go.Figure(go.Bar(
        x=risk_pcts,
        y=risk_counts.index,
        orientation='h',
        marker_color=['green', 'yellow', 'orange', 'red'],
        text=[f"{pct}% ({count:,} institutions)" 
              for pct, count in zip(risk_pcts, risk_counts)],
        textposition='auto'
    ))
    
    fig.update_layout(
        xaxis_title="Percentage of Institutions",
        yaxis_title="Risk Level",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    summary = df.groupby('risk_level').agg({
        'UNITID': 'count',
        'median_earnings': 'mean',
        'Threshold': 'mean',
        'earnings_margin_pct': 'mean'
    }).round(0)
    
    summary.columns = ['# Institutions', 'Avg Earnings', 'Avg Threshold', 'Avg Margin']
    summary['% of Total'] = (summary['# Institutions'] / len(df) * 100).round(1)
    
    # Reorder columns
    summary = summary[['# Institutions', '% of Total', 'Avg Earnings', 
                       'Avg Threshold', 'Avg Margin']]
    
    st.dataframe(
        summary.style.format({
            '# Institutions': '{:,.0f}',
            '% of Total': '{:.1f}%',
            'Avg Earnings': '${:,.0f}',
            'Avg Threshold': '${:,.0f}',
            'Avg Margin': '{:+.0f}%'
        }),
        use_container_width=True
    )

def render_key_findings(df):
    """Render automatically generated insights"""
    
    st.subheader("📊 Key Findings")
    
    # Calculate insights
    critical_pct = len(df[df['risk_level'] == 'Critical Risk']) / len(df) * 100
    
    for_profit_risk = df[df['sector_name'].str.contains('For-profit')]
    for_profit_high_risk_pct = (
        len(for_profit_risk[for_profit_risk['risk_level'].isin(['High Risk', 'Critical Risk'])]) / 
        len(for_profit_risk) * 100
    )
    
    # State with most critical institutions
    critical_by_state = df[df['risk_level'] == 'Critical Risk'].groupby('STABBR').size()
    worst_state = critical_by_state.idxmax()
    worst_state_count = critical_by_state.max()
    
    # Display insights
    st.markdown(f"""
    • **{critical_pct:.1f}%** of institutions have median earnings below their state 
      threshold, placing them at critical risk for EP compliance issues.
    
    • For-profit institutions show the highest risk concentration, with 
      **{for_profit_high_risk_pct:.1f}%** in high or critical risk categories.
    
    • **{worst_state}** has the highest number of critical-risk institutions 
      ({worst_state_count}), indicating potential regional challenges.
    
    • Public 2-year institutions face particular challenges, with lower earnings 
      relative to state thresholds due to certificate and associate degree outcomes.
    """)
```

#### Institution Lookup (8.2)

```python
# src/sections/earnings_premium/institution_lookup.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.core.ep_data_loader import load_ep_data

def render():
    """Render the Institution Lookup section"""
    
    st.title("Institution Lookup")
    st.markdown("Search for a specific institution to see its EP risk assessment.")
    
    # Load data
    df = load_ep_data()
    
    # Search interface
    selected_inst = render_search_interface(df)
    
    if selected_inst is not None:
        # Display institution card
        render_institution_card(selected_inst, df)

def render_search_interface(df):
    """Render search box with autocomplete"""
    
    # Create searchable list of institutions
    institution_list = df['INSTNM'].sort_values().tolist()
    
    # Search box
    search_term = st.selectbox(
        "Search for an institution:",
        options=[''] + institution_list,
        format_func=lambda x: "Type to search..." if x == '' else x
    )
    
    if search_term and search_term != '':
        selected = df[df['INSTNM'] == search_term].iloc[0]
        return selected
    
    return None

def render_institution_card(inst, df):
    """Render detailed institution risk card"""
    
    st.markdown("---")
    
    # Header
    st.header(inst['INSTNM'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"📍 {inst['STABBR']}")
    with col2:
        st.write(f"🏫 {inst['sector_name']}")
    with col3:
        if pd.notna(inst['ENROLLMENT']):
            st.write(f"👥 {inst['ENROLLMENT']:,.0f} students")
    
    st.markdown("---")
    
    # Risk assessment section
    st.subheader("EARNINGS PREMIUM RISK ASSESSMENT")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric(
                "Median Earnings (10 yr)",
                f"${inst['median_earnings']:,.0f}" if pd.notna(inst['median_earnings']) else "No data"
            )
        
        with metric_col2:
            st.metric(
                "State Threshold",
                f"${inst['Threshold']:,.0f}"
            )
        
        with metric_col3:
            if pd.notna(inst['earnings_margin_pct']):
                st.metric(
                    "Earnings Margin",
                    f"{inst['earnings_margin_pct']:+.0f}%",
                    delta=f"${inst['median_earnings'] - inst['Threshold']:,.0f}"
                )
            else:
                st.metric("Earnings Margin", "N/A")
    
    with col2:
        # Risk level indicator
        risk_colors = {
            'Low Risk': '🟢',
            'Moderate Risk': '🟡',
            'High Risk': '🟠',
            'Critical Risk': '🔴',
            'No Data': '⚪'
        }
        st.markdown(f"### {risk_colors[inst['risk_level']]} {inst['risk_level']}")
    
    # Visual risk indicator
    if inst['risk_level'] != 'No Data':
        render_risk_scale(inst)
    
    # Peer comparison
    st.markdown("---")
    st.subheader("Peer Comparison")
    render_peer_comparison(inst, df)
    
    # Additional context
    if pd.notna(inst['graduation_rate']):
        st.markdown("---")
        st.subheader("Additional Context")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Graduation Rate", f"{inst['graduation_rate']:.1f}%")
        with col2:
            if pd.notna(inst['fed_aid_pct']):
                st.metric("Federal Aid Dependency", f"{inst['fed_aid_pct']:.1f}%")
        with col3:
            if pd.notna(inst['net_price']):
                st.metric("Net Price", f"${inst['net_price']:,.0f}")
    
    # Important limitation notice
    st.markdown("---")
    st.warning("""
    ⚠️ **IMPORTANT LIMITATION**
    
    This assessment uses institution-level earnings data. Individual programs may vary 
    significantly. Actual EP testing will assess each degree program separately using 
    IRS/SSA data not publicly available.
    """)
    
    # Link to full profile
    st.markdown(f"""
    [View Full Institution Profile in Section 5 →](#)
    """)

def render_risk_scale(inst):
    """Render visual risk scale showing institution position"""
    
    # Create a horizontal scale
    fig = go.Figure()
    
    # Background sections
    sections = [
        {'x': [0, 20], 'color': 'red', 'label': 'Critical'},
        {'x': [20, 40], 'color': 'orange', 'label': 'High'},
        {'x': [40, 60], 'color': 'yellow', 'label': 'Moderate'},
        {'x': [60, 100], 'color': 'green', 'label': 'Low'}
    ]
    
    for section in sections:
        fig.add_trace(go.Scatter(
            x=section['x'],
            y=[1, 1],
            fill='tozeroy',
            fillcolor=section['color'],
            opacity=0.3,
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Position indicator
    # Map margin to 0-100 scale
    if inst['earnings_margin_pct'] < 0:
        position = 10  # Critical zone
    elif inst['earnings_margin_pct'] < 20:
        position = 30  # High risk zone
    elif inst['earnings_margin_pct'] < 50:
        position = 50  # Moderate zone
    else:
        position = min(95, 60 + (inst['earnings_margin_pct'] - 50) / 2)  # Low risk zone
    
    fig.add_trace(go.Scatter(
        x=[position],
        y=[1],
        mode='markers+text',
        marker=dict(size=20, color='black', symbol='triangle-down'),
        text=[inst['INSTNM']],
        textposition='top center',
        showlegend=False
    ))
    
    fig.update_layout(
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False),
        yaxis=dict(range=[0, 2], showticklabels=False, showgrid=False),
        height=150,
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_peer_comparison(inst, df):
    """Render peer institution comparison table"""
    
    # Find peer institutions (same state and sector)
    peers = df[
        (df['STABBR'] == inst['STABBR']) &
        (df['sector_name'] == inst['sector_name']) &
        (df['UNITID'] != inst['UNITID']) &
        (df['risk_level'] != 'No Data')
    ].copy()
    
    if len(peers) == 0:
        st.info("No peer institutions with available data in the same state and sector.")
        return
    
    # Get closest peers by enrollment size
    if pd.notna(inst['ENROLLMENT']):
        peers['enrollment_diff'] = abs(peers['ENROLLMENT'] - inst['ENROLLMENT'])
        peers = peers.nsmallest(5, 'enrollment_diff')
    else:
        peers = peers.head(5)
    
    # Add the selected institution
    inst_df = pd.DataFrame([inst])
    comparison = pd.concat([inst_df, peers])
    
    # Sort by earnings
    comparison = comparison.sort_values('median_earnings', ascending=False)
    
    # Highlight the selected institution
    def highlight_selected(row):
        if row['UNITID'] == inst['UNITID']:
            return ['background-color: #ffffcc'] * len(row)
        return [''] * len(row)
    
    # Display table
    display_df = comparison[[
        'INSTNM',
        'median_earnings',
        'earnings_margin_pct',
        'risk_level'
    ]].copy()
    
    display_df.columns = ['Institution', 'Median Earnings', 'Margin', 'Risk Level']
    
    st.dataframe(
        display_df.style
            .apply(highlight_selected, axis=1)
            .format({
                'Median Earnings': '${:,.0f}',
                'Margin': '{:+.0f}%'
            }),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Showing peer institutions: {inst['sector_name']} in {inst['STABBR']}")
```

### Caching Strategy

Use Streamlit caching to optimize performance:

```python
# src/core/ep_data_loader.py

import streamlit as st
import pandas as pd
from pathlib import Path

DATA_VERSION = "ep_v1"  # Update this when data schema changes

@st.cache_data(ttl=3600, show_spinner="Loading Earnings Premium data...")
def load_ep_data():
    """
    Load processed EP analysis data
    Cached for 1 hour
    """
    data_path = Path('data/processed/ep_analysis.parquet')
    
    if not data_path.exists():
        st.error(f"EP data file not found: {data_path}")
        st.info("Please run: python src/data/build_ep_metrics.py")
        st.stop()
    
    df = pd.read_parquet(data_path)
    return df

@st.cache_data(ttl=3600)
def load_state_thresholds():
    """Load state threshold lookup table"""
    df = pd.read_csv('data/raw/ep_thresholds/state_thresholds_2024.csv')
    return df.set_index('State')['Threshold'].to_dict()

@st.cache_data(ttl=3600)
def get_risk_summary():
    """Get cached risk summary statistics"""
    df = load_ep_data()
    df_valid = df[df['risk_level'] != 'No Data']
    
    summary = {
        'total_institutions': len(df_valid),
        'at_risk_count': len(df_valid[df_valid['risk_level'].isin(['High Risk', 'Critical Risk'])]),
        'critical_count': len(df_valid[df_valid['risk_level'] == 'Critical Risk']),
        'avg_margin': df_valid['earnings_margin_pct'].mean(),
        'risk_distribution': df_valid['risk_level'].value_counts().to_dict()
    }
    
    return summary
```

---

## Testing & Validation

### Data Quality Checks

Before deploying, validate:

1. **Data Completeness**
   - All 50 states + DC have thresholds
   - Threshold values match Federal Register
   - No unexpected missing data

2. **Calculation Accuracy**
   - Manually verify risk calculations for sample institutions
   - Check edge cases (earnings exactly at threshold, etc.)
   - Validate peer comparison logic

3. **Visual Accuracy**
   - Scatter plot reference line is at 45°
   - Risk colors match consistently across all visualizations
   - Hover tooltips show correct values

### Test Cases

```python
# Test script: tests/test_ep_calculations.py

import pytest
import pandas as pd
from src.core.ep_calculations import categorize_risk, calculate_earnings_margin

def test_risk_categorization():
    """Test risk level assignment"""
    assert categorize_risk(0.60) == 'Low Risk'
    assert categorize_risk(0.30) == 'Moderate Risk'
    assert categorize_risk(0.10) == 'High Risk'
    assert categorize_risk(-0.05) == 'Critical Risk'
    assert pd.isna(categorize_risk(None)) or categorize_risk(None) == 'No Data'

def test_earnings_margin_calculation():
    """Test earnings margin calculation"""
    earnings = 50000
    threshold = 30000
    expected_margin = (50000 - 30000) / 30000
    assert abs(calculate_earnings_margin(earnings, threshold) - expected_margin) < 0.001

def test_threshold_coverage():
    """Test that all states have thresholds"""
    from src.core.ep_data_loader import load_state_thresholds
    thresholds = load_state_thresholds()
    
    # Should have 50 states + DC + national = 52 entries
    assert len(thresholds) >= 51
    
    # Check specific states
    assert 'CA' in thresholds or 'California' in thresholds
    assert 'NY' in thresholds or 'New York' in thresholds
```

---

## Deployment Checklist

### Pre-Launch

- [ ] Run `python src/data/build_ep_metrics.py` to generate processed data
- [ ] Verify data file exists: `data/processed/ep_analysis.parquet`
- [ ] Run all test cases
- [ ] Review all text content for accuracy
- [ ] Test all filters and interactive elements
- [ ] Verify download CSV functionality
- [ ] Check mobile responsiveness
- [ ] Proofread all disclaimers and limitation notices

### Post-Launch

- [ ] Monitor for errors in logs
- [ ] Check analytics for user behavior
- [ ] Gather user feedback
- [ ] Plan iterative improvements based on usage patterns

---

## Future Enhancements

### Phase 2 (Post-Launch)

1. **Debt-to-Earnings Calculator**
   - Interactive tool to model D/E ratios
   - Input: earnings, debt → Output: pass/fail
   - Use the allowable debt table from fact sheet

2. **Field-of-Study Analysis**
   - Integrate Census ACS field-level earnings data
   - Show which academic fields face higher/lower risk
   - Help institutions identify program categories to investigate

3. **Vulnerability Score**
   - Composite metric combining EP risk + aid dependency + grad rates + costs
   - Identify institutions with compound vulnerabilities

4. **Program-Level Estimates (Advanced)**
   - Where College Scorecard has program-level data, show it
   - Clear disclaimers about limitations
   - Focus on programs where data is available

5. **Alerts & Notifications**
   - Allow institutions to "watch" their data
   - Email alerts when new data is released
   - Comparative tracking over time

6. **State Policy Context**
   - Add state-level policy information
   - Show which states have additional accountability measures
   - Link to state higher ed agency resources

### Phase 3 (Long-term)

1. **Scenario Modeling**
   - "What if" calculators for institutions
   - Model impact of program closures, cost reductions, etc.

2. **Longitudinal Tracking**
   - Track institutions' EP risk over time
   - Show trends as new data becomes available
   - Identify improving vs. declining institutions

3. **API Access**
   - Provide programmatic access to EP data
   - Enable researchers and policy analysts to use data

---

## Support & Maintenance

### Data Updates

Plan to update annually when new data is released:

1. **College Scorecard** (typically September/October)
   - Update earnings data
   - Re-run processing pipeline

2. **State Thresholds** (annually via Federal Register)
   - Update threshold CSV file
   - Re-calculate all risk metrics

3. **IPEDS** (annually, spring release)
   - Update institutional characteristics
   - Refresh enrollment, sector data

### Version Control

Tag releases in git:
- `ep-v1.0` - Initial launch
- `ep-v1.1` - Bug fixes
- `ep-v2.0` - Major feature additions

### Documentation

Maintain:
- Data dictionary for all EP fields
- Calculation methodology documentation
- User guide / FAQ
- Change log

---

## Questions for Implementation

1. **Data Access:**
   - Do you already have College Scorecard data in your pipeline?
   - Do you have IPEDS data loaded?
   - What format are these currently in?

2. **Existing Code:**
   - Can you share a sample of how you load data for other sections?
   - What's your preferred data processing pattern?
   - Any specific Streamlit components you're already using?

3. **Scope:**
   - Which sub-sections do you want to prioritize for initial launch?
   - Should we start with 8.1 (Overview) and 8.2 (Lookup) first?
   - Do you want all features or phased approach?

4. **Design:**
   - Should Section 8 match the style of existing sections?
   - Any specific color schemes or branding guidelines?
   - Do you have a style guide?

5. **Timeline:**
   - What's your target launch date?
   - How much time do you have for implementation?
   - Do you need help with any specific components?

---

## Contact & Collaboration

For questions during implementation:
- Review this spec document carefully
- Test incrementally (one sub-section at a time)
- Validate data at each step
- Keep user experience simple and clear

Good luck with the implementation! This is a valuable tool that will help thousands of institutions prepare for a major regulatory change.
