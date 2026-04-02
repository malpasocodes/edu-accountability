"""
Fetch and validate Federal Student Aid (FSA) disbursement data.

The FSA Data Center provides institution-level Pell Grant and Federal
Loan disbursement files with year columns (YR2008, YR2009, ...).

Direct-download URLs on studentaid.gov change frequently, so this
script focuses on validation and provides manual download instructions
when programmatic access fails.

Usage:
    python src/data/fetch_fsa_data.py              # attempt download, then validate
    python src/data/fetch_fsa_data.py --validate    # validate existing files only
    python src/data/fetch_fsa_data.py --force       # re-download even if files exist

Source: https://studentaid.gov/data-center/school/
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FSA_DIR = PROJECT_ROOT / "data" / "raw" / "fsa"

YR_PATTERN = re.compile(r"^YR(\d{4})$", re.IGNORECASE)

# FSA Data Center download URLs — these rotate when FSA redesigns their
# site.  If they 404, follow the manual instructions printed below.
PELL_URL = "https://studentaid.gov/sites/default/files/fsawg/datacenter/library/PellBySchool.csv"
LOAN_URL = "https://studentaid.gov/sites/default/files/fsawg/datacenter/library/LoanBySchool.csv"

FILES = [
    {"url": PELL_URL, "filename": "pelltotals.csv", "label": "Pell Grant disbursements"},
    {"url": LOAN_URL, "filename": "loantotals.csv", "label": "Federal Loan disbursements"},
]

MANUAL_INSTRUCTIONS = """
Manual Download Instructions
=============================
The FSA Data Center direct-download URLs are currently unavailable.
Download the files manually:

1. Go to https://studentaid.gov/data-center/school
2. Under "Grant" data, download the Pell Grant file by school
3. Under "Loan" data, download the Federal Loan file by school
4. Save them as:
     data/raw/fsa/pelltotals.csv
     data/raw/fsa/loantotals.csv
5. Re-run this script with --validate to verify:
     python src/data/fetch_fsa_data.py --validate

Alternative sources:
  - https://data.ed.gov (search "Title IV Program Volume")
  - https://catalog.data.gov/dataset?q=pell+grant+disbursement
"""


def _detect_years(path: Path) -> list[int]:
    """Read the header of a CSV and return sorted list of detected years."""
    with path.open(encoding="utf-8") as fh:
        header = fh.readline()
    return sorted(int(m.group(1)) for col in header.split(",") if (m := YR_PATTERN.match(col.strip())))


def validate_files() -> bool:
    """Validate existing FSA files and report year coverage."""
    print("\nValidation")
    print("-" * 40)

    all_ok = True
    for entry in FILES:
        path = FSA_DIR / entry["filename"]
        print(f"\n{entry['label']} ({entry['filename']}):")

        if not path.exists():
            print(f"  NOT FOUND: {path}")
            all_ok = False
            continue

        size_kb = path.stat().st_size / 1024
        years = _detect_years(path)

        if not years:
            print(f"  WARNING: No YR columns detected in header")
            all_ok = False
            continue

        print(f"  File size: {size_kb:.0f} KB")
        print(f"  Year columns: {years[0]}-{years[-1]} ({len(years)} years)")
        print(f"  Years: {', '.join(str(y) for y in years)}")

    return all_ok


def fetch_file(url: str, dest: Path, *, force: bool = False) -> bool:
    """Attempt to download a file. Returns True on success, False on failure."""
    if dest.exists() and not force:
        print(f"  Exists: {dest.name} (use --force to re-download)")
        return True

    print(f"  Downloading {url} ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        # Sanity-check: response should look like CSV, not HTML error page
        snippet = data[:200].decode("utf-8", errors="replace")
        if "UnitID" not in snippet and "unitid" not in snippet.lower():
            print(f"  Download returned unexpected content (not a CSV)")
            return False

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        size_mb = dest.stat().st_size / 1024 / 1024
        print(f"  Saved {dest.name} ({size_mb:.1f} MB)")
        return True

    except Exception as exc:
        print(f"  Download failed: {exc}")
        return False


def main(*, force: bool = False, validate_only: bool = False) -> None:
    print("=" * 60)
    print("FSA Data — Pell Grants & Federal Loans")
    print("=" * 60)

    if not validate_only:
        FSA_DIR.mkdir(parents=True, exist_ok=True)
        any_failed = False

        for entry in FILES:
            print(f"\n{entry['label']}:")
            ok = fetch_file(entry["url"], FSA_DIR / entry["filename"], force=force)
            if not ok:
                any_failed = True

        if any_failed:
            print(MANUAL_INSTRUCTIONS)

    ok = validate_files()

    print("\n" + "=" * 60)
    if ok:
        print("All FSA files present and valid.")
    else:
        print("Some files missing or invalid. See above.")
        if validate_only:
            print(MANUAL_INSTRUCTIONS)
    print("=" * 60)

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and validate FSA disbursement data.")
    parser.add_argument("--force", action="store_true", help="Re-download even if files exist")
    parser.add_argument("--validate", action="store_true", help="Validate existing files only (no download)")
    args = parser.parse_args()
    main(force=args.force, validate_only=args.validate)
