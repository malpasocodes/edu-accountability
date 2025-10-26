"""
Build Earnings Premium analysis dataset.

Merges College Scorecard earnings data, IPEDS institution characteristics,
and state EP thresholds to create a comprehensive dataset for institutional
EP risk assessment.

Run this script to regenerate the processed EP data from raw sources.

Usage:
    python src/data/build_ep_metrics.py
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


def load_state_thresholds() -> pd.DataFrame:
    """Load state EP thresholds from CSV."""
    print("Loading state EP thresholds...")

    base_dir = Path(__file__).parent.parent.parent
    threshold_path = base_dir / "data" / "raw" / "ep_thresholds" / "state_thresholds_2024.csv"

    df = pd.read_csv(threshold_path)

    # Create state abbreviation from state name for merging
    # Most entries are just state names, but we need to handle special cases
    state_abbr_map = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
        'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
        'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
        'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
        'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
        'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'United States (National)': 'US'
    }

    df['STABBR'] = df['State'].map(state_abbr_map)

    print(f"  ✓ Loaded {len(df)} thresholds")
    print(f"  Range: ${df['Threshold'].min():,} - ${df['Threshold'].max():,}")
    print(f"  Median: ${df['Threshold'].median():,.0f}")

    return df


def load_scorecard_earnings() -> pd.DataFrame:
    """Load institution earnings from College Scorecard."""
    print("\nLoading College Scorecard earnings data...")

    base_dir = Path(__file__).parent.parent.parent
    scorecard_dir = base_dir / "data" / "raw" / "college_scorecard"

    # Try to find the scorecard file (check both real and mock)
    possible_files = [
        scorecard_dir / "scorecard_earnings.csv",  # Real data
        scorecard_dir / "scorecard_earnings_MOCK.csv",  # Mock data for development
        scorecard_dir / "Most-Recent-Cohorts-Institution.csv",  # Alternative name
    ]

    scorecard_path = None
    for path in possible_files:
        if path.exists():
            scorecard_path = path
            break

    if scorecard_path is None:
        raise FileNotFoundError(
            f"College Scorecard data not found. Expected one of:\n" +
            "\n".join(f"  - {p}" for p in possible_files)
        )

    # Check if using mock data
    is_mock = "MOCK" in scorecard_path.name
    if is_mock:
        print(f"  ⚠️  Using MOCK data: {scorecard_path.name}")
        print(f"  ⚠️  Replace with real College Scorecard data before production!")
    else:
        print(f"  ✓ Using real data: {scorecard_path.name}")

    # Load data
    df = pd.read_csv(scorecard_path)

    # Select relevant columns
    required_cols = ['UNITID', 'INSTNM', 'STABBR', 'MD_EARN_WNE_P10', 'MD_EARN_WNE_P6']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df[required_cols].copy()

    # Convert earnings to numeric (handles 'PrivacySuppressed', 'NULL', etc.)
    df['MD_EARN_WNE_P10'] = pd.to_numeric(df['MD_EARN_WNE_P10'], errors='coerce')
    df['MD_EARN_WNE_P6'] = pd.to_numeric(df['MD_EARN_WNE_P6'], errors='coerce')

    # Rename UNITID to match IPEDS convention
    df = df.rename(columns={'UNITID': 'UnitID'})

    print(f"  ✓ Loaded {len(df):,} institutions")
    print(f"  10-year earnings: {df['MD_EARN_WNE_P10'].notna().sum():,} " +
          f"({df['MD_EARN_WNE_P10'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  6-year earnings:  {df['MD_EARN_WNE_P6'].notna().sum():,} " +
          f"({df['MD_EARN_WNE_P6'].notna().sum()/len(df)*100:.1f}%)")

    return df


def load_ipeds_characteristics() -> pd.DataFrame:
    """Load institution characteristics from existing IPEDS data."""
    print("\nLoading IPEDS institution characteristics...")

    base_dir = Path(__file__).parent.parent.parent

    # Try both 4-year and 2-year datasets
    ipeds_4yr = base_dir / "data" / "processed" / "tuition_vs_graduation.parquet"
    ipeds_2yr = base_dir / "data" / "processed" / "tuition_vs_graduation_two_year.parquet"

    # Load both and combine
    dfs = []
    for path in [ipeds_4yr, ipeds_2yr]:
        if path.exists():
            df = pd.read_parquet(path)
            dfs.append(df)
            print(f"  ✓ Loaded {len(df):,} from {path.name}")

    if not dfs:
        raise FileNotFoundError(
            "IPEDS data not found. Expected:\n" +
            f"  - {ipeds_4yr}\n" +
            f"  - {ipeds_2yr}"
        )

    # Combine both datasets
    df = pd.concat(dfs, ignore_index=True)

    # Remove duplicates (in case some institutions appear in both)
    df = df.drop_duplicates(subset=['UnitID'], keep='first')

    # Select relevant columns
    # Available: UnitID, institution, cost, graduation_rate, state, SECTOR, enrollment, sector
    df = df[['UnitID', 'institution', 'state', 'SECTOR', 'sector', 'enrollment',
             'graduation_rate', 'cost']].copy()

    # Rename for consistency with Scorecard data
    df = df.rename(columns={'state': 'STABBR'})

    print(f"  ✓ Combined dataset: {len(df):,} institutions")

    return df


def merge_datasets(
    thresholds: pd.DataFrame,
    earnings: pd.DataFrame,
    characteristics: pd.DataFrame
) -> pd.DataFrame:
    """Merge all datasets on UnitID and state."""
    print("\nMerging datasets...")

    # Start with earnings data (this is our base - we want all institutions with earnings data)
    df = earnings.copy()

    print(f"  Starting with {len(df):,} institutions from Scorecard")

    # Merge with IPEDS characteristics
    df = df.merge(
        characteristics,
        on='UnitID',
        how='left',
        suffixes=('_scorecard', '_ipeds')
    )

    print(f"  After IPEDS merge: {len(df):,} institutions")
    print(f"    Matched: {df['institution'].notna().sum():,}")
    print(f"    Unmatched: {df['institution'].isna().sum():,}")

    # For institutions without IPEDS data, use Scorecard data
    df['institution'] = df['institution'].fillna(df['INSTNM'])
    df['STABBR'] = df['STABBR_ipeds'].fillna(df['STABBR_scorecard'])
    df = df.drop(columns=['STABBR_scorecard', 'STABBR_ipeds', 'INSTNM'])

    # Merge with state thresholds
    df = df.merge(
        thresholds[['STABBR', 'Threshold']],
        on='STABBR',
        how='left'
    )

    print(f"  After threshold merge: {len(df):,} institutions")
    print(f"    With thresholds: {df['Threshold'].notna().sum():,}")
    print(f"    Without thresholds: {df['Threshold'].isna().sum():,}")

    # Use 10-year earnings as primary, fall back to 6-year if missing
    df['median_earnings'] = df['MD_EARN_WNE_P10'].fillna(df['MD_EARN_WNE_P6'])

    print(f"  Combined earnings coverage: {df['median_earnings'].notna().sum():,} " +
          f"({df['median_earnings'].notna().sum()/len(df)*100:.1f}%)")

    return df


def calculate_risk_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate EP risk metrics."""
    print("\nCalculating risk metrics...")

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
            return 'Very Low Risk'
        elif margin > 0.20:
            return 'Low Risk'
        elif margin > 0:
            return 'Moderate Risk'
        else:
            return 'High Risk'

    df['risk_level'] = df['earnings_margin'].apply(categorize_risk)

    # Risk level numeric (for sorting/filtering)
    risk_level_map = {
        'Very Low Risk': 1,
        'Low Risk': 2,
        'Moderate Risk': 3,
        'High Risk': 4,
        'No Data': 5
    }
    df['risk_level_numeric'] = df['risk_level'].map(risk_level_map)

    # Sector name (readable labels from SECTOR code)
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

    # If SECTOR is missing, use the text 'sector' field
    df['sector_name'] = df['sector_name'].fillna(df['sector'])

    # Print distribution
    print("\nRisk level distribution:")
    risk_counts = df['risk_level'].value_counts().sort_index()
    for risk, count in risk_counts.items():
        pct = count / len(df) * 100
        print(f"  {risk:20s}: {count:6,} ({pct:5.1f}%)")

    return df


