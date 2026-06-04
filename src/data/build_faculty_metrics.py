"""Build processed instructional-faculty staffing metrics from IPEDS HR (EAP) data.

The IPEDS Human Resources survey reports instructional staff by full-time vs.
part-time status in the "Employees by Assigned Position" (EAP) file. IPEDS has
no "adjunct" category; the universally used proxy is *part-time instructional
staff*. This script extracts the single per-institution total row
(``EAPCAT == 21000`` -- "Instructional staff, total") and derives full-time,
part-time, total counts and the part-time (adjunct proxy) percentage.

Run with::

    python -m src.data.build_faculty_metrics
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Raw inputs. The EAP file sits at the IPEDS root; the institution metadata
# lives in the year-stamped snapshot directory used by the rest of the dashboard.
EAP_PATH = RAW_DIR / "ipeds" / "eap2023.csv"
INSTITUTIONS_PATH = RAW_DIR / "ipeds" / "2023" / "institutions.csv"

CSV_OUTPUT = PROCESSED_DIR / "faculty_metrics.csv"
PARQUET_OUTPUT = PROCESSED_DIR / "faculty_metrics.parquet"

# EAPCAT code for "Instructional staff, total" (all faculty/tenure statuses).
# One row per institution; carries EAPTOT/EAPFT/EAPPT headcounts.
INSTRUCTIONAL_TOTAL_CODE = 21000

SECTOR_LABELS = {
    1: "Public",
    2: "Private, not-for-profit",
    3: "Private, for-profit",
    4: "Public",
    5: "Private, not-for-profit",
    6: "Private, for-profit",
    7: "Public",
    8: "Private, not-for-profit",
    9: "Private, for-profit",
}

OUTPUT_COLUMNS = [
    "UnitID",
    "institution",
    "state",
    "SECTOR",
    "sector",
    "fulltime_faculty",
    "parttime_faculty",
    "total_faculty",
    "pct_parttime",
]


def _load_instructional_totals() -> pd.DataFrame:
    """Read the EAP file and return one instructional-total row per institution."""
    eap = pd.read_csv(
        EAP_PATH,
        usecols=["UNITID", "EAPCAT", "EAPTOT", "EAPFT", "EAPPT"],
    )
    totals = eap[eap["EAPCAT"] == INSTRUCTIONAL_TOTAL_CODE].copy()

    # EAPPT/EAPFT are blank (NaN) when a count is zero; coalesce to 0.
    totals["fulltime_faculty"] = (
        pd.to_numeric(totals["EAPFT"], errors="coerce").fillna(0).round().astype(int)
    )
    totals["parttime_faculty"] = (
        pd.to_numeric(totals["EAPPT"], errors="coerce").fillna(0).round().astype(int)
    )
    totals["total_faculty"] = (
        pd.to_numeric(totals["EAPTOT"], errors="coerce").fillna(0).round().astype(int)
    )
    totals.rename(columns={"UNITID": "UnitID"}, inplace=True)
    return totals[["UnitID", "fulltime_faculty", "parttime_faculty", "total_faculty"]]


def _load_institutions() -> pd.DataFrame:
    """Read institution metadata (name, state, sector) keyed on UnitID."""
    institutions = pd.read_csv(
        INSTITUTIONS_PATH,
        usecols=["UnitID", "INSTITUTION", "STATE", "SECTOR"],
    )
    institutions.rename(
        columns={"INSTITUTION": "institution", "STATE": "state"}, inplace=True
    )
    institutions["SECTOR"] = pd.to_numeric(institutions["SECTOR"], errors="coerce")
    institutions["sector"] = institutions["SECTOR"].map(SECTOR_LABELS).fillna("Unknown")
    return institutions[["UnitID", "institution", "state", "SECTOR", "sector"]]


def build_dataframe() -> pd.DataFrame:
    """Join instructional staffing with institution metadata and derive metrics."""
    totals = _load_instructional_totals()
    institutions = _load_institutions()

    merged = totals.merge(institutions, on="UnitID", how="inner")
    dropped = len(totals) - len(merged)
    if dropped:
        logger.info(
            "Dropped %d of %d EAP institutions with no matching institution metadata.",
            dropped,
            len(totals),
        )

    # Part-time (adjunct proxy) share of instructional staff. Undefined when an
    # institution reports zero instructional staff.
    merged["pct_parttime"] = (
        merged["parttime_faculty"]
        .div(merged["total_faculty"].where(merged["total_faculty"] > 0))
        .mul(100)
        .round(1)
    )

    merged = merged[OUTPUT_COLUMNS].sort_values(
        ["institution", "UnitID"], key=lambda s: s.astype(str).str.lower()
    )
    return merged.reset_index(drop=True)


def _apply_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce to the dashboard dtype conventions before writing Parquet."""
    typed = df.copy()
    typed["UnitID"] = typed["UnitID"].astype("Int32")
    for column in ("fulltime_faculty", "parttime_faculty", "total_faculty"):
        typed[column] = typed[column].astype("Int32")
    typed["SECTOR"] = typed["SECTOR"].astype("Int32")
    typed["pct_parttime"] = typed["pct_parttime"].astype("float32")
    typed["institution"] = typed["institution"].astype("string")
    typed["state"] = typed["state"].astype("category")
    typed["sector"] = typed["sector"].astype("category")
    return typed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    df = build_dataframe()
    if df.empty:
        raise SystemExit("No instructional-faculty rows produced; check EAP inputs.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_OUTPUT, index=False)
    _apply_schema(df).to_parquet(PARQUET_OUTPUT, compression="snappy", index=False)

    logger.info("Wrote %d institutions to %s", len(df), CSV_OUTPUT)
    logger.info("Wrote %d institutions to %s", len(df), PARQUET_OUTPUT)


if __name__ == "__main__":
    main()
