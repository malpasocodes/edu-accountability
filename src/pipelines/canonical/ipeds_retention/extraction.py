"""Extraction helpers for canonical IPEDS retention cohorts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import re
from pathlib import Path
from typing import Iterable, Pattern

import pandas as pd


UNIT_ID_COL = "UnitID"
INST_NAME_COL = "Institution Name"

FULL_TIME_PATTERN = re.compile(
    r"Full-time fall (?P<cohort_year>\d{4}) cohort\s+\((?P<source_flag>EF\d{4}D)(?P<revision>_RV)?\)",
    re.IGNORECASE,
)

FULL_TIME_RATE_PATTERN = re.compile(
    r"Full-time retention rate\s+(?P<cohort_year>\d{4})?\s*\((?P<source_flag>EF\d{4}D)(?P<revision>_RV)?\)",
    re.IGNORECASE,
)


@dataclass
class IPEDSRetentionExtractionConfig:
    """Configuration for transforming retention wide files."""

    wide_csv: Path
    value_column: str
    column_pattern: Pattern[str]
    cohort_label_template: str
    output_path: Path | None = None
    load_ts: datetime | None = None
    value_dtype: str = "Int64"
    round_values: bool = False
    year_offset_from_source: int = 0


class IPEDSRetentionExtractor:
    """Converts the retention wide table into canonical long format."""

    def __init__(self, config: IPEDSRetentionExtractionConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        """Execute the extraction pipeline."""

        wide_df = self._load_wide()
        long_df = self._wide_to_long(wide_df)

        if write_output and self.config.output_path is not None:
            self._write(long_df)

        return long_df

    def _load_wide(self) -> pd.DataFrame:
        if not self.config.wide_csv.exists():
            raise FileNotFoundError(self.config.wide_csv)
        return pd.read_csv(self.config.wide_csv)

    def _wide_to_long(self, frame: pd.DataFrame) -> pd.DataFrame:
        id_vars = [UNIT_ID_COL, INST_NAME_COL]
        value_columns = [
            col for col in frame.columns if col not in id_vars and col and col.strip()
        ]

        column_meta = self._build_column_metadata(value_columns)
        if not column_meta:
            raise ValueError("No Full-time retention columns detected.")

        melted = frame.melt(
            id_vars=id_vars,
            value_vars=list(column_meta.keys()),
            var_name="_original_column",
            value_name=self.config.value_column,
        )

        meta_df = pd.DataFrame.from_records(list(column_meta.values()))
        melted = melted.merge(
            meta_df, left_on="_original_column", right_on="column_name", how="left"
        )

        melted[self.config.value_column] = pd.to_numeric(
            melted[self.config.value_column], errors="coerce"
        )
        melted = melted.dropna(subset=[self.config.value_column])

        if self.config.round_values:
            melted[self.config.value_column] = melted[self.config.value_column].round()

        melted[self.config.value_column] = melted[self.config.value_column].astype(
            self.config.value_dtype
        )

        melted = melted.rename(columns={UNIT_ID_COL: "unitid", INST_NAME_COL: "instnm"})
        melted["unitid"] = melted["unitid"].astype("Int64")
        melted["instnm"] = melted["instnm"].astype("string")
        melted["year"] = melted["cohort_year"].astype("int16")
        melted["source_flag"] = melted["source_flag"].astype("string")
        melted["is_revised"] = melted["is_revised"].astype("boolean")

        load_ts = self.config.load_ts or datetime.now(timezone.utc)
        melted["load_ts"] = pd.Timestamp(load_ts).tz_convert(None)

        melted["cohort_reference"] = melted.apply(
            lambda row: self.config.cohort_label_template.format(
                year=row["year"], source_flag=row["source_flag"]
            ),
            axis=1,
        )

        for col in ("control", "level", "state", "sector"):
            melted[col] = pd.Series(pd.NA, index=melted.index, dtype="string")

        ordered_columns = [
            "unitid",
            "year",
            "instnm",
            "control",
            "level",
            "state",
            "sector",
            self.config.value_column,
            "source_flag",
            "is_revised",
            "cohort_reference",
            "load_ts",
        ]

        melted = melted[ordered_columns]
        return melted.sort_values(["unitid", "year"]).reset_index(drop=True)

    def _write(self, df: pd.DataFrame) -> None:
        assert self.config.output_path is not None
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.config.output_path, index=False)

    def _build_column_metadata(self, columns: Iterable[str]) -> dict[str, dict]:
        metadata: dict[str, dict] = {}
        for column in columns:
            match = self.config.column_pattern.search(column)
            if not match:
                continue
            source_flag = match.group("source_flag")
            cohort_year = match.group("cohort_year")
            if cohort_year:
                year = int(cohort_year)
            else:
                year = int(source_flag[2:6]) - self.config.year_offset_from_source
            metadata[column] = {
                "column_name": column,
                "cohort_year": year,
                "source_flag": source_flag,
                "is_revised": bool(match.group("revision")),
            }
        return metadata


def _build_config(dataset: str) -> IPEDSRetentionExtractionConfig:
    base_dir = Path("data")
    raw_dir = base_dir / "raw" / "ipeds"
    processed_dir = base_dir / "processed" / "2023" / "canonical"

    if dataset == "counts":
        return IPEDSRetentionExtractionConfig(
            wide_csv=raw_dir / "retention_rates.csv",
            value_column="retained_students_full_time",
            column_pattern=FULL_TIME_PATTERN,
            cohort_label_template="Full-time fall {year} cohort ({source_flag})",
            output_path=processed_dir / "ipeds_retention_full_time_long.parquet",
            round_values=True,
            value_dtype="Int64",
            year_offset_from_source=1,
        )
    if dataset == "pct":
        return IPEDSRetentionExtractionConfig(
            wide_csv=raw_dir / "retention_rate_pctgs.csv",
            value_column="retention_rate_full_time",
            column_pattern=FULL_TIME_RATE_PATTERN,
            cohort_label_template="Full-time retention rate {year} ({source_flag})",
            output_path=processed_dir / "ipeds_retention_rate_full_time_long.parquet",
            round_values=False,
            value_dtype="float32",
            year_offset_from_source=0,
        )
    raise ValueError(f"Unsupported dataset: {dataset}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract canonical retention datasets."
    )
    parser.add_argument(
        "--dataset",
        choices=["counts", "pct"],
        default="counts",
        help="Which retention dataset to process (counts or percentages).",
    )
    args = parser.parse_args()

    config = _build_config(args.dataset)
    extractor = IPEDSRetentionExtractor(config)
    df = extractor.run(write_output=True)
    print(f"Extracted {len(df)} canonical retention rows for dataset {args.dataset}.")


if __name__ == "__main__":
    main()
