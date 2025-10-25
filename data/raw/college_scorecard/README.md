# College Scorecard Data

✅ **PRODUCTION DATA IN USE**

## Current Status

This directory contains **REAL College Scorecard data** downloaded from the U.S. Department of Education.

## Current Files

- `Most-Recent-Cohorts-Institution_05192025 2.csv` - Full College Scorecard data (98MB)
- `scorecard_earnings.csv` - Processed file with only needed fields (0.3MB)

## Current Data

The real data (`scorecard_earnings.csv`) includes:
- **6,429 institutions** (May 19, 2025 release)
- **Earnings distribution**: Median $40,092 (10-year)
- **Data coverage**: 86.2% have either 10-year or 6-year earnings data
- **Real institutions**: Harvard, Stanford, MIT, UCLA, UC Berkeley, all U.S. colleges
- **Full geographic coverage**: All 50 states + DC

## Data Source

Downloaded from:
- **Official Website**: https://collegescorecard.ed.gov/data/
- **Data.gov**: https://catalog.data.gov/dataset/college-scorecard-c25e9

## Data Fields

Processed fields for EP Analysis:
- `UNITID` - Institution identifier (links to IPEDS)
- `INSTNM` - Institution name
- `STABBR` - State abbreviation (2-letter)
- `MD_EARN_WNE_P10` - Median earnings 10 years after entry (primary metric)
- `MD_EARN_WNE_P6` - Median earnings 6 years after entry (backup metric)

## Data Processing

To regenerate processed data:
```bash
python src/data/build_ep_metrics.py
```

This will:
1. Load raw College Scorecard data
2. Merge with IPEDS characteristics
3. Merge with state EP thresholds
4. Calculate risk metrics
5. Generate `data/processed/ep_analysis.parquet`

## Validation Checklist

Production data validation completed:
- [x] Real College Scorecard data downloaded (May 19, 2025)
- [x] Mock data files deleted
- [x] Real data has 6,429 institutions
- [x] Earnings values are realistic ($8,535-$143,372 range)
- [x] All real institution names (no placeholders)
- [x] UNITID values match IPEDS database
- [x] All 50 states + DC represented
- [x] Risk calculations validated

## Updates

To update with newer College Scorecard data:
1. Download latest release from https://collegescorecard.ed.gov/data/
2. Replace `Most-Recent-Cohorts-Institution_*.csv`
3. Run: `python src/data/build_ep_metrics.py`
4. Verify output and commit changes

## Questions?

If you encounter issues:
1. Check if the official website has moved
2. Try the Data.gov catalog as backup
3. Contact College Scorecard support: scorecarddata@rti.org
4. Check for API access documentation

---

**Last Updated**: 2025-10-25
**Status**: Production - Real Data
**Data Version**: May 19, 2025 Release
**Institutions**: 6,429
**Earnings Coverage**: 86.2%
