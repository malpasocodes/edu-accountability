# Data Dictionary

This document provides human-readable documentation for all datasets used in the College Accountability Dashboard.

## Overview

The dashboard integrates data from multiple authoritative sources to provide comprehensive insights into higher education accountability, affordability, and outcomes. All data sources are public and maintained by federal agencies.

## Data Sources

### IPEDS (Integrated Postsecondary Education Data System)
- **Provider**: National Center for Education Statistics (NCES), U.S. Department of Education
- **Website**: https://nces.ed.gov/ipeds/
- **Description**: Primary source for data on colleges, universities, and technical institutions
- **Update Frequency**: Annual
- **Coverage**: All institutions participating in federal student aid programs

### Federal Student Aid (FSA)
- **Provider**: Federal Student Aid, U.S. Department of Education  
- **Website**: https://studentaid.gov/data-center/
- **Description**: Federal student aid program data including Pell Grants and loans
- **Update Frequency**: Quarterly for recent data, annual for historical
- **Coverage**: Institutions participating in federal student aid programs

## Dataset Descriptions

### Institutions (`institutions.csv`)
Core institutional characteristics and identifying information.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Unique institution identifier assigned by IPEDS | IPEDS HD.UNITID |
| `INSTITUTION` | String | Official institution name | IPEDS HD.INSTNM |
| `CITY` | String | City where institution is located | IPEDS HD.CITY |
| `STATE` | String | Two-letter state postal code | IPEDS HD.STABBR |
| `SECTOR` | Integer | Institutional sector (see codes below) | IPEDS HD.SECTOR |
| `CONTROL` | Integer | Institutional control (see codes below) | IPEDS HD.CONTROL |
| `HISTORICALLY_BLACK` | Integer | HBCU status (1=Yes, 2=No) | IPEDS HD.HBCU |
| `TRIBAL` | Integer | Tribal college status (1=Yes, 2=No) | IPEDS HD.TRIBAL |

**Sector Codes:**
- 1: Public, 4-year or above
- 2: Private not-for-profit, 4-year or above  
- 3: Private for-profit, 4-year or above
- 4: Public, 2-year
- 5: Private not-for-profit, 2-year
- 6: Private for-profit, 2-year
- 7: Public, less-than 2-year
- 8: Private not-for-profit, less-than 2-year
- 9: Private for-profit, less-than 2-year

**Control Codes:**
- 1: Public
- 2: Private not-for-profit
- 3: Private for-profit

### Enrollment (`enrollment.csv`)
Fall enrollment data by institution.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Institution identifier (links to institutions) | IPEDS EF.UNITID |
| `ENR_TOTAL` | Integer | Total fall enrollment | IPEDS EF.EFYTOTLT |
| `ENR_UG` | Integer | Total undergraduate enrollment | IPEDS EF.EFYUGRAD |
| `ENR_GRAD` | Integer | Total graduate enrollment | IPEDS EF.EFYGRAD |

### Cost (`cost.csv`)
Published tuition and fee information.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Institution identifier (links to institutions) | IPEDS IC.UNITID |
| `TUITION_FEES_2023_OUTSTATE` | Float | Out-of-state tuition and fees for 2023-24 | IPEDS IC.TUITION2 |
| `TUITION_FEES_INSTATE2023` | Float | In-state tuition and fees for 2023-24 | IPEDS IC.TUITION1 |

**Notes:**
- Amounts are published prices before financial aid
- For 2-year institutions, in-state and out-of-state may be the same
- Private institutions typically have one published price

### Graduation Rates (`gradrates.csv`)
Graduation rate outcomes for degree-seeking students.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Institution identifier (links to institutions) | IPEDS GR.UNITID |
| `graduation_rate` | Float | Graduation rate (percentage, 0-100) | IPEDS GR.GRTOTLT |

**Notes:**
- Rates calculated at 150% of normal time for degree completion
- 4-year institutions: 6-year graduation rate
- 2-year institutions: 3-year graduation rate
- Includes only first-time, full-time students

