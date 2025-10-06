"""
Build processed ROI metrics dataset for California institutions.

This script processes the ROI data from epanalysis into Parquet format
for efficient loading in the dashboard.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def build_roi_metrics():
    """
    Process ROI data from epanalysis into Parquet format.

    Input:
    - data/raw/epanalysis/roi-metrics.csv (327 CA institutions from epanalysis)
    - data/raw/epanalysis/opeid_unitid_mapping.csv (109 mapped institutions)

    Output:
    - data/processed/roi_metrics.parquet (109 CA institutions with UnitID)
    """
    print("=" * 70)
    print("Building ROI Metrics Dataset for California Institutions")
    print("=" * 70)

    # Load ROI data
    print("\n1. Loading ROI data from epanalysis...")
    roi_df = pd.read_csv('data/raw/epanalysis/roi-metrics.csv')
    print(f"   Loaded {len(roi_df)} institutions from epanalysis")

    # Load OPEID → UnitID mapping
    print("\n2. Loading OPEID → UnitID mapping...")
    mapping = pd.read_csv('data/raw/epanalysis/opeid_unitid_mapping.csv')
    print(f"   Loaded mapping for {len(mapping)} institutions")

    # Merge ROI data with mapping
    print("\n3. Merging ROI data with UnitID mapping...")
    merged = roi_df.merge(
        mapping[['OPEID6', 'UnitID']],
        left_on='OPEID6',
        right_on='OPEID6',
        how='inner'  # Only keep institutions we can map
    )

    print(f"   Merged dataset: {len(merged)} institutions")

    # Convert data types for Parquet efficiency
    print("\n4. Optimizing data types...")

    # Integer columns
    merged['UnitID'] = merged['UnitID'].astype('int32')
    merged['OPEID6'] = merged['OPEID6'].astype(str)

    # String/Category columns
    merged['Institution'] = merged['Institution'].astype('string')
    merged['County'] = merged['County'].astype('category')
    merged['Sector'] = merged['Sector'].astype('category')

    # Float columns (32-bit for space efficiency)
    float_cols = [
        'median_earnings_10yr', 'total_net_price',
        'premium_statewide', 'premium_regional',
        'roi_statewide_years', 'roi_regional_years',
        'hs_median_income'
    ]
    for col in float_cols:
        merged[col] = merged[col].astype('float32')

    # Integer ranking columns (nullable int16 for cases where ranking might be missing)
    int_cols = ['rank_statewide', 'rank_regional', 'rank_change']
    for col in int_cols:
        merged[col] = merged[col].astype('Int16')  # Nullable integer type

    # Add calculated fields for UI display
    print("\n5. Adding calculated fields...")

    # Convert years to months (easier to display)
    merged['roi_statewide_months'] = (merged['roi_statewide_years'] * 12).round().astype('Int16')
    merged['roi_regional_months'] = (merged['roi_regional_years'] * 12).round().astype('Int16')

    # Add boolean flags for easier filtering
    merged['has_positive_premium_state'] = (merged['premium_statewide'] > 0)
    merged['has_positive_premium_regional'] = (merged['premium_regional'] > 0)

    # Validation
    print("\n6. Validating dataset...")
    validate_roi_dataset(merged)

    # Save as Parquet
    print("\n7. Saving to Parquet...")
    output_path = 'data/processed/roi_metrics.parquet'
    merged.to_parquet(
        output_path,
        engine='pyarrow',
        compression='snappy',
        index=False
    )

    file_size = Path(output_path).stat().st_size / 1024
    print(f"   ✓ Saved to: {output_path}")
    print(f"   ✓ File size: {file_size:.1f} KB")
    print(f"   ✓ Rows: {len(merged)}")
    print(f"   ✓ Columns: {len(merged.columns)}")

    return merged


def validate_roi_dataset(df: pd.DataFrame) -> None:
    """Validate ROI metrics dataset."""
    print("\n   === Validation Checks ===")

    # Check row count
    expected_min = 100  # We mapped 109, so should have at least 100
    assert len(df) >= expected_min, f"Expected at least {expected_min} institutions, got {len(df)}"
    print(f"   ✓ Row count: {len(df)} institutions")

    # Check required columns
    required_cols = [
        'UnitID', 'OPEID6', 'Institution', 'County', 'Sector',
        'median_earnings_10yr', 'total_net_price',
        'premium_statewide', 'premium_regional',
        'roi_statewide_years', 'roi_regional_years',
        'rank_statewide', 'rank_regional', 'rank_change',
        'roi_statewide_months', 'roi_regional_months'
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    print(f"   ✓ All {len(required_cols)} required columns present")

    # Check no nulls in key columns
    key_cols = ['UnitID', 'median_earnings_10yr', 'roi_statewide_years']
    for col in key_cols:
        null_count = df[col].isna().sum()
        assert null_count == 0, f"Found {null_count} nulls in {col}"
    print(f"   ✓ No nulls in key columns")

    # Check ROI reasonableness
    # Note: 999 is used as a flag for negative premium (invalid ROI)
    valid_roi = df[df['roi_statewide_years'] < 999]
    roi_min = valid_roi['roi_statewide_years'].min()
    roi_max = valid_roi['roi_statewide_years'].max()
    roi_999_count = (df['roi_statewide_years'] >= 999).sum()

    assert 0 <= roi_min, f"ROI min ({roi_min}) should be >= 0"
    assert roi_max <= 100, f"ROI max ({roi_max}) out of range (excluding 999 flags)"
    print(f"   ✓ ROI values reasonable: {roi_min:.2f} - {roi_max:.2f} years")
    if roi_999_count > 0:
        print(f"   ⚠ {roi_999_count} institutions with invalid ROI (999 = negative premium)")

    # Check rankings (should be 1-N where N is total institutions in epanalysis)
    rank_min = df['rank_statewide'].min()
    rank_max = df['rank_statewide'].max()
    assert rank_min >= 1, f"Rank min ({rank_min}) should be >= 1"
    print(f"   ✓ Rankings valid: {rank_min} - {rank_max}")

    # Check data types
    assert df['UnitID'].dtype == 'int32', "UnitID should be int32"
    assert df['roi_statewide_years'].dtype == 'float32', "ROI should be float32"
    assert df['Sector'].dtype.name == 'category', "Sector should be category"
    print(f"   ✓ Data types optimized for Parquet")

    # Summary statistics
    print(f"\n   === Summary Statistics ===")
    print(f"   Median earnings: ${df['median_earnings_10yr'].median():,.0f}")
    print(f"   Median net price: ${df['total_net_price'].median():,.0f}")
    print(f"   Median ROI (statewide): {df['roi_statewide_years'].median():.2f} years")
    print(f"   Median ROI (regional): {df['roi_regional_years'].median():.2f} years")

    # Best/worst ROI
    best_idx = df['roi_statewide_years'].idxmin()
    worst_idx = df['roi_statewide_years'].idxmax()

    print(f"\n   Best ROI: {df.loc[best_idx, 'Institution']} ({df.loc[best_idx, 'roi_statewide_years']:.2f} years)")
    print(f"   Worst ROI: {df.loc[worst_idx, 'Institution']} ({df.loc[worst_idx, 'roi_statewide_years']:.2f} years)")

    # Sector breakdown
    print(f"\n   Institutions by sector:")
    for sector, count in df['Sector'].value_counts().items():
        print(f"      {sector}: {count}")


if __name__ == '__main__':
    try:
        roi_df = build_roi_metrics()
        print("\n" + "=" * 70)
        print("✓ SUCCESS: ROI metrics dataset created successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
