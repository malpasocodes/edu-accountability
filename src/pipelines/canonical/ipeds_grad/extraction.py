"""Phase 02 extraction helpers for IPEDS graduation rates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Iterable, List

import pandas as pd

UNIT_ID_COL = "UnitID"
INST_NAME_COL = "Institution Name"
MELT_VALUE_COL = "grad_rate_150"

SOURCE_PATTERN = re.compile(r"\((DRVGR|DFR)(\d{4})(?:_RV)?\)")


@dataclass
class IPEDSGradExtractionConfig:
    """Configuration for IPEDS graduation-rate extraction."""

    wide_csv: Path
    output_path: Path | None = None
    load_ts: datetime | None = None


class IPEDSGradExtractor:
    """Transforms the IPEDS DRV/DFR wide table into canonical long format."""

    def __init__(self, config: IPEDSGradExtractionConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        """Load, reshape, and optionally persist the canonical long dataframe."""

        wide_df = self._load_wide()
        long_df = self._wide_to_long(wide_df)

        if write_output and self.config.output_path is not None:
            self._write(long_df)

        return long_df

    def _load_wide(self) -> pd.DataFrame:
        if not self.config.wide_csv.exists():
            raise FileNotFoundError(f"Wide IPEDS file not found: {self.config.wide_csv}")

        return pd.read_csv(self.config.wide_csv)

    def _wide_to_long(self, frame: pd.DataFrame) -> pd.DataFrame:
        id_vars = [UNIT_ID_COL, INST_NAME_COL]
        value_cols = [col for col in frame.columns if col not in id_vars]

        column_meta = self._build_column_metadata(value_cols)
        if not column_meta:
            raise ValueError("No DRV/DFR columns detected in the wide IPEDS file.")

        melted = frame.melt(
            id_vars=id_vars,
            value_vars=list(column_meta.keys()),
            var_name="_original_column",
            value_name=MELT_VALUE_COL,
        )

        melted = melted.merge(
            pd.DataFrame.from_records(list(column_meta.values())),
            left_on="_original_column",
            right_on="column_name",
            how="left",
        )

        melted[MELT_VALUE_COL] = pd.to_numeric(melted[MELT_VALUE_COL], errors="coerce")
        melted = melted.dropna(subset=[MELT_VALUE_COL])

        melted.rename(
            columns={UNIT_ID_COL: "unitid", INST_NAME_COL: "instnm"}, inplace=True
        )

        melted["unitid"] = melted["unitid"].astype("Int64")
        melted["year"] = melted["year"].astype("int16")
        melted[MELT_VALUE_COL] = melted[MELT_VALUE_COL].astype("float32")

        melted["cohort_reference"] = (
            melted["year"].astype(str) + " cohort, total cohort"
        )

        load_ts = self.config.load_ts or datetime.now(timezone.utc)
        melted["load_ts"] = pd.Timestamp(load_ts).tz_convert(None)

        # Placeholder columns for metadata enrichment in Phase 03.
        for col in ("control", "level", "state", "sector"):
            melted[col] = pd.Series(pd.NA, index=melted.index, dtype="string")

        melted = melted[
            [
                "unitid",
                "year",
                "instnm",
                "control",
                "level",
                "state",
                "sector",
                MELT_VALUE_COL,
                "source_flag",
                "is_revised",
                "cohort_reference",
                "load_ts",
            ]
        ]

        return melted.sort_values(["unitid", "year"]).reset_index(drop=True)

    def _write(self, df: pd.DataFrame) -> None:
        assert self.config.output_path is not None
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.config.output_path, index=False)

    @staticmethod
    def _build_column_metadata(columns: Iterable[str]) -> dict[str, dict]:
        metadata: dict[str, dict] = {}
        for col in columns:
            match = SOURCE_PATTERN.search(col)
            if not match:
                continue
            source_flag, year = match.groups()
            metadata[col] = {
                "column_name": col,
                "source_flag": source_flag,
                "year": int(year),
                "is_revised": "_RV" in col,
            }
        return metadata


def main() -> None:
    """CLI entry point for Phase 02 extraction."""

    input_path = Path("data/raw/ipeds/grad_rates_2004_2023.csv")
    output_path = Path("data/processed/2023/canonical/ipeds_grad_rates_long.parquet")
    extractor = IPEDSGradExtractor(
        IPEDSGradExtractionConfig(wide_csv=input_path, output_path=output_path)
    )
    df = extractor.run(write_output=True)
    print(f"Extracted {len(df)} rows to {output_path}.")


if __name__ == "__main__":
    main()
