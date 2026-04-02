"""
Fetch Federal Student Aid (FSA) disbursement data.

Downloads Pell Grant and Federal Loan disbursement CSV files from the
FSA Data Center. These files provide institution-level annual totals
with year columns like YR2008, YR2009, ..., YR2023.

Source: https://studentaid.gov/data-center/school/
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FSA_DIR = PROJECT_ROOT / "data" / "raw" / "fsa"

# FSA Data Center download URLs
# These point to the "by school" disbursement files.  When FSA publishes
# updated award-year data the same URLs typically serve the refreshed
# CSVs, but verify the landing page if downloads fail.
PELL_URL = "https://studentaid.gov/sites/default/files/fsawg/datacenter/library/PellBySchool.csv"
LOAN_URL = "https://studentaid.gov/sites/default/files/fsawg/datacenter/library/LoanBySchool.csv"

FILES = [
    {"url": PELL_URL, "filename": "pelltotals.csv", "label": "Pell Grant disbursements"},
    {"url": LOAN_URL, "filename": "loantotals.csv", "label": "Federal Loan disbursements"},
]


def fetch_file(url: str, dest: Path, *, force: bool = False) -> Path:
    """Download a single file from *url* to *dest*.

    Skips the download when *dest* already exists unless *force* is True.
    """
    if dest.exists() and not force:
        print(f"  Skipped (exists): {dest}")
        return dest

    print(f"  Downloading {url} ...")
    try:
        urllib.request.urlretrieve(url, dest)
        size_mb = dest.stat().st_size / 1024 / 1024
        print(f"  Saved {dest.name} ({size_mb:.1f} MB)")
    except Exception as exc:
        print(f"  Download failed: {exc}")
        raise
    return dest


def main(*, force: bool = False) -> None:
    """Download all FSA disbursement files."""
    print("=" * 60)
    print("FSA Data Fetch — Pell Grants & Federal Loans")
    print("=" * 60)

    FSA_DIR.mkdir(parents=True, exist_ok=True)

    for entry in FILES:
        print(f"\n{entry['label']}:")
        fetch_file(entry["url"], FSA_DIR / entry["filename"], force=force)

    print("\n" + "=" * 60)
    print("Done.  Files saved to:", FSA_DIR)
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch FSA disbursement data.")
    parser.add_argument("--force", action="store_true", help="Re-download even if files exist")
    args = parser.parse_args()
    main(force=args.force)
