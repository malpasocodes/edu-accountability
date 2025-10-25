# College Scorecard Data - Development Notice

⚠️ **IMPORTANT: MOCK DATA IN USE**

## Current Status

This directory currently contains **MOCK DATA** (`scorecard_earnings_MOCK.csv`) generated for development and testing purposes.

**This mock data should be replaced with real College Scorecard data before production deployment.**

## Real Data Source

Download authentic College Scorecard data from:
- **Official Website**: https://collegescorecard.ed.gov/data/
- **Data.gov**: https://catalog.data.gov/dataset/college-scorecard-c25e9

## How to Replace Mock Data

### Option 1: Manual Download
1. Visit https://collegescorecard.ed.gov/data/
2. Download "Most Recent Institution-Level Data"
3. Extract the ZIP file
4. Find the CSV file (usually `Most-Recent-Cohorts-Institution.csv`)
5. Extract only needed columns: UNITID, INSTNM, STABBR, MD_EARN_WNE_P10, MD_EARN_WNE_P6
6. Save as `scorecard_earnings.csv` in this directory
7. Delete `scorecard_earnings_MOCK.csv`

### Option 2: Use Download Script (when URL is fixed)
```bash
python src/data/download_scorecard.py
```

**Note**: The download script currently has a broken URL. Update the URL in the script once College Scorecard updates their data hosting.

## Mock Data Characteristics

The mock data (`scorecard_earnings_MOCK.csv`) includes:
- **6,500 institutions** (realistic count)
- **Earnings distribution**: Median $39,700 (10-year), ranging from ~$7k to ~$196k
- **Missing data**: ~15% missing 10-year earnings, ~20% missing 6-year earnings
- **Known institutions** for testing: Harvard, Stanford, MIT, UCLA, UC Berkeley, etc.
- **State distribution**: Weighted to match US distribution (more CA, TX, NY, FL institutions)

## Data Fields

Required fields for EP Analysis:
- `UNITID` - Institution identifier (links to IPEDS)
- `INSTNM` - Institution name
- `STABBR` - State abbreviation (2-letter)
- `MD_EARN_WNE_P10` - Median earnings 10 years after entry (primary)
- `MD_EARN_WNE_P6` - Median earnings 6 years after entry (backup)

## Validation Checklist

Before production deployment, verify:
- [ ] Real College Scorecard data downloaded
- [ ] Mock data file deleted
- [ ] Real data has ~6,000-7,000 institutions
- [ ] Earnings values are realistic ($20k-$150k range)
- [ ] No "Institution XXXX" placeholder names remain
- [ ] UNITID values match IPEDS database
- [ ] All 50 states + DC represented

## Questions?

If you encounter issues downloading College Scorecard data:
1. Check if the official website has moved
2. Try the Data.gov catalog as backup
3. Contact College Scorecard support: scorecarddata@rti.org
4. Check for API access documentation

---

**Last Updated**: 2025-10-25
**Status**: Development - Mock Data
