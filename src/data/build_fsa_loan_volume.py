"""Build a tidy federal Direct Loan volume dataset from FSA's official reports.

Source: FSA Title IV Program Volume Reports — "Direct Loan Volume by School"
(https://studentaid.gov/data-center/student/title-iv). One Excel workbook per
award year; the "Award Year Summary" tab carries full-year (Q4 cumulative)
recipients and disbursements per school, broken out into five loan types:
Subsidized, Unsubsidized-Undergraduate, Unsubsidized-Graduate, Parent PLUS,
and Grad PLUS. Data come from the Common Origination and Disbursement (COD)
system and are the Department of Education's official disbursement figures.

The raw workbooks live in ``data/raw/fsa/dl_volume/`` (award years 2012-13
through 2021-22; AY2012-13 was recovered from the Internet Archive after FSA
removed it from the live site — see ``data/raw/fsa/metadata.yaml``).

Schools are keyed by 8-digit OPE ID, *not* IPEDS UnitID: one row covers the
whole institution (e.g. all University of Phoenix campuses appear as the
single OPE ID 02098800).

NOTE: this dataset supersedes ``data/raw/fsa/loantotals.csv`` for dollar
amounts. That legacy file (an FSA "LoanBySchool.csv" download whose exact
definition is undocumented) runs at roughly 40-60% of the COD disbursement
figures and should not be used for loan-dollar totals.

Requires ``xlrd`` (legacy .xls support; in the dev dependency group).

Run with::

    python -m src.data.build_fsa_loan_volume
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fsa" / "dl_volume"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CSV_OUTPUT = PROCESSED_DIR / "fsa_dl_volume.csv"
PARQUET_OUTPUT = PROCESSED_DIR / "fsa_dl_volume.parquet"

SHEET_NAME = "Award Year Summary"

# Workbook filename pattern: dl_volume_ay2012_2013_q4.xls
FILENAME_PATTERN = re.compile(r"dl_volume_ay(\d{4})_(\d{4})_q4\.xls$")

# Loan-type block labels as they appear (with whitespace variants) in the
# header band above the column names, normalised to snake_case keys.
LOAN_TYPE_LABELS = {
    "DL SUBSIDIZED": "subsidized",
    "DL UNSUBSIDIZED-UNDERGRADUATE": "unsub_undergrad",
    "DL UNSUBSIDIZED-GRADUATE": "unsub_grad",
    "DL PARENT PLUS": "parent_plus",
    "DL GRAD PLUS": "grad_plus",
}

OUTPUT_COLUMNS = [
    "opeid",
    "school",
    "state",
    "award_year",
    "year",
    "loan_type",
    "recipients",
    "disbursed_usd",
]


def _normalize_label(value: object) -> str:
    """Collapse spacing variants like ``DL UNSUBSIDIZED - UNDERGRADUATE``."""
    text = re.sub(r"\s*-\s*", "-", str(value).strip().upper())
    return re.sub(r"\s+", " ", text)


def _parse_workbook(path: Path) -> pd.DataFrame:
    """Return tidy per-school, per-loan-type rows for one award-year file."""
    match = FILENAME_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"Unexpected workbook filename: {path.name}")
    start_year, end_year = int(match.group(1)), int(match.group(2))
    award_year = f"{start_year}-{str(end_year)[2:]}"

    raw = pd.read_excel(path, sheet_name=SHEET_NAME, header=None)

    header_rows = raw.index[raw[0].astype(str).str.strip().isin(["OPE ID", "OPEID"])]
    if len(header_rows) == 0:
        raise ValueError(f"No 'OPE ID' header row found in {path.name}")
    header_row = header_rows[0]

    # The row above the column headers names the loan-type block; each block
    # spans five columns (recipients, loans originated #/$, disbursements #/$).
    block_row = raw.iloc[header_row - 1]
    column_names = raw.iloc[header_row].astype(str).str.strip()

    current_block: str | None = None
    block_by_column: dict[int, str | None] = {}
    for col in raw.columns:
        label = block_row[col]
        if isinstance(label, str) and label.strip():
            normalized = _normalize_label(label)
            current_block = LOAN_TYPE_LABELS.get(normalized, normalized)
        block_by_column[col] = current_block

    data = raw.iloc[header_row + 1 :].copy()
    # Keep only real school rows (numeric OPE ID); drops footnotes/totals.
    opeid = data[0].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    data = data[opeid.str.fullmatch(r"\d{6,8}")]
    data[0] = opeid.str.zfill(8)

    frames = []
    for loan_type in LOAN_TYPE_LABELS.values():
        block_cols = [c for c, b in block_by_column.items() if b == loan_type]
        recipients_cols = [c for c in block_cols if column_names[c] == "Recipients"]
        disbursed_cols = [
            c for c in block_cols if column_names[c] == "$ of Disbursements"
        ]
        if not recipients_cols or not disbursed_cols:
            raise ValueError(f"Missing '{loan_type}' columns in {path.name}")
        frame = pd.DataFrame(
            {
                "opeid": data[0],
                "school": data[1].astype(str).str.strip(),
                "state": data[2].astype(str).str.strip(),
                "award_year": award_year,
                "year": end_year,
                "loan_type": loan_type,
                "recipients": pd.to_numeric(data[recipients_cols[0]], errors="coerce"),
                "disbursed_usd": pd.to_numeric(
                    data[disbursed_cols[0]], errors="coerce"
                ),
            }
        )
        frames.append(frame)

    tidy = pd.concat(frames, ignore_index=True)
    # Drop empty combinations (school did not participate in that loan type).
    tidy = tidy[
        (tidy["recipients"].fillna(0) > 0) | (tidy["disbursed_usd"].fillna(0) > 0)
    ]
    logger.info("%s: %d rows", path.name, len(tidy))
    return tidy


def build_fsa_loan_volume() -> pd.DataFrame:
    """Parse every workbook in ``data/raw/fsa/dl_volume/`` into one dataset."""
    paths = sorted(RAW_DIR.glob("dl_volume_ay*_q4.xls"))
    if not paths:
        raise FileNotFoundError(f"No DL volume workbooks found in {RAW_DIR}")

    tidy = pd.concat([_parse_workbook(p) for p in paths], ignore_index=True)

    tidy["year"] = tidy["year"].astype("Int32")
    tidy["recipients"] = tidy["recipients"].round().astype("Int32")
    # Whole dollars; int64 keeps decade sums exact (float32 would round).
    tidy["disbursed_usd"] = tidy["disbursed_usd"].fillna(0).round().astype("int64")
    tidy["state"] = tidy["state"].astype("category")
    tidy["loan_type"] = tidy["loan_type"].astype("category")
    tidy["school"] = tidy["school"].astype("string")
    tidy["opeid"] = tidy["opeid"].astype("string")

    return tidy[OUTPUT_COLUMNS].sort_values(["year", "opeid", "loan_type"])


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    dataset = build_fsa_loan_volume()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(CSV_OUTPUT, index=False)
    dataset.to_parquet(PARQUET_OUTPUT, compression="snappy", index=False)
    logger.info(
        "Wrote %d rows for %d award years to %s / %s",
        len(dataset),
        dataset["award_year"].nunique(),
        CSV_OUTPUT.name,
        PARQUET_OUTPUT.name,
    )


if __name__ == "__main__":
    main()
