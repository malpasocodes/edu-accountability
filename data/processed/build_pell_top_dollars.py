#!/usr/bin/env python3
"""Build the processed dataset for top Pell grant dollar recipients."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

TOP_N = 25
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PELL_PATH = PROJECT_ROOT / "data" / "raw" / "pelltotals.csv"
INSTITUTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "institutions.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "pell_top_dollars.csv"

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

def _extract_year(field: str) -> Optional[int]:
    if not field:
        return None
    cleaned = field.strip()
    if len(cleaned) < 6:
        return None
    prefix = cleaned[:2].upper()
    if prefix != "YR":
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


def _sum_years(row: dict[str, str], year_columns: List[Tuple[int, str]]) -> float:
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


def build_dataset() -> None:
    if not RAW_PELL_PATH.exists():
        raise FileNotFoundError(f"Missing raw Pell totals file: {RAW_PELL_PATH}")

    sector_lookup = _load_sector_lookup(INSTITUTIONS_PATH)

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

        rows: List[dict[str, str]] = []
        for raw_row in reader:
            total_dollars = _sum_years(raw_row, year_columns)
            if total_dollars <= 0:
                continue

            unit_id = (raw_row.get("UnitID") or "").strip()
            if not unit_id:
                continue

            institution = (raw_row.get("Institution") or "").strip()
            sector = (raw_row.get("sector") or raw_row.get("Sector") or "").strip()
            if not sector:
                sector_code = (raw_row.get("SECTOR") or raw_row.get("SectorCode") or "").strip()
                if sector_code in SECTOR_NAME_BY_CODE:
                    sector = SECTOR_NAME_BY_CODE[sector_code]
            if not sector:
                sector = sector_lookup.get(unit_id, "Unknown")

            rows.append(
                {
                    "UnitID": unit_id,
                    "Institution": institution,
                    "Sector": sector,
                    "PellDollars": total_dollars,
                    "YearsCovered": years_covered,
                }
            )

    rows.sort(key=lambda item: item["PellDollars"], reverse=True)
    top_rows = rows[:TOP_N]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "rank",
            "UnitID",
            "Institution",
            "Sector",
            "PellDollars",
            "PellDollarsBillions",
            "YearsCovered",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for rank, row in enumerate(top_rows, start=1):
            dollars = row["PellDollars"]
            writer.writerow(
                {
                    "rank": rank,
                    "UnitID": row["UnitID"],
                    "Institution": row["Institution"],
                    "Sector": row["Sector"],
                    "PellDollars": f"{dollars:.0f}",
                    "PellDollarsBillions": f"{dollars / 1_000_000_000:.3f}",
                    "YearsCovered": row["YearsCovered"],
                }
            )


if __name__ == "__main__":
    build_dataset()
