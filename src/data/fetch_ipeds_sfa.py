"""
Fetch IPEDS Student Financial Aid (SFA) percentage datasets.

Downloads the "Percent receiving Pell Grants" and "Percent receiving
federal student loans" derived variables from the IPEDS Data Center.
These are the wide-format CSV tables consumed by the canonical SFA
pipeline (src/pipelines/canonical/ipeds_sfa/).

The IPEDS Data Center does not offer a stable direct-download URL for
custom variable exports.  This script therefore documents the manual
steps and validates that the expected files are present after the user
places them in the correct directory.

For fully automated access, consider the Urban Institute Education Data
API: https://educationdata.urban.org/documentation/
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IPEDS_DIR = PROJECT_ROOT / "data" / "raw" / "ipeds"

EXPECTED_FILES = {
    "percent_pell_grants.csv": {
        "description": "Percent of undergraduates receiving Pell Grants (SFA wide format)",
        "column_pattern": re.compile(r"\(SFA\d{4}(?:_RV)?\)"),
    },
    "percent_federal_loans.csv": {
        "description": "Percent of undergraduates receiving federal student loans (SFA wide format)",
        "column_pattern": re.compile(r"\(SFA\d{4}(?:_RV)?\)"),
    },
}

INSTRUCTIONS = """
IPEDS SFA Download Instructions
================================

1. Go to https://nces.ed.gov/ipeds/datacenter/DataFiles.aspx
2. Select survey component: "Student Financial Aid and Net Price"
3. Choose the most recent available year
4. Under "Select Variables", add:
   - "Percent of full-time first-time undergraduates awarded Pell grants"
   - "Percent of full-time first-time undergraduates awarded federal student loans"
5. Select all available years
6. Download each as CSV

7. Save the files as:
   - data/raw/ipeds/percent_pell_grants.csv
   - data/raw/ipeds/percent_federal_loans.csv

8. Re-run this script to validate.
"""


def validate_file(path: Path, spec: dict) -> list[str]:
    """Return a list of issues found with *path*, empty if valid."""
    issues: list[str] = []
    if not path.exists():
        issues.append(f"File not found: {path}")
        return issues

    # Check that at least one SFA column exists
    with path.open(encoding="utf-8") as fh:
        header = fh.readline()

    if not spec["column_pattern"].search(header):
        issues.append(f"No SFA year columns detected in {path.name}")

    if "UnitID" not in header and "unitid" not in header.lower():
        issues.append(f"Missing UnitID column in {path.name}")

    return issues


def main() -> None:
    print("=" * 60)
    print("IPEDS SFA Data Validation")
    print("=" * 60)

    all_ok = True
    for filename, spec in EXPECTED_FILES.items():
        path = IPEDS_DIR / filename
        print(f"\n{spec['description']}:")
        print(f"  Expected at: {path}")

        issues = validate_file(path, spec)
        if issues:
            all_ok = False
            for issue in issues:
                print(f"  WARNING: {issue}")
        else:
            size_kb = path.stat().st_size / 1024
            print(f"  OK ({size_kb:.0f} KB)")

    if not all_ok:
        print(INSTRUCTIONS)
        sys.exit(1)
    else:
        print("\nAll IPEDS SFA files present and valid.")
        print("Run the canonical pipeline to process:")
        print("  python -m src.pipelines.canonical.ipeds_sfa.extraction --dataset pell")
        print("  python -m src.pipelines.canonical.ipeds_sfa.extraction --dataset loans")
        print("  python -m src.pipelines.canonical.ipeds_sfa.enrich_metadata --dataset pell")
        print("  python -m src.pipelines.canonical.ipeds_sfa.enrich_metadata --dataset loans")
        print("  python -m src.pipelines.canonical.ipeds_sfa.build_outputs --dataset pell")
        print("  python -m src.pipelines.canonical.ipeds_sfa.build_outputs --dataset loans")


if __name__ == "__main__":
    main()