### Pell Grant Totals (`pelltotals.csv`)
Annual Pell Grant disbursements by institution.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Institution identifier (links to institutions) | FSA |
| `Institution` | String | Institution name (may differ from IPEDS) | FSA |
| `YR2022` | Float | Total Pell dollars disbursed in 2021-22 academic year | FSA |
| `YR2021` | Float | Total Pell dollars disbursed in 2020-21 academic year | FSA |
| ... | Float | Historical years from 2009-2022 | FSA |

**Notes:**
- Amounts in current dollars (not inflation-adjusted)
- Academic year format (e.g., YR2022 = 2021-22 academic year)
- Zero amounts may indicate no eligible students

### Federal Loan Totals (`loantotals.csv`)
Annual federal loan disbursements by institution.

| Field | Type | Description | Source |
|-------|------|-------------|---------|
| `UnitID` | Integer | Institution identifier (links to institutions) | FSA |
| `Institution` | String | Institution name (may differ from IPEDS) | FSA |
| `YR2022` | Float | Total federal loan dollars disbursed in 2021-22 | FSA |
| `YR2021` | Float | Total federal loan dollars disbursed in 2020-21 | FSA |
| ... | Float | Historical years from 2009-2022 | FSA |

**Notes:**
- Includes Direct Subsidized, Unsubsidized, and PLUS loans
- Amounts in current dollars (not inflation-adjusted)
- Academic year format (e.g., YR2022 = 2021-22 academic year)

## Data Processing

### Transformations Applied
The dashboard applies several standardized transformations to create analytical datasets:

1. **Numeric Conversion**: Cost and enrollment fields converted to numeric types
2. **Sector Mapping**: IPEDS sector codes mapped to readable categories
3. **Missing Value Handling**: Empty values preserved as null for analysis
4. **Enrollment Filtering**: Minimum enrollment thresholds applied for some analyses

### Processed Datasets
Several analytical datasets are created from the raw data:

- `tuition_vs_graduation.csv`: Combined cost and graduation data for 4-year institutions
- `tuition_vs_graduation_two_year.csv`: Combined data for 2-year institutions  
- `pell_top_dollars_*.csv`: Top Pell recipient analyses
- `pell_vs_grad_scatter_*.csv`: Pell funding vs. graduation correlations

## Data Quality Notes

### Known Limitations
- **Missing Data**: Not all institutions report all variables
- **Timing**: IPEDS and FSA data may reflect different academic years
- **Institution Changes**: Mergers, closures, and name changes affect continuity
- **Private Institutions**: For-profit institutions have higher missing data rates

### Validation Rules
- UnitID must be 6-digit integer
- Graduation rates must be 0-100 percentage
- Financial amounts must be non-negative
- State codes must be valid 2-letter abbreviations

## Usage Guidelines

### Best Practices
1. **Check Data Availability**: Verify data exists before analysis
2. **Account for Missing Values**: Use appropriate handling for null values
3. **Consider Context**: Compare institutions of similar type and size
4. **Inflation Adjustment**: Adjust financial data for multi-year comparisons

### Common Analyses
- **Value Analysis**: Cost vs. graduation rate by sector
- **Aid Distribution**: Pell and loan concentrations by institution type
- **Trends**: Multi-year patterns in aid and outcomes
- **Correlations**: Relationships between aid levels and graduation rates

## Data Updates

### Update Schedule
- **IPEDS**: Annual updates (typically 12-18 months after collection)
- **FSA**: Quarterly updates for recent years, annual for historical
- **Dashboard**: Updates applied after data validation

### Version Control
- Raw data preserved in source directories with metadata
- Schema changes tracked in `data/dictionary/schema.json`
- Processing changes documented in transformation rules

## Contact and Support

### Data Issues
Report data quality issues or questions by creating an issue in the repository.

### Source Data Support
- **IPEDS**: ipedshelp@rti.org or 1-877-225-2568
- **FSA**: Contact through https://studentaid.gov/feedback

### Documentation Updates
This documentation is maintained alongside the codebase. Suggest improvements through pull requests.