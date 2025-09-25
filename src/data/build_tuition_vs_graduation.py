"""Build the processed tuition vs. graduation dataset used in the dashboard."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "tuition_vs_graduation.csv"

FOUR_YEAR_SECTORS = {"1", "2", "3"}
SECTOR_LABELS = {
    "1": "Public",
    "2": "Private, not-for-profit",
    "3": "Private, for-profit",
}


def _parse_float(value: str) -> Optional[float]:
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_int(value: str) -> Optional[int]:
    cleaned = (value or "").strip().replace(",", "")
    if not cleaned:
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


@dataclass
class Institution:
    unit_id: str
    name: str
    state: str
    sector_code: str
    level: Optional[int]
    category: Optional[int]

    @property
    def sector_label(self) -> str:
        return SECTOR_LABELS.get(self.sector_code, "Unknown")


def _load_institutions() -> Dict[str, Institution]:
    path = RAW_DIR / "institutions.csv"
    institutions: Dict[str, Institution] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sector = row.get("SECTOR", "").strip()
            if sector not in FOUR_YEAR_SECTORS:
                continue

            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue

            institutions[unit_id] = Institution(
                unit_id=unit_id,
                name=row.get("INSTITUTION", "").strip(),
                state=row.get("STATE", "").strip(),
                sector_code=sector,
                level=_parse_int(row.get("LEVEL", "")),
                category=_parse_int(row.get("CATEGORY", "")),
            )
    return institutions


def _load_numeric_column(filename: str, value_field: str, parser) -> Dict[str, float]:
    path = RAW_DIR / filename
    values: Dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue
            value = parser(row.get(value_field, ""))
            if value is None:
                continue
            values[unit_id] = value
    return values


def _build_rows() -> List[List[object]]:
    institutions = _load_institutions()
    if not institutions:
        return []

    tuition = _load_numeric_column("cost.csv", "TUITION_FEES_INSTATE2023", _parse_float)
    grad_rates = _load_numeric_column("gradrates.csv", "PCT_AWARD_6YRS", _parse_float)
    enrollment = _load_numeric_column("enrollment.csv", "ENR_UGD", _parse_int)

    rows: List[List[object]] = []
    for unit_id, inst in institutions.items():
        cost = tuition.get(unit_id)
        grad = grad_rates.get(unit_id)
        if cost is None or grad is None:
            continue

        enr = enrollment.get(unit_id, 0)

        rows.append(
            [
                int(unit_id),
                inst.name,
                cost,
                grad,
                inst.state,
                float(inst.sector_code),
                inst.level if inst.level is not None else "",
                inst.category if inst.category is not None else "",
                enr,
                inst.sector_label,
            ]
        )

    rows.sort(key=lambda item: (item[1].lower(), item[0]))
    return rows


def write_dataset(rows: Iterable[List[object]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "UnitID",
                "institution",
                "cost",
                "graduation_rate",
                "state",
                "SECTOR",
                "LEVEL",
                "CATEGORY",
                "enrollment",
                "sector",
            ]
        )
        for row in rows:
            writer.writerow(row)


def main() -> None:
    rows = _build_rows()
    if not rows:
        raise SystemExit("No qualifying institutions found.")
    write_dataset(rows)


if __name__ == "__main__":
    main()
