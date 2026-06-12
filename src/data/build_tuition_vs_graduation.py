"""Build processed tuition vs. graduation datasets used in the dashboard."""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
# Year-stamped IPEDS snapshot used by the rest of the dashboard.
IPEDS_DIR = RAW_DIR / "ipeds" / "2023"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Graduation Rate Survey (GRS) series: GR{year} columns, latest first.
GR_YEAR_COLUMNS = [f"GR{year}" for year in range(2023, 2015, -1)]

SEGMENTS = {
    "tuition_vs_graduation": {
        "sectors": {"1", "2", "3"},
        "output": PROCESSED_DIR / "tuition_vs_graduation.csv",
    },
    "tuition_vs_graduation_two_year": {
        "sectors": {"4", "5", "6"},
        "output": PROCESSED_DIR / "tuition_vs_graduation_two_year.csv",
    },
}

SECTOR_LABELS = {
    "1": "Public",
    "2": "Private, not-for-profit",
    "3": "Private, for-profit",
    "4": "Public",
    "5": "Private, not-for-profit",
    "6": "Private, for-profit",
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


def _load_institutions(sector_filter: Sequence[str]) -> Dict[str, Institution]:
    path = IPEDS_DIR / "institutions.csv"
    institutions: Dict[str, Institution] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sector = row.get("SECTOR", "").strip()
            if sector not in sector_filter:
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


def _load_numeric_column(
    filename: str, value_field: str, parser: Callable[[str], Optional[float]]
) -> Dict[str, float]:
    path = IPEDS_DIR / filename
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


def _load_latest_grad_rates() -> Dict[str, float]:
    """Latest available IPEDS Graduation Rate Survey (GRS) six-year rate per UnitID.

    GRS measures first-time, full-time, degree-seeking students completing within
    150% of normal time -- the standard completion metric reported by College
    Explorer and the canonical grad-rate pipeline. We take each institution's most
    recent non-null ``GR{year}`` value so the whole dashboard reports one outcome.
    (Replaces the broader Outcome Measures ``PCT_AWARD_6YRS`` cut previously used
    here, which runs higher because it also counts part-time/returning students.)
    """
    path = IPEDS_DIR / "pellgradrates.csv"
    values: Dict[str, float] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            unit_id = row.get("UnitID", "").strip()
            if not unit_id:
                continue
            for column in GR_YEAR_COLUMNS:
                rate = _parse_float(row.get(column, ""))
                if rate is not None:
                    values[unit_id] = rate
                    break
    return values


def _build_rows(sector_filter: Sequence[str]) -> List[List[object]]:
    institutions = _load_institutions(sector_filter)
    if not institutions:
        return []

    tuition = _load_numeric_column("cost.csv", "TUITION_FEES_INSTATE2023", _parse_float)
    grad_rates = _load_latest_grad_rates()
    enrollment = _load_numeric_column("enrollment.csv", "ENR_UGD", _parse_int)

    rows: List[List[object]] = []
    missing_cost = 0
    missing_grad = 0
    missing_both = 0
    for unit_id, inst in institutions.items():
        cost = tuition.get(unit_id)
        grad = grad_rates.get(unit_id)
        if cost is None or grad is None:
            if cost is None and grad is None:
                missing_both += 1
            elif cost is None:
                missing_cost += 1
            else:
                missing_grad += 1
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

    dropped = missing_cost + missing_grad + missing_both
    if dropped:
        logger.info(
            "Dropped %d of %d institutions (missing cost=%d, missing grad=%d, missing both=%d)",
            dropped,
            len(institutions),
            missing_cost,
            missing_grad,
            missing_both,
        )

    rows.sort(key=lambda item: (item[1].lower(), item[0]))
    return rows


def write_dataset(rows: Iterable[List[object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    for name, config in SEGMENTS.items():
        rows = _build_rows(config["sectors"])
        if not rows:
            raise SystemExit(f"No qualifying institutions found for segment '{name}'.")
        write_dataset(rows, config["output"])
        logger.info("Wrote %d rows to %s", len(rows), config["output"])


if __name__ == "__main__":
    main()
