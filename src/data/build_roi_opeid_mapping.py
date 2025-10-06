"""
Build OPEID → UnitID mapping for California institutions.

This script creates a mapping between OPEID6 (used in epanalysis) and
IPEDS UnitID (used in this dashboard) for California institutions
in the ROI dataset.

The OPEID format differs between sources:
- epanalysis: 4-digit OPEID (e.g., "1111" for Allan Hancock College)
- IPEDS: 6-digit OPEID with suffix (e.g., "111100" for Allan Hancock College)

We match by extracting the first 4 digits from IPEDS OPEID and matching
to CA institutions only.
"""

import pandas as pd
from pathlib import Path


def build_opeid_unitid_mapping():
    """
    Create mapping between OPEID (epanalysis) and UnitID (IPEDS).

    Returns:
        DataFrame with OPEID4, UnitID, Institution, County mapping
    """
    print("=" * 70)
    print("Building OPEID → UnitID Mapping for California Institutions")
    print("=" * 70)

    # Load IPEDS institutions data
    print("\n1. Loading IPEDS institutions data...")
    ipeds = pd.read_csv('data/raw/ipeds/2023/institutions.csv')
    print(f"   Loaded {len(ipeds):,} institutions from IPEDS")

    # Filter to CA only
    ipeds_ca = ipeds[ipeds['STATE'] == 'CA'].copy()
    print(f"   California institutions: {len(ipeds_ca)}")

    # Load epanalysis ROI data
    print("\n2. Loading epanalysis ROI data...")
    roi_data = pd.read_csv('data/raw/epanalysis/roi-metrics.csv')
    print(f"   Loaded {len(roi_data)} institutions from epanalysis")

    # Prepare OPEID matching
    print("\n3. Preparing OPEID mapping...")

    # Extract first 4 digits from IPEDS OPEID (e.g., 111100.0 → 1111)
    ipeds_ca['OPEID_str'] = ipeds_ca['OPEID'].astype(str).str.split('.').str[0]
    ipeds_ca['OPEID4'] = ipeds_ca['OPEID_str'].str[:4]

    # epanalysis already uses 4-digit OPEID
    roi_data['OPEID4'] = roi_data['OPEID6'].astype(str)

    print(f"   Sample IPEDS OPEID: {ipeds_ca.iloc[0]['OPEID']} → {ipeds_ca.iloc[0]['OPEID4']}")
    print(f"   Sample ROI OPEID: {roi_data.iloc[0]['OPEID6']}")

    # Create mapping: OPEID4 → UnitID (for CA institutions)
    # Note: Some OPEID4 values may map to multiple institutions
    # We'll keep all matches and resolve duplicates by institution name later
    print("\n4. Creating OPEID4 → UnitID mapping...")

    # Merge ROI with IPEDS on OPEID4
    merged = roi_data.merge(
        ipeds_ca[['OPEID4', 'UnitID', 'INSTITUTION']],
        on='OPEID4',
        how='left'
    )

    # Count matches per OPEID4
    opeid_counts = merged.groupby('OPEID4')['UnitID'].nunique()
    ambiguous = opeid_counts[opeid_counts > 1]

    if len(ambiguous) > 0:
        print(f"\n   ⚠ {len(ambiguous)} OPEID4 values map to multiple UnitIDs")
        print("   Resolving by institution name similarity...")

        # For ambiguous cases, use fuzzy string matching
        from difflib import SequenceMatcher

        def best_unitid_match(group):
            """Find best UnitID match based on institution name."""
            if len(group) == 1:
                return group.iloc[0]

            # Compare ROI institution name with IPEDS institution names
            roi_name = group.iloc[0]['Institution'].lower()
            best_ratio = 0
            best_row = group.iloc[0]

            for _, row in group.iterrows():
                ipeds_name = str(row['INSTITUTION']).lower() if pd.notna(row['INSTITUTION']) else ''
                ratio = SequenceMatcher(None, roi_name, ipeds_name).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_row = row

            return best_row

        # Group by OPEID6 (each ROI institution) and find best match
        merged = merged.groupby('OPEID6', as_index=False).apply(best_unitid_match).reset_index(drop=True)

    print(f"   Mapping created for {len(merged)} institutions")

    # Validation
    print("\n5. Validating mapping...")
    matched = merged['UnitID'].notna().sum()
    unmatched = merged['UnitID'].isna().sum()

    print(f"   ✓ Matched:   {matched} / {len(roi_data)} institutions")
    if unmatched > 0:
        print(f"   ✗ Unmatched: {unmatched} institutions")
        print("\n   Unmatched institutions:")
        unmatched_df = merged[merged['UnitID'].isna()]
        for _, row in unmatched_df.head(10).iterrows():
            print(f"      - {row['Institution']} (OPEID4: {row['OPEID4']})")
        if len(unmatched_df) > 10:
            print(f"      ... and {len(unmatched_df) - 10} more")

    # Save mapping
    print("\n6. Saving mapping...")
    output_path = 'data/raw/epanalysis/opeid_unitid_mapping.csv'

    mapping_df = merged[merged['UnitID'].notna()][
        ['OPEID6', 'UnitID', 'Institution', 'County']
    ].copy()

    mapping_df.to_csv(output_path, index=False)
    print(f"   Saved to: {output_path}")
    print(f"   Rows: {len(mapping_df)}")

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total institutions in epanalysis: {len(roi_data)}")
    print(f"Successfully mapped to UnitID:    {matched}")
    print(f"Match rate:                        {matched/len(roi_data)*100:.1f}%")

    if matched == len(roi_data):
        print("\n✓ SUCCESS: All institutions mapped successfully!")
    elif matched > 0:
        print(f"\n⚠ PARTIAL SUCCESS: {matched} institutions mapped, {unmatched} unmatched")
    else:
        print("\n✗ FAILURE: No institutions could be mapped")

    return mapping_df


if __name__ == '__main__':
    try:
        mapping = build_opeid_unitid_mapping()
        print("\n✓ Mapping complete!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