def add_program_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add program count data to EP analysis

    Merges program counts from IPEDS completions data to show
    the scale of program-level EP assessment requirements.
    """
    print("\nAdding program counts...")

    base_dir = Path(__file__).parent.parent.parent
    program_counts_path = base_dir / 'data' / 'processed' / 'program_counts.parquet'

    if not program_counts_path.exists():
        print("  ⚠️  WARNING: Program counts file not found")
        print("  ⚠️  Run: python src/data/build_program_counts.py")
        print("  ⚠️  Skipping program count integration")
        return df

    program_counts = pd.read_parquet(program_counts_path)

    # Rename UNITID to UnitID to match EP data
    program_counts = program_counts.rename(columns={'UNITID': 'UnitID'})

    print(f"  Merging program counts for {len(program_counts):,} institutions...")

    df = df.merge(
        program_counts[['UnitID', 'total_programs', 'assessable_programs',
                       'total_completions', 'avg_completions_per_program']],
        on='UnitID',
        how='left'
    )

    # Fill missing with 0 (institutions with no completions data)
    df['total_programs'] = df['total_programs'].fillna(0).astype('Int32')
    df['assessable_programs'] = df['assessable_programs'].fillna(0).astype('Int32')
    df['total_completions'] = df['total_completions'].fillna(0).astype('Int32')
    df['avg_completions_per_program'] = df['avg_completions_per_program'].fillna(0).astype('float32')

    institutions_with_programs = len(df[df['total_programs'] > 0])
    print(f"  ✓ {institutions_with_programs:,} institutions have program count data")
    print(f"  Total programs nationwide: {df['total_programs'].sum():,}")
    print(f"  Total assessable programs: {df['assessable_programs'].sum():,}")

    return df


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize data types for efficient storage."""
    print("\nOptimizing data types...")

    # Integer columns (including new program count columns)
    int_cols = ['UnitID', 'SECTOR', 'risk_level_numeric',
                'total_programs', 'assessable_programs', 'total_completions']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].astype('Int32')

    # Float columns (including new avg_completions_per_program)
    float_cols = ['median_earnings', 'Threshold', 'earnings_margin',
                  'earnings_margin_pct', 'MD_EARN_WNE_P10', 'MD_EARN_WNE_P6',
                  'graduation_rate', 'cost', 'enrollment', 'avg_completions_per_program']
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].astype('float32')

    # Category columns (for memory efficiency)
    cat_cols = ['STABBR', 'risk_level', 'sector_name', 'sector']
    for col in cat_cols:
        if col in df.columns and df[col].notna().any():
            df[col] = df[col].astype('category')

    # String columns
    string_cols = ['institution']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype('string')

    print("  ✓ Data types optimized")

    return df


