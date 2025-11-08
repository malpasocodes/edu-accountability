"""Extraction helpers for IPEDS instructional staff salary datasets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import re
from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_grad.enrich_metadata import (
    CONTROL_MAP,
    LEVEL_MAP,
    SECTOR_MAP,
)


SALARY_PATTERN = re.compile(
    r"\((?P<source_flag>DRVHR(?P<year>\d{4}))(?P<revision>_RV)?\)",
    re.IGNORECASE,
)


@dataclass
class IPEDSSalaryExtractionConfig:
    """Configuration for converting the salary table to canonical long format."""

    wide_csv: Path
    hd_csv: Path
    output_path: Path | None = None
    value_column: str = "avg_salary_9mo_all_ranks"
    metric_label: str = "Instructional Staff Avg Salary (9mo)"
    load_ts: datetime | None = None


class IPEDSSalaryExtractor:
    """Transforms the instructional staff salary wide table into a canonical long table."""

    def __init__(self, config: IPEDSSalaryExtractionConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        wide_df = self._load_wide()
        long_df = self._wide_to_long(wide_df)
        enriched = self._enrich_with_hd(long_df)

        if write_output and self.config.output_path is not None:
            self._write(enriched)

        return enriched

    def _load_wide(self) -> pd.DataFrame:
        if not self.config.wide_csv.exists():
            raise FileNotFoundError(self.config.wide_csv)
        return pd.read_csv(self.config.wide_csv)

    def _wide_to_long(self, frame: pd.DataFrame) -> pd.DataFrame:
        id_vars = ["UnitID", "Institution Name"]
        value_columns = [col for col in frame.columns if col not in id_vars and col.strip()]

        column_meta = self._build_column_metadata(value_columns)
        if not column_meta:
            raise ValueError("No DRVHR salary columns detected in the input file.")

        melted = frame.melt(
            id_vars=id_vars,
            value_vars=list(column_meta.keys()),
            var_name="_original_column",
            value_name=self.config.value_column,
        )

        meta_df = pd.DataFrame.from_records(list(column_meta.values()))
        melted = melted.merge(
            meta_df,
            left_on="_original_column",
            right_on="column_name",
            how="left",
        )
        melted = melted.drop(columns=["_original_column", "column_name"])

        value_col = self.config.value_column
        melted[value_col] = pd.to_numeric(melted[value_col], errors="coerce")
        melted = melted.dropna(subset=[value_col])

        melted = melted.rename(columns={"UnitID": "unitid", "Institution Name": "instnm"})
        melted["unitid"] = melted["unitid"].astype("Int64")
        melted["instnm"] = melted["instnm"].astype("string")
        melted[value_col] = melted[value_col].astype("float32")
        melted["year"] = melted["year"].astype("int16")
        melted["source_flag"] = melted["source_flag"].astype("string")
        melted["is_revised"] = melted["is_revised"].astype("boolean")

        load_ts = self.config.load_ts or datetime.now(timezone.utc)
        melted["load_ts"] = pd.Timestamp(load_ts).tz_convert(None)
        melted["cohort_reference"] = melted.apply(
            lambda row: f"{row['year']} {self.config.metric_label}", axis=1
        )

        return melted.sort_values(["unitid", "year"]).reset_index(drop=True)

    def _build_column_metadata(self, columns: list[str]) -> dict[str, dict]:
        metadata: dict[str, dict] = {}
        for column in columns:
            match = SALARY_PATTERN.search(column)
            if not match:
                continue
            metadata[column] = {
                "column_name": column,
                "source_flag": match.group("source_flag").upper(),
                "year": int(match.group("year")),
                "is_revised": bool(match.group("revision")),
            }
        return metadata

    def _enrich_with_hd(self, frame: pd.DataFrame) -> pd.DataFrame:
        hd_df = self._load_hd()
        enriched = frame.merge(hd_df, on="unitid", how="left", validate="many_to_one")

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
        remaining = [col for col in enriched.columns if col not in ordered_columns]
        enriched = enriched[ordered_columns + remaining]
        return enriched

    def _load_hd(self) -> pd.DataFrame:
        if not self.config.hd_csv.exists():
            raise FileNotFoundError(self.config.hd_csv)

        df = pd.read_csv(
            self.config.hd_csv,
            dtype={"UnitID": "Int64"},
            usecols=["UnitID", "STATE", "LEVEL", "CONTROL", "SECTOR"],
        )
        df = df.rename(
            columns={
                "UnitID": "unitid",
                "STATE": "state",
                "LEVEL": "level_code",
                "CONTROL": "control_code",
                "SECTOR": "sector_code",
            }
        )

        df["state"] = df["state"].astype("string")
        df["control"] = df["control_code"].map(CONTROL_MAP).astype("string")
        df["level"] = df["level_code"].map(LEVEL_MAP).astype("string")
        df["sector"] = df["sector_code"].map(SECTOR_MAP).astype("string")

        return df[["unitid", "state", "control", "level", "sector"]]

    def _write(self, df: pd.DataFrame) -> None:
        assert self.config.output_path is not None
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.config.output_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract canonical IPEDS instructional staff salary datasets."
    )
    parser.add_argument(
        "--wide-csv",
        default=Path("data/raw/ipeds/avgsalaries_instructionalstaff_9months.csv"),
        type=Path,
        help="Path to the DRVHR wide CSV",
    )
    parser.add_argument(
        "--hd-csv",
        default=Path("data/raw/ipeds/2023/institutions.csv"),
        type=Path,
        help="Path to the IPEDS HD file for metadata enrichment",
    )
    parser.add_argument(
        "--output",
        default=Path(
            "data/processed/2023/canonical/ipeds_avg_salary_instructional_staff_long.parquet"
        ),
        type=Path,
        help="Where to write the canonical long-format parquet",
    )
    args = parser.parse_args()

    config = IPEDSSalaryExtractionConfig(
        wide_csv=args.wide_csv,
        hd_csv=args.hd_csv,
        output_path=args.output,
    )
    extractor = IPEDSSalaryExtractor(config)
    df = extractor.run(write_output=True)
    print(f"Extracted {len(df)} instructional salary rows.")


if __name__ == "__main__":
    main()
