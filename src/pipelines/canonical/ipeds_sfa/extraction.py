"""Extraction helpers for IPEDS SFA percentage datasets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


SOURCE_PATTERN = re.compile(r"\(SFA(\d{2})(\d{2})(?:_RV)?\)")


@dataclass
class SFAPercentExtractionConfig:
    wide_csv: Path
    value_column: str
    output_path: Path | None = None
    metric_label: str = "Pell"


class SFAPercentExtractor:
    """Converts the IPEDS SFA percentage tables into long format."""

    def __init__(self, config: SFAPercentExtractionConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
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
        id_vars = ["UnitID", "Institution Name"]
        value_cols = [col for col in frame.columns if col not in id_vars]

        column_meta = self._build_column_metadata(value_cols)
        if not column_meta:
            raise ValueError("No SFA columns detected in the input file.")

        melted = frame.melt(
            id_vars=id_vars,
            value_vars=list(column_meta.keys()),
            var_name="_original_column",
            value_name=self.config.value_column,
        )

        meta_df = pd.DataFrame.from_records(list(column_meta.values()))
        melted = melted.merge(meta_df, left_on="_original_column", right_on="column_name", how="left")

        melted[self.config.value_column] = pd.to_numeric(melted[self.config.value_column], errors="coerce")
        melted = melted.dropna(subset=[self.config.value_column])

        melted = melted.rename(columns={"UnitID": "unitid", "Institution Name": "instnm"})
        melted["unitid"] = melted["unitid"].astype("Int64")
        melted["year"] = melted["year"].astype("int16")
        melted[self.config.value_column] = melted[self.config.value_column].astype("float32")

        melted["cohort_reference"] = melted.apply(
            lambda row: f"{row['aid_year']} {self.config.metric_label}", axis=1
        )

        load_ts = datetime.now(timezone.utc)
        melted["load_ts"] = pd.Timestamp(load_ts).tz_convert(None)

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
        output_path = self.config.output_path
        assert output_path is not None
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)

    @staticmethod
    def _build_column_metadata(columns: Iterable[str]) -> dict[str, dict]:
        metadata: dict[str, dict] = {}
        for col in columns:
            match = SOURCE_PATTERN.search(col)
            if not match:
                continue
            start_digits, end_digits = match.groups()
            start_year = 2000 + int(start_digits)
            end_year = 2000 + int(end_digits)
            metadata[col] = {
                "column_name": col,
                "source_flag": "SFA",
                "year": end_year,
                "aid_year": f"{start_year}-{str(end_year)[-2:]}",
                "is_revised": "_RV" in col,
            }
        return metadata


def main() -> None:
    config = SFAPercentExtractionConfig(
        wide_csv=Path("data/raw/ipeds/percent_pell_grants.csv"),
        value_column="percent_pell",
        output_path=Path("data/processed/2023/canonical/ipeds_percent_pell_long.parquet"),
        metric_label="Pell",
    )
    extractor = SFAPercentExtractor(config)
    df = extractor.run(write_output=True)
    print(f"Extracted {len(df)} rows of percent Pell grants data.")


if __name__ == "__main__":
    main()