def main():
    """Main processing pipeline."""
    print("=" * 70)
    print("Earnings Premium Analysis - Data Processing Pipeline")
    print("=" * 70)

    try:
        # Load datasets
        thresholds = load_state_thresholds()
        earnings = load_scorecard_earnings()
        characteristics = load_ipeds_characteristics()

        # Merge
        df = merge_datasets(thresholds, earnings, characteristics)

        # Calculate risk metrics
        df = calculate_risk_metrics(df)

        # Add program counts
        df = add_program_counts(df)

        # Optimize dtypes
        df = optimize_dtypes(df)

        # Save processed data
        print("\nSaving processed data...")
        base_dir = Path(__file__).parent.parent.parent
        output_path = base_dir / "data" / "processed" / "ep_analysis.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(
            output_path,
            compression='snappy',
            index=False
        )

        file_size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"  ✓ Saved to: {output_path}")
        print(f"  Size: {file_size_mb:.2f} MB")

        # Summary statistics
        print("\n" + "=" * 70)
        print("Summary Statistics")
        print("=" * 70)
        print(f"Total institutions: {len(df):,}")
        print(f"  With earnings data: {df['median_earnings'].notna().sum():,}")
        print(f"  With IPEDS data: {df['sector_name'].notna().sum():,}")
        print(f"  With state thresholds: {df['Threshold'].notna().sum():,}")

        print(f"\nEarnings statistics:")
        print(f"  Median: ${df['median_earnings'].median():,.0f}")
        print(f"  Mean:   ${df['median_earnings'].mean():,.0f}")
        print(f"  Range:  ${df['median_earnings'].min():,.0f} - ${df['median_earnings'].max():,.0f}")

        print(f"\nState threshold statistics:")
        print(f"  Median: ${df['Threshold'].median():,.0f}")
        print(f"  Range:  ${df['Threshold'].min():,.0f} - ${df['Threshold'].max():,.0f}")

        print("\n" + "=" * 70)
        print("✓ Data processing complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review risk distribution above")
        print("  2. Run unit tests: pytest tests/test_ep_calculations.py")
        print("  3. Proceed with UI implementation")

        return df

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    df = main()
