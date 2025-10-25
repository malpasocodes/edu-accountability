"""
Download College Scorecard data for Earnings Premium analysis.

This script downloads the most recent institution-level data from the
College Scorecard and extracts only the fields needed for EP analysis.

Source: https://collegescorecard.ed.gov/data/
"""

from __future__ import annotations

import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd


# College Scorecard data URL (most recent institution-level data)
SCORECARD_URL = "https://ed-public-download.app.cloud.gov/downloads/Most-Recent-Cohorts-Institution.zip"

# Fields to extract
FIELDS_TO_EXTRACT = [
    "UNITID",              # Institution ID (links to IPEDS)
    "INSTNM",              # Institution name
    "STABBR",              # State abbreviation
    "MD_EARN_WNE_P10",     # Median earnings 10 years after entry
    "MD_EARN_WNE_P6",      # Median earnings 6 years after entry (backup)
]


def download_scorecard_data(
    output_dir: Path,
    url: str = SCORECARD_URL,
    force: bool = False
) -> Path:
    """
    Download College Scorecard ZIP file.

    Args:
        output_dir: Directory to save downloaded file
        url: URL to download from
        force: If True, re-download even if file exists

    Returns:
        Path to downloaded ZIP file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "scorecard_data.zip"

    if zip_path.exists() and not force:
        print(f"✓ ZIP file already exists: {zip_path}")
        return zip_path

    print(f"Downloading College Scorecard data from:")
    print(f"  {url}")
    print(f"  This may take a few minutes (~200MB)...")

    try:
        urllib.request.urlretrieve(url, zip_path)
        print(f"✓ Downloaded to: {zip_path}")
        print(f"  Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        return zip_path
    except Exception as e:
        print(f"✗ Download failed: {e}")
        raise


def extract_scorecard_csv(zip_path: Path, output_dir: Path) -> Optional[Path]:
    """
    Extract CSV file from ZIP archive.

    Args:
        zip_path: Path to ZIP file
        output_dir: Directory to extract to

    Returns:
        Path to extracted CSV file, or None if not found
    """
    print(f"\nExtracting CSV from ZIP...")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the CSV file (usually Most-Recent-Cohorts-Institution.csv)
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]

            if not csv_files:
                print("✗ No CSV files found in ZIP archive")
                return None

            # Use the first CSV file found
            csv_filename = csv_files[0]
            print(f"  Found: {csv_filename}")

            # Extract to output directory
            zip_ref.extract(csv_filename, output_dir)
            csv_path = output_dir / csv_filename

            print(f"✓ Extracted to: {csv_path}")
            print(f"  Size: {csv_path.stat().st_size / 1024 / 1024:.1f} MB")

            return csv_path

    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        raise


def process_scorecard_data(
    csv_path: Path,
    output_path: Path,
    fields: list[str] = FIELDS_TO_EXTRACT
) -> pd.DataFrame:
    """
    Load full Scorecard CSV and extract only needed fields.

    Args:
        csv_path: Path to full Scorecard CSV
        output_path: Path to save processed CSV
        fields: List of field names to extract

    Returns:
        DataFrame with extracted fields
    """
    print(f"\nProcessing Scorecard data...")
    print(f"  Reading: {csv_path}")
    print(f"  This may take a minute...")

    try:
        # Read only the columns we need to reduce memory usage
        df = pd.read_csv(csv_path, usecols=fields, low_memory=False)

        print(f"✓ Loaded {len(df):,} institutions")
        print(f"  Columns: {list(df.columns)}")

        # Convert earnings columns to numeric (they may contain 'PrivacySuppressed' or 'NULL')
        earnings_cols = ["MD_EARN_WNE_P10", "MD_EARN_WNE_P6"]
        for col in earnings_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Check data availability
        has_10yr = df["MD_EARN_WNE_P10"].notna().sum()
        has_6yr = df["MD_EARN_WNE_P6"].notna().sum()
        has_either = (df["MD_EARN_WNE_P10"].notna() | df["MD_EARN_WNE_P6"].notna()).sum()

        print(f"\nData availability:")
        print(f"  10-year earnings: {has_10yr:,} ({has_10yr/len(df)*100:.1f}%)")
        print(f"  6-year earnings:  {has_6yr:,} ({has_6yr/len(df)*100:.1f}%)")
        print(f"  Either available: {has_either:,} ({has_either/len(df)*100:.1f}%)")

        # Save processed data
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"\n✓ Saved processed data to: {output_path}")
        print(f"  Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")

        return df

    except Exception as e:
        print(f"✗ Processing failed: {e}")
        raise


def create_metadata(output_dir: Path, df: pd.DataFrame) -> None:
    """Create metadata file documenting the Scorecard data."""
    metadata_content = f"""---
