#!/usr/bin/env python3
"""Build Pell graduation rate scatter datasets (4-year and 2-year)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PELL_GRAD_PATH = PROJECT_ROOT / "data" / "raw" / "ipeds" / "2023" / "pellgradrates.csv"
PELL_DOLLARS_PATH = PROJECT_ROOT / "data" / "raw" / "fsa" / "pelltotals.csv"
ENROLLMENT_PATH = PROJECT_ROOT / "data" / "raw" / "ipeds" / "2023" / "enrollment.csv"
INSTITUTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "ipeds" / "2023" / "institutions.csv"
OUTPUT_DIR = Path(__file__).resolve().parent

OUTPUT_PATHS = {
    "four_year": OUTPUT_DIR / "pell_grad_rate_scatter_four_year.csv",
    "two_year": OUTPUT_DIR / "pell_grad_rate_scatter_two_year.csv",
}

SECTOR_NAME_BY_CODE: Dict[str, str] = {
    "1": "Public",
    "2": "Private, not-for-profit",
    "3": "Private, for-profit",
    "4": "Public",
    "5": "Private, not-for-profit",
    "6": "Private, for-profit",
    "7": "Public",
    "8": "Private, not-for-profit",
    "9": "Private, for-profit",
}

FieldRow = Dict[str, str]


def _calculate_average_pell_grad_rate(row: FieldRow) -> Optional[float]:
    """Calculate average Pell graduation rate across years 2017-2023."""
    rates = []
    for year in range(2017, 2024):
        field_name = f"PGR{year}"
        value = row.get(field_name, "").strip()
        if value:
            try:
                rates.append(float(value))
            except ValueError:
                pass

    if not rates:
        return None
    return sum(rates) / len(rates)


def _calculate_total_pell_dollars(row: FieldRow) -> float:
    """Calculate total Pell dollars across all available years."""
    total = 0.0
    for field_name, value in row.items():
        if field_name.startswith("YR"):
            cleaned = value.replace(",", "").strip()
            if cleaned:
                try:
                    total += float(cleaned)
                except ValueError:
                    pass
    return total


def _load_pell_grad_rates() -> Dict[str, float]:
    """Load and calculate average Pell graduation rates by UnitID."""
    if not PELL_GRAD_PATH.exists():
        raise FileNotFoundError(f"Missing Pell graduation rates file: {PELL_GRAD_PATH}")

    rates_by_unit: Dict[str, float] = {}
    with PELL_GRAD_PATH.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue

            avg_rate = _calculate_average_pell_grad_rate(row)
            if avg_rate is not None:
                rates_by_unit[unit_id] = avg_rate

    return rates_by_unit


def _load_pell_dollars() -> Dict[str, float]:
    """Load total Pell dollars by UnitID."""
    if not PELL_DOLLARS_PATH.exists():
        raise FileNotFoundError(f"Missing Pell dollars file: {PELL_DOLLARS_PATH}")

    dollars_by_unit: Dict[str, float] = {}
    with PELL_DOLLARS_PATH.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue

            total = _calculate_total_pell_dollars(row)
            if total > 0:
                dollars_by_unit[unit_id] = total

    return dollars_by_unit


def _load_enrollment() -> Dict[str, int]:
    """Load enrollment by UnitID."""
    if not ENROLLMENT_PATH.exists():
        raise FileNotFoundError(f"Missing enrollment file: {ENROLLMENT_PATH}")

    enrollment_by_unit: Dict[str, int] = {}
    with ENROLLMENT_PATH.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue

            # Try undergraduate enrollment first, then total enrollment
            enr_value = row.get("ENR_UG", "").strip() or row.get("ENR_TOTAL", "").strip()
            if enr_value:
                try:
                    enrollment_by_unit[unit_id] = int(float(enr_value))
                except ValueError:
                    pass

    return enrollment_by_unit


def _load_institutions() -> Dict[str, Dict[str, str]]:
    """Load institution metadata by UnitID."""
    if not INSTITUTIONS_PATH.exists():
        raise FileNotFoundError(f"Missing institutions file: {INSTITUTIONS_PATH}")

    institutions_by_unit: Dict[str, Dict[str, str]] = {}
    with INSTITUTIONS_PATH.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue

            sector_code = row.get("SECTOR", "").strip()
            sector_name = SECTOR_NAME_BY_CODE.get(sector_code, "Unknown")

            institutions_by_unit[unit_id] = {
                "name": row.get("INSTITUTION", "").strip(),
                "sector": sector_name,
                "category": row.get("CATEGORY", "").strip(),
                "state": row.get("STATE", "").strip(),
            }

    return institutions_by_unit


def _write_dataset(path: Path, rows: List[FieldRow]) -> None:
    """Write dataset to CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "UnitID",
            "Institution",
            "State",
            "Sector",
            "PellGraduationRate",
            "PellDollars",
            "PellDollarsBillions",
            "Enrollment",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_datasets() -> None:
    """Build Pell graduation rate scatter datasets."""
    # Load all data
    pell_grad_rates = _load_pell_grad_rates()
    pell_dollars = _load_pell_dollars()
    enrollment = _load_enrollment()
    institutions = _load_institutions()

    # Combine data
    rows_4year: List[FieldRow] = []
    rows_2year: List[FieldRow] = []

    # Find institutions with both Pell grad rates and dollar data
    for unit_id in pell_grad_rates:
        if unit_id not in pell_dollars:
            continue
        if unit_id not in institutions:
            continue

        inst_data = institutions[unit_id]
        category = inst_data.get("category", "")

        # Determine if 4-year or 2-year based on CATEGORY
        # CATEGORY 2 = 4-year degree granting
        # CATEGORY 3,4 = 2-year degree granting
        if category == "2":
            target_list = rows_4year
        elif category in ["3", "4"]:
            target_list = rows_2year
        else:
            continue  # Skip institutions with other categories

        # Get enrollment (default to 0 if not found)
        enr = enrollment.get(unit_id, 0)

        record: FieldRow = {
            "UnitID": unit_id,
            "Institution": inst_data["name"],
            "State": inst_data["state"],
            "Sector": inst_data["sector"],
            "PellGraduationRate": f"{pell_grad_rates[unit_id]:.2f}",
            "PellDollars": f"{pell_dollars[unit_id]:.0f}",
            "PellDollarsBillions": f"{pell_dollars[unit_id] / 1_000_000_000:.3f}",
            "Enrollment": str(enr),
        }

        target_list.append(record)

    # Sort by Pell dollars descending
    rows_4year.sort(key=lambda x: float(x["PellDollars"]), reverse=True)
    rows_2year.sort(key=lambda x: float(x["PellDollars"]), reverse=True)

    # Write datasets
    _write_dataset(OUTPUT_PATHS["four_year"], rows_4year)
    _write_dataset(OUTPUT_PATHS["two_year"], rows_2year)

    print(f"Created {OUTPUT_PATHS['four_year']} with {len(rows_4year)} institutions")
    print(f"Created {OUTPUT_PATHS['two_year']} with {len(rows_2year)} institutions")


if __name__ == "__main__":
    build_datasets()