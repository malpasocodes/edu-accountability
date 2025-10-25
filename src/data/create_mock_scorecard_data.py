"""
Create mock College Scorecard data for development and testing.

This script generates a realistic sample dataset that mimics the structure
of College Scorecard data. Replace with real data before production deployment.

🚨 FOR DEVELOPMENT ONLY - NOT FOR PRODUCTION USE
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


def create_mock_scorecard_data(n_institutions: int = 6500) -> pd.DataFrame:
    """
    Generate mock College Scorecard data with realistic distributions.

    Args:
        n_institutions: Number of institutions to generate

    Returns:
        DataFrame with UNITID, INSTNM, STABBR, MD_EARN_WNE_P10, MD_EARN_WNE_P6
    """
    np.random.seed(42)  # Reproducible

    # State abbreviations and frequencies (approximate US distribution)
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL',
        'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
        'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
        'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
        'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]

    # Generate state distribution (CA, TX, NY, FL have more institutions)
    state_weights = np.ones(len(states))
    state_weights[states.index('CA')] = 5.0  # California has many institutions
    state_weights[states.index('TX')] = 4.0
    state_weights[states.index('NY')] = 3.5
    state_weights[states.index('FL')] = 3.0
    state_weights = state_weights / state_weights.sum()

    state_abbr = np.random.choice(states, size=n_institutions, p=state_weights)

    # Generate UNITIDs (6-digit numbers starting from 100000)
    unitid = np.arange(100000, 100000 + n_institutions)

    # Generate institution names (generic for now)
    instnm = [f"Institution {i:04d}" for i in range(n_institutions)]

    # Add some recognizable institutions for testing
    known_institutions = {
        100000: ("Harvard University", "MA", 95000, 85000),
        100001: ("Stanford University", "CA", 94000, 84000),
        100002: ("MIT", "MA", 104000, 94000),
        100003: ("UCLA", "CA", 70700, 62000),
        100004: ("UC Berkeley", "CA", 76200, 68000),
        100005: ("University of Phoenix-Online", "AZ", 28400, 26000),
        100006: ("Community College Example", "CA", 31000, 28500),
        100007: ("For-Profit College Example", "FL", 27500, 25000),
    }

    for unitid_val, (name, state, earn10, earn6) in known_institutions.items():
        if unitid_val < 100000 + n_institutions:
            idx = unitid_val - 100000
            instnm[idx] = name
            state_abbr[idx] = state

    # Generate earnings data with realistic distributions
    # Base earnings distribution (median around $40k, range $20k-$120k)
    base_10yr = np.random.lognormal(mean=10.6, sigma=0.45, size=n_institutions)
    base_6yr = base_10yr * np.random.uniform(0.85, 0.95, size=n_institutions)

    # Apply known institution earnings
    for unitid_val, (name, state, earn10, earn6) in known_institutions.items():
        if unitid_val < 100000 + n_institutions:
            idx = unitid_val - 100000
            base_10yr[idx] = earn10
            base_6yr[idx] = earn6

    # Simulate missing data (about 15% for 10-year, 20% for 6-year)
    missing_10yr = np.random.random(n_institutions) < 0.15
    missing_6yr = np.random.random(n_institutions) < 0.20

    md_earn_wne_p10 = base_10yr.copy()
    md_earn_wne_p10[missing_10yr] = np.nan

    md_earn_wne_p6 = base_6yr.copy()
    md_earn_wne_p6[missing_6yr] = np.nan

    # Create DataFrame
    df = pd.DataFrame({
        'UNITID': unitid,
        'INSTNM': instnm,
        'STABBR': state_abbr,
        'MD_EARN_WNE_P10': md_earn_wne_p10,
        'MD_EARN_WNE_P6': md_earn_wne_p6
    })

    return df


def main():
    """Generate and save mock College Scorecard data."""
    print("=" * 70)
    print("Creating Mock College Scorecard Data for Development")
    print("🚨 FOR DEVELOPMENT ONLY - REPLACE WITH REAL DATA")
    print("=" * 70)

    # Generate data
    print("\nGenerating mock data...")
    df = create_mock_scorecard_data(n_institutions=6500)

    # Statistics
    print(f"✓ Generated {len(df):,} mock institutions")
    print(f"  10-year earnings: {df['MD_EARN_WNE_P10'].notna().sum():,} " +
          f"({df['MD_EARN_WNE_P10'].notna().sum()/len(df)*100:.1f}%)")
    print(f"  6-year earnings:  {df['MD_EARN_WNE_P6'].notna().sum():,} " +
          f"({df['MD_EARN_WNE_P6'].notna().sum()/len(df)*100:.1f}%)")

    # Save to CSV
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "data" / "raw" / "college_scorecard"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "scorecard_earnings_MOCK.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✓ Saved to: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    # Show sample data
    print("\nSample institutions:")
    print(df.head(8).to_string(index=False))

    print("\nEarnings statistics:")
    print(f"  10-year median: ${df['MD_EARN_WNE_P10'].median():,.0f}")
    print(f"  10-year mean:   ${df['MD_EARN_WNE_P10'].mean():,.0f}")
    print(f"  10-year range:  ${df['MD_EARN_WNE_P10'].min():,.0f} - ${df['MD_EARN_WNE_P10'].max():,.0f}")

    print("\n" + "=" * 70)
    print("✓ Mock data generation complete!")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Replace with real College Scorecard data before production")
    print("   Real data: https://collegescorecard.ed.gov/data/")


if __name__ == "__main__":
    main()