name: College Scorecard Earnings Data
description: |
  Institution-level median earnings data from the College Scorecard.
  Used to assess Earnings Premium risk for all U.S. institutions.

source: College Scorecard
source_url: https://collegescorecard.ed.gov/data/
download_url: {SCORECARD_URL}

data_type: Institution-level earnings (federal aid recipients)
update_frequency: Annual (typically September/October)

fields:
  - name: UNITID
    description: IPEDS institution identifier
    type: integer

  - name: INSTNM
    description: Institution name
    type: string

  - name: STABBR
    description: State abbreviation (2-letter)
    type: string

  - name: MD_EARN_WNE_P10
    description: Median earnings 10 years after enrollment entry
    type: float
    unit: USD
    notes: Includes only students who received federal aid

  - name: MD_EARN_WNE_P6
    description: Median earnings 6 years after enrollment entry
    type: float
    unit: USD
    notes: Includes only students who received federal aid (backup metric)

coverage:
  total_institutions: {len(df):,}
  with_10yr_earnings: {df['MD_EARN_WNE_P10'].notna().sum():,}
  with_6yr_earnings: {df['MD_EARN_WNE_P6'].notna().sum():,}
  with_any_earnings: {(df['MD_EARN_WNE_P10'].notna() | df['MD_EARN_WNE_P6'].notna()).sum():,}

data_quality_notes: |
  - Earnings are measured from enrollment ENTRY, not completion
  - Only includes students who received federal financial aid
  - Small cohorts may be privacy-suppressed
  - Some institutions may have missing data

processing:
  - Extracted only fields needed for EP analysis
  - Converted earnings to numeric (NULL/PrivacySuppressed → NaN)
  - Reduced file size from ~200MB to ~{output_dir.joinpath('scorecard_earnings.csv').stat().st_size / 1024 / 1024:.1f}MB

downloaded: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
version: "1.0"
"""

    metadata_path = output_dir / "metadata.yaml"
    with open(metadata_path, 'w') as f:
        f.write(metadata_content)

    print(f"✓ Created metadata: {metadata_path}")


def main():
    """Main download and processing workflow."""
    print("=" * 70)
    print("College Scorecard Data Download for Earnings Premium Analysis")
    print("=" * 70)

    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    raw_dir = base_dir / "data" / "raw" / "college_scorecard"

    # Step 1: Download ZIP file
    zip_path = download_scorecard_data(raw_dir)

    # Step 2: Extract CSV from ZIP
    csv_path = extract_scorecard_csv(zip_path, raw_dir)
    if csv_path is None:
        return

    # Step 3: Process and extract needed fields
    output_path = raw_dir / "scorecard_earnings.csv"
    df = process_scorecard_data(csv_path, output_path, FIELDS_TO_EXTRACT)

    # Step 4: Create metadata
    create_metadata(raw_dir, df)

    # Step 5: Clean up (optional - remove full CSV to save space)
    cleanup = input("\nDelete full Scorecard CSV to save space? (y/n): ").lower()
    if cleanup == 'y':
        csv_path.unlink()
        zip_path.unlink()
        print(f"✓ Deleted: {csv_path}")
        print(f"✓ Deleted: {zip_path}")
        print(f"  Kept: {output_path}")

    print("\n" + "=" * 70)
    print("✓ Download and processing complete!")
    print("=" * 70)
    print(f"\nNext step: Run build_ep_metrics.py to generate EP analysis dataset")


if __name__ == "__main__":
    main()
