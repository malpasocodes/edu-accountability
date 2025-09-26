#!/usr/bin/env python3
"""Build processed datasets for top Pell grant dollar recipients (4-year and 2-year)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

TOP_N = 25
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PELL_PATH = PROJECT_ROOT / "data" / "raw" / "pelltotals.csv"
INSTITUTIONS_PATH = PROJECT_ROOT / "data" / "raw" / "institutions.csv"
GRAD_4YR_PATH = PROJECT_ROOT / "data" / "processed" / "tuition_vs_graduation.csv"
GRAD_2YR_PATH = PROJECT_ROOT / "data" / "processed" / "tuition_vs_graduation_two_year.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_PATHS = {
    "all": OUTPUT_DIR / "pell_top_dollars.csv",
    "four_year": OUTPUT_DIR / "pell_top_dollars_four_year.csv",
    "two_year": OUTPUT_DIR / "pell_top_dollars_two_year.csv",
}

TREND_OUTPUT_PATHS = {
    "four_year": OUTPUT_DIR / "pell_top_dollars_trend_four_year.csv",
    "two_year": OUTPUT_DIR / "pell_top_dollars_trend_two_year.csv",
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
            }
    return lookup


def _write_dataset(path: Path, rows: List[FieldRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
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
        for rank, row in enumerate(rows, start=1):
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


def _write_trend_dataset(
    path: Path,
    unit_ids: List[str],
    metadata: Dict[str, Dict[str, str]],
    raw_rows: Dict[str, Dict[str, str]],
    year_columns: List[Tuple[int, str]],
    anchor_year: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "UnitID",
            "Institution",
            "Sector",
            "Year",
            "PellDollars",
            "PellDollarsBillions",
            "AnchorYear",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for unit_id in unit_ids:
            raw_row = raw_rows.get(unit_id)
            if raw_row is None:
                continue
            meta = metadata.get(unit_id, {})
            institution = meta.get("Institution", "")
            sector = meta.get("Sector", "Unknown") or "Unknown"

            for year, column in year_columns:
                value_raw = (raw_row.get(column) or "").replace(",", "").strip()
                if not value_raw:
                    continue
                try:
                    dollars = float(value_raw)
                except ValueError:
                    continue
                if dollars <= 0:
                    continue
                writer.writerow(
                    {
                        "UnitID": unit_id,
                        "Institution": institution,
                        "Sector": sector,
                        "Year": year,
                        "PellDollars": f"{dollars:.0f}",
                        "PellDollarsBillions": f"{dollars / 1_000_000_000:.3f}",
                        "AnchorYear": anchor_year,
                    }
                )


def _top_ids_for_year(
    rows: List[FieldRow],
    raw_rows: Dict[str, Dict[str, str]],
    year_column_map: Dict[int, str],
    target_year: int,
    limit: int,
) -> List[str]:
    column = year_column_map.get(target_year)
    if column is None:
        return [row["UnitID"] for row in rows[:limit]]

    scored: List[Tuple[str, float]] = []
    for row in rows:
        unit_id = row["UnitID"]
        value_raw = (raw_rows.get(unit_id, {}).get(column) or "").replace(",", "").strip()
        try:
            value = float(value_raw)
        except ValueError:
            value = 0.0
        scored.append((unit_id, value))

    scored.sort(key=lambda item: item[1], reverse=True)
    selected: List[str] = []
    seen = set()
    for unit_id, value in scored:
        if unit_id in seen:
            continue
        if value <= 0:
            continue
        selected.append(unit_id)
        seen.add(unit_id)
        if len(selected) == limit:
            break

    if not selected:
        for row in rows[:limit]:
            unit_id = row["UnitID"]
            if unit_id not in seen:
                selected.append(unit_id)
                seen.add(unit_id)
                if len(selected) == limit:
                    break

    return selected


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

        year_column_map = {year: column for year, column in year_columns}
        target_year = 2022 if 2022 in year_column_map else year_columns[-1][0]

        min_year = year_columns[0][0]
        max_year = year_columns[-1][0]
        years_covered = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

        rows_all: List[FieldRow] = []
        rows_4: List[FieldRow] = []
        rows_2: List[FieldRow] = []
        metadata: Dict[str, Dict[str, str]] = {}
        raw_year_rows: Dict[str, Dict[str, str]] = {}

        for raw_row in reader:
            unit_id = (raw_row.get("UnitID") or "").strip()
            if not unit_id:
                continue

            total_dollars = _sum_years(raw_row, year_columns)
            if total_dollars <= 0:
                continue

            info = grad_lookup_4.get(unit_id)
            segment_rows: Optional[List[FieldRow]] = None
            if info is not None:
                segment_rows = rows_4
            else:
                info = grad_lookup_2.get(unit_id)
                if info is not None:
                    segment_rows = rows_2

            if info is None:
                # Institution not present in graduation datasets we rely on.
                continue

            institution = info["institution"] or (raw_row.get("Institution") or "").strip()
            sector = info["sector"] or sector_lookup.get(unit_id, "Unknown") or "Unknown"

            record: FieldRow = {
                "UnitID": unit_id,
                "Institution": institution,
                "Sector": sector,
                "PellDollars": total_dollars,
                "YearsCovered": years_covered,
            }

            rows_all.append(record)
            if segment_rows is not None:
                segment_rows.append(record)
            metadata[unit_id] = {
                "Institution": institution,
                "Sector": sector,
            }
            raw_year_rows[unit_id] = {
                column: raw_row.get(column, "") for _, column in year_columns
            }

    if not rows_all:
        raise ValueError("No Pell dollar records constructed. Check raw inputs.")

    rows_all.sort(key=lambda item: item["PellDollars"], reverse=True)
    rows_4.sort(key=lambda item: item["PellDollars"], reverse=True)
    rows_2.sort(key=lambda item: item["PellDollars"], reverse=True)

    top_all = rows_all[:TOP_N]
    top_four = rows_4[:TOP_N]
    top_two = rows_2[:TOP_N]

    _write_dataset(OUTPUT_PATHS["all"], top_all)
    _write_dataset(OUTPUT_PATHS["four_year"], top_four)
    _write_dataset(OUTPUT_PATHS["two_year"], top_two)

    top_four_ids = [row["UnitID"] for row in top_four]
    top_two_ids = [row["UnitID"] for row in top_two]

    trend_four_ids = _top_ids_for_year(rows_4, raw_year_rows, year_column_map, target_year, 10)
    trend_two_ids = _top_ids_for_year(rows_2, raw_year_rows, year_column_map, target_year, 10)

    _write_trend_dataset(
        TREND_OUTPUT_PATHS["four_year"],
        trend_four_ids,
        metadata,
        raw_year_rows,
        year_columns,
        target_year,
    )
    _write_trend_dataset(
        TREND_OUTPUT_PATHS["two_year"],
        trend_two_ids,
        metadata,
        raw_year_rows,
        year_columns,
        target_year,
    )


if __name__ == "__main__":
    build_dataset()
