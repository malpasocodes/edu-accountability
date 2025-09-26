# Streamlit App UI Specification

These are implementation instructions for Codex. The goal is to organize the Streamlit app sidebar by **chart sections**, each containing multiple chart types, with scoped filters and options.  

---

## Overall Structure

- The app has a **sidebar** and a **main content area**.
- **Sidebar** = navigation + chart selection + filters.  
- **Main content area** = dynamic title, short explainer, chart, caption, optional data preview, and download buttons.  

---

## Sidebar Layout

### Global Controls
- **State**: fixed to California (future-proof for expansion).
- **Data Vintage**: show current data source (e.g., *ACS 2023 5-yr*).

### Section Headers (Collapsible)
Organize charts into two major **sections** (expandable groups):

1. **College Value Grid**
   - Chart types:
     - TBD
     - TBD
     - TBD
   - Filters (scoped to section):
     - 
     -  
     -  
   - Display options:
     -  
     -  
     -  

2. **Pell Grants**
   - Chart types:
     - Pell share by institution (bars)
     - Pell recipients vs Net Price (bubble)
     - Pell dollars by region (map or bar)
     - Pell trend (if multi-year data added later)
   - Filters (scoped to section):
     - Region (multi-select)
     - Sector (Public / Private)
     - Enrollment band (<2k, 2–10k, >10k)
   - Display options:
     - Sort by: Pell share | Pell count | Net price
     - Show labels (toggle)
     - Normalize by enrollment (toggle)

---

## Main Content Area

- **Dynamic Page Title**: shows section + chart (e.g., *College Value Grid » Quadrants*).
- **Short Explainer Line**: one sentence summary of the chart.
- **Chart Canvas**: main visualization.
- **Caption**: 1–2 lines explaining what is being shown.
- **Data Preview (Optional)**: collapsible, shows top N rows of filtered dataset.
- **Download Buttons**:  
  - PNG of the chart.  
  - CSV of filtered dataset.

---

## Default Settings

- Default section: **College Value Grid**
- Default chart: **Quadrants**
- Filters: all regions, both sectors, all credentials
- Display: median lines on, labels off
- Pell Grants section defaults:
  - Chart: Pell share by institution
  - Sorted by Pell share (descending), top 25

---

## Additional Guidelines

- **Tooltips**: add definitions for technical terms (e.g., *H-Premium: Earnings above local HS median*).
- **Empty State**: if filters yield no data → display a friendly message.
- **Color Scheme**: consistent across sections (e.g., Public = blue, Private = orange).
- **Axis Titles**: keep short; push definitions to tooltips.
- **Prose**: keep outside the chart area (above/below).

---

## Data (Examples)

### `roi_with_county_baseline_combined_clean.csv`
Used for **College Value Grid**. Fields include:
- Institution, Region, County, Sector, Predominant Award
- Median Earnings 10 Years After Enrollment
- HS Median Income (Statewide and Regional baselines)
- Premiums (C and H)
- ROI (C and H)
- Ranks

### `pelltotals.csv`
Used for **Pell Grants**. Fields include:
- Institution ID / Name
- Pell recipients (counts)
- Pell dollars
- Enrollment
- Sector, Region
- Derived metrics:
  - Pell share = Pell recipients / enrollment
  - Pell per student = Pell dollars / enrollment

---

## Navigation Logic

1. **Select Section** (College Value Grid | Pell Grants)
2. **Select Chart** (contextual to section)
3. **Apply Filters** (contextual to section)
4. **Adjust Display Options**

---

## Deliverables

Codex should:
1. Implement the sidebar with **collapsible sections** for chart families.
2. Scope filters and display options to their respective section only.
3. Render main content with dynamic title, chart, caption, and optional data preview.
4. Ensure defaults and empty states behave as described.