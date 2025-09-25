#!/usr/bin/env python3
"""Build Pell dollars versus graduation rate datasets (4-year and 2-year)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PELL_PATH = PROJECT_ROOT / "data" / "raw" / "pelltotals.csv"
INSTITUTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "institutions.csv"
GRAD_4YR_PATH = PROJECT_ROOT / "data" / "processed" / "tuition_vs_graduation.csv"
GRAD_2YR_PATH = PROJECT_ROOT / "data" / "processed" / "tuition_vs_graduation_two_year.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_PATHS = {
    "all": OUTPUT_DIR / "pell_vs_grad_scatter.csv",
    "four_year": OUTPUT_DIR / "pell_vs_grad_scatter_four_year.csv",
    "two_year": OUTPUT_DIR / "pell_vs_grad_scatter_two_year.csv",
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


def _extract_year(field: str) -> Optional[int]:
    if not field:
        return None
    cleaned = field.strip()
    if len(cleaned) < 6:
        return None
    if not cleaned.lower().startswith("yr"):
        return None
    digits = "".join(ch for ch in cleaned[2:] if ch.isdigit())
    if len(digits) != 4:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def _identify_year_columns(fieldnames: Iterable[str]) -> List[Tuple[int, str]]:
    year_columns: List[Tuple[int, str]] = []
    for field in fieldnames:
        year = _extract_year(field)
        if year is not None:
            year_columns.append((year, field))
    return sorted(year_columns)


def _sum_years(row: FieldRow, year_columns: List[Tuple[int, str]]) -> float:
    total = 0.0
    for _, column in year_columns:
        raw_value = (row.get(column) or "").replace(",", "").strip()
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        total += value
    return total


def _load_sector_lookup(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            return {}
        lookup: Dict[str, str] = {}
        for row in reader:
            unit_id = (row.get("UnitID") or "").strip()
            if not unit_id:
                continue
            sector_code = (row.get("SECTOR") or "").strip()
            sector_name = (row.get("Sector") or "").strip()
            if not sector_name and sector_code in SECTOR_NAME_BY_CODE:
                sector_name = SECTOR_NAME_BY_CODE[sector_code]
            if sector_name:
                lookup[unit_id] = sector_name
        return lookup


def _load_grad_lookup(path: Path, sector_lookup: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing processed graduation dataset: {path}")

    lookup: Dict[str, Dict[str, str]] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Graduation dataset is missing headers.")

        for row in reader:
            unit_id = (row.get("UnitID") or row.get("unitid") or "").strip()
            if not unit_id:
                continue
            grad_rate_raw = (row.get("graduation_rate") or row.get("GraduationRate") or "").strip()
            try:
                grad_rate = float(grad_rate_raw)
            except ValueError:
                continue
            institution = (
                row.get("institution")
                or row.get("Institution")
                or row.get("INSTNM")
                or ""
            ).strip()
            sector = (row.get("sector") or row.get("Sector") or "").strip()
            if not sector:
                sector = sector_lookup.get(unit_id, "Unknown")
            if not sector:
                sector = "Unknown"
            lookup[unit_id] = {
                "institution": institution,
                "sector": sector,
                "graduation_rate": grad_rate,
            }
    return lookup


def _write_dataset(path: Path, rows: List[FieldRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "UnitID",
            "Institution",
            "Sector",
            "GraduationRate",
            "PellDollars",
            "PellDollarsBillions",
            "YearsCovered",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_dataset() -> None:
    if not RAW_PELL_PATH.exists():
        raise FileNotFoundError(f"Missing raw Pell totals file: {RAW_PELL_PATH}")

    sector_lookup = _load_sector_lookup(INSTITUTIONS_PATH)
    grad_lookup_4 = _load_grad_lookup(GRAD_4YR_PATH, sector_lookup)
    grad_lookup_2 = _load_grad_lookup(GRAD_2YR_PATH, sector_lookup)

    with RAW_PELL_PATH.open("r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Pell totals CSV is missing headers.")
        year_columns = _identify_year_columns(reader.fieldnames)
        if not year_columns:
            raise ValueError(
                "Unable to locate year columns (expected headers like 'YR2022')."
            )

        min_year = year_columns[0][0]
        max_year = year_columns[-1][0]
        years_covered = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

        rows_all: List[FieldRow] = []
        rows_4: List[FieldRow] = []
        rows_2: List[FieldRow] = []

        for raw_row in reader:
            unit_id = (raw_row.get("UnitID") or "").strip()
            if not unit_id:
                continue

            total_dollars = _sum_years(raw_row, year_columns)
            if total_dollars <= 0:
                continue

            target_lookup: Optional[Dict[str, Dict[str, str]]] = None
            if unit_id in grad_lookup_4:
                target_lookup = grad_lookup_4
                segment_rows = rows_4
            elif unit_id in grad_lookup_2:
                target_lookup = grad_lookup_2
                segment_rows = rows_2
            else:
                continue

            grad_info = target_lookup[unit_id]
            institution = grad_info["institution"] or (raw_row.get("Institution") or "").strip()
            sector = grad_info["sector"] or sector_lookup.get(unit_id, "Unknown") or "Unknown"
            grad_rate = grad_info["graduation_rate"]

            record: FieldRow = {
                "UnitID": unit_id,
                "Institution": institution,
                "Sector": sector,
                "GraduationRate": f"{grad_rate:.2f}",
                "PellDollars": f"{total_dollars:.0f}",
                "PellDollarsBillions": f"{total_dollars / 1_000_000_000:.3f}",
                "YearsCovered": years_covered,
            }

            rows_all.append(record)
            segment_rows.append(record)

    if not rows_all:
        raise ValueError("No Pell/graduation overlap records constructed. Check inputs.")

    for key, rows in ("all", rows_all), ("four_year", rows_4), ("two_year", rows_2):
        rows.sort(key=lambda item: float(item["PellDollars"]), reverse=True)
        _write_dataset(OUTPUT_PATHS[key], rows)


if __name__ == "__main__":
    build_dataset()
