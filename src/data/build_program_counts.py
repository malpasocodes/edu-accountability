"""
Process IPEDS completions data to count programs per institution.

This script:
1. Loads IPEDS completions data
2. Counts unique program combinations (CIP code + award level) per institution
3. Identifies "large" programs likely to be assessed (sufficient completers)
4. Generates program_counts.parquet for integration with EP analysis

Usage:
    python src/data/build_program_counts.py
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
import numpy as np


def load_ipeds_completions(year=2024):
    """
    Load IPEDS completions data

    Parameters:
    -----------
    year : int
        Academic year (2024 = 2023-24 academic year)

    Returns:
    --------
    pd.DataFrame with completions data
    """

    file_path = Path(f'data/raw/ipeds/{year}/C{year}_a.csv')

    if not file_path.exists():
        raise FileNotFoundError(
            f"IPEDS completions file not found: {file_path}\n"
            f"Expected location: data/raw/ipeds/2024/C2024_a.csv"
        )

    print(f"Loading IPEDS completions data from {file_path}...")

    # Load data - COMMA DELIMITED (not space-delimited)
    df = pd.read_csv(
        file_path,
        encoding='utf-8-sig',  # Handle BOM (Byte Order Mark)
        low_memory=False,
        index_col=False  # Prevent UNITID from being used as index
    )

    print(f"Loaded {len(df):,} completion records")

    return df


def clean_completions_data(df):
    """
    Clean and filter completions data for program counting

    Steps:
    1. Remove rows with missing CIP codes
    2. Convert CTOTALT to numeric (handling R, Z flags)
    3. Filter to valid award levels
    4. Remove invalid/missing data
    """

    print("Cleaning completions data...")

    # Remove rows with missing CIP codes
    initial_count = len(df)
    df = df[df['CIPCODE'].notna()].copy()
    print(f"  Removed {initial_count - len(df):,} rows with missing CIP codes")

    # Convert CTOTALT to numeric
    # R = revised/imputed, Z = rounds to zero or suppressed
    df['CTOTALT'] = pd.to_numeric(df['CTOTALT'], errors='coerce')
    df['CTOTALT'] = df['CTOTALT'].fillna(0)

    # Ensure numeric types
    df['UNITID'] = df['UNITID'].astype(int)
    df['AWLEVEL'] = pd.to_numeric(df['AWLEVEL'], errors='coerce')
    df['MAJORNUM'] = pd.to_numeric(df['MAJORNUM'], errors='coerce')

    # Remove any remaining invalid rows
    df = df[df['AWLEVEL'].notna()]
    df = df[df['MAJORNUM'].notna()]

    print(f"After cleaning: {len(df):,} records")
    print(f"  Institutions: {df['UNITID'].nunique():,}")
    print(f"  Records with completions > 0: {len(df[df['CTOTALT'] > 0]):,}")

    return df


def filter_to_ep_programs(df):
    """
    Filter to programs subject to Earnings Premium requirements

    Criteria:
    1. 6-digit CIP codes only (exclude 2-digit summaries)
    2. Relevant award levels only (Associate, Bachelor's, Master's, Doctoral)
    3. First majors only (exclude second majors)
    """

    print("Filtering to EP-relevant programs...")

    initial_count = len(df)

    # Convert CIPCODE to string for pattern matching
    df['CIPCODE'] = df['CIPCODE'].astype(str)

    # Filter to 6-digit CIP codes (format: "XX.XXXX")
    # Exclude 2-digit summaries like "01" or "42"
    df = df[df['CIPCODE'].str.match(r'^\d{2}\.\d{4}$', na=False)]
    print(f"  6-digit CIP codes only: {len(df):,} records")

    # Filter to relevant award levels for EP
    # AWLEVEL codes:
    # 3 = Associate degree
    # 5 = Bachelor's degree
    # 7 = Master's degree
    # 17 = Doctor's degree - research/scholarship
    # 18 = Doctor's degree - professional practice
    # 19 = Doctor's degree - other
    relevant_levels = [3, 5, 7, 17, 18, 19]
    df = df[df['AWLEVEL'].isin(relevant_levels)]
    print(f"  Relevant award levels only: {len(df):,} records")

    # Filter to first majors only
    df = df[df['MAJORNUM'] == 1]
    print(f"  First majors only: {len(df):,} records")

    print(f"Filtered out {initial_count - len(df):,} records not subject to EP")

    return df


def calculate_program_counts(df):
    """
    Calculate program counts per institution

    Returns:
    --------
    DataFrame with columns:
    - UNITID: Institution ID
    - total_programs: Count of unique CIP+Level combinations
    - assessable_programs: Count of "large" programs (likely to be assessed)
    - total_completions: Sum of all completions across programs
    - avg_completions_per_program: Average completions per program
    """

    print("Calculating program counts...")

    # Count unique program combinations (CIP code + Award level) per institution
    programs_per_institution = df.groupby('UNITID').apply(
        lambda x: len(x[['CIPCODE', 'AWLEVEL']].drop_duplicates())
    ).reset_index()
    programs_per_institution.columns = ['UNITID', 'total_programs']

    # Calculate total completions per institution
    completions = df.groupby('UNITID')['CTOTALT'].sum().reset_index()
    completions.columns = ['UNITID', 'total_completions']

    # Merge
    result = programs_per_institution.merge(completions, on='UNITID')

    # Count "large" programs likely to be assessed
    # EP requires sufficient completers for reliable median calculation
    # Rule of thumb: 30+ completions over 2-year period = 15+ per year
    large_threshold = 15
    large_programs = df[df['CTOTALT'] >= large_threshold]

    assessable = large_programs.groupby('UNITID').apply(
        lambda x: len(x[['CIPCODE', 'AWLEVEL']].drop_duplicates())
    ).reset_index()
    assessable.columns = ['UNITID', 'assessable_programs']

    result = result.merge(assessable, on='UNITID', how='left')
    result['assessable_programs'] = result['assessable_programs'].fillna(0).astype(int)

    # Calculate average completions per program
    result['avg_completions_per_program'] = (
        result['total_completions'] / result['total_programs']
    ).round(1)

    print(f"\nProgram count statistics:")
    print(f"  Institutions with programs: {len(result):,}")
    print(f"  Total programs nationwide: {result['total_programs'].sum():,}")
    print(f"  Total assessable programs: {result['assessable_programs'].sum():,}")
    print(f"  Avg programs per institution: {result['total_programs'].mean():.1f}")
    print(f"  Median programs per institution: {result['total_programs'].median():.0f}")
    print(f"  Max programs (single institution): {result['total_programs'].max():.0f}")

    return result


def optimize_dtypes(df):
    """Optimize data types for efficient storage"""

    df['UNITID'] = df['UNITID'].astype('Int32')
    df['total_programs'] = df['total_programs'].astype('Int32')
    df['assessable_programs'] = df['assessable_programs'].astype('Int32')
    df['total_completions'] = df['total_completions'].astype('Int32')
    df['avg_completions_per_program'] = df['avg_completions_per_program'].astype('float32')

    return df


def main():
    """Main processing pipeline"""

    print("="*60)
    print("IPEDS COMPLETIONS DATA PROCESSING")
    print("Building program counts for EP Analysis")
    print("="*60)
    print()

    # Load data
    df = load_ipeds_completions(2024)

    # Clean data
    df = clean_completions_data(df)

    # Filter to EP-relevant programs
    df = filter_to_ep_programs(df)

    # Calculate program counts
    program_counts = calculate_program_counts(df)

    # Optimize data types
    program_counts = optimize_dtypes(program_counts)

    # Save
    output_path = Path('data/processed/program_counts.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    program_counts.to_parquet(
        output_path,
        compression='snappy',
        index=False
    )

    print(f"\n✓ Program counts saved to {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Display sample
    print("\nSample institutions (top 10 by program count):")
    print(program_counts.nlargest(10, 'total_programs')[
        ['UNITID', 'total_programs', 'assessable_programs', 'total_completions']
    ].to_string(index=False))

    return program_counts


if __name__ == '__main__':
    program_counts = main()
