"""Extraction for College Scorecard institutional metrics.

Focus: median debt (completers) and 3-year borrower-based repayment breakdown.
Reads MERGED* files from the Scorecard ZIP to build a year-indexed long table.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import io
import re
import zipfile
from typing import Iterable

import pandas as pd

from src.pipelines.canonical.ipeds_grad.enrich_metadata import CONTROL_MAP


MERGED_PATTERN = re.compile(r"MERGED(\d{4})_(\d{2})_PP\.csv$", re.IGNORECASE)


@dataclass
class ScorecardExtractionConfig:
    zip_path: Path
    output_path: Path | None = None


SCORECARD_TO_LEVEL = {
    3: "4-year",
    2: "2-year",
    1: "<2-year",
    4: "+grad",  # graduate-only; treat as 4-year+ in UI
}


REPAY3_COLUMNS = {
    "repay_3yr_default": "BBRR3_FED_UG_DFLT",
    "repay_3yr_delinquent": "BBRR3_FED_UG_DLNQ",
    "repay_3yr_forbearance": "BBRR3_FED_UG_FBR",
    "repay_3yr_deferment": "BBRR3_FED_UG_DFR",
    "repay_3yr_not_making_progress": "BBRR3_FED_UG_NOPROG",
    "repay_3yr_making_progress": "BBRR3_FED_UG_MAKEPROG",
    "repay_3yr_paid_in_full": "BBRR3_FED_UG_PAIDINFULL",
    "repay_3yr_discharged": "BBRR3_FED_UG_DISCHARGE",
}


BASE_COLUMNS = [
    "UNITID",
    "INSTNM",
    "STABBR",
    "CONTROL",
    "PREDDEG",
]


def _iter_merged_members(zf: zipfile.ZipFile) -> Iterable[zipfile.ZipInfo]:
    for info in zf.infolist():
        name = info.filename
        if name.endswith(".csv") and \
           "/" in name and \
           MERGED_PATTERN.search(Path(name).name):
            yield info


def _year_from_name(name: str) -> int:
    m = MERGED_PATTERN.search(name)
    if not m:
        raise ValueError(f"Unrecognized MERGED file name: {name}")
    start, end2 = int(m.group(1)), int(m.group(2))
    # Example MERGED2023_24 -> year 2024
    end_year = (start // 100) * 100 + end2
    if end_year < start:  # roll to next century safeguard
        end_year += 100
    return end_year


class ScorecardExtractor:
    """Builds a long table for selected Scorecard metrics across years."""

    def __init__(self, config: ScorecardExtractionConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        zpath = self.config.zip_path
        if not zpath.exists():
            raise FileNotFoundError(zpath)

        frames: list[pd.DataFrame] = []
        with zipfile.ZipFile(zpath, "r") as zf:
            for member in _iter_merged_members(zf):
                year = _year_from_name(Path(member.filename).name)
                with zf.open(member, "r") as fh:
                    data = fh.read()
                csv_buf = io.BytesIO(data)
                usecols = BASE_COLUMNS + ["GRAD_DEBT_MDN"] + list(REPAY3_COLUMNS.values())
                df = pd.read_csv(csv_buf, usecols=[c for c in usecols if c])
                df["year"] = year
                frames.append(df)

        if not frames:
            raise ValueError("No MERGED* files found in Scorecard ZIP.")

        wide = pd.concat(frames, ignore_index=True)

        # Normalize columns
        wide = wide.rename(columns={
            "UNITID": "unitid",
            "INSTNM": "instnm",
            "STABBR": "state",
            "CONTROL": "control_code",
            "PREDDEG": "preddeg",
        })

        # Control/level strings
        wide["control"] = wide["control_code"].map(CONTROL_MAP).astype("string")
        wide["level"] = wide["preddeg"].map(SCORECARD_TO_LEVEL).astype("string")

        # Coerce numeric fields
        wide["unitid"] = pd.to_numeric(wide["unitid"], errors="coerce").astype("Int64")
        wide["year"] = wide["year"].astype("int16")
        wide["instnm"] = wide["instnm"].astype("string")
        wide["state"] = wide["state"].astype("string")

        # Median debt
        wide["median_debt_completers"] = pd.to_numeric(wide["GRAD_DEBT_MDN"], errors="coerce").astype("float32")

        # Repayment shares (as percent 0..100)
        for new_col, src in REPAY3_COLUMNS.items():
            wide[new_col] = pd.to_numeric(wide[src], errors="coerce").astype("float32") * 100.0

        columns = [
            "unitid", "year", "instnm", "state", "control", "level",
            "median_debt_completers",
        ] + list(REPAY3_COLUMNS.keys())
        long = wide[columns].sort_values(["unitid", "year"]).reset_index(drop=True)

        if write_output and self.config.output_path is not None:
            self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
            long.to_parquet(self.config.output_path, index=False)

        return long


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Scorecard MERGED files from ZIP.")
    parser.add_argument(
        "--zip",
        type=Path,
        default=Path("data/raw/college_scorecard/College_Scorecard_Raw_Data_05192025.zip"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/2023/canonical/scorecard_debt_repayment_long.parquet"),
    )
    args = parser.parse_args()

    cfg = ScorecardExtractionConfig(zip_path=args.zip, output_path=args.output)
    df = ScorecardExtractor(cfg).run(write_output=True)
    print(f"Extracted rows: {len(df)}; years {df['year'].min()}–{df['year'].max()}")


if __name__ == "__main__":
    main()

