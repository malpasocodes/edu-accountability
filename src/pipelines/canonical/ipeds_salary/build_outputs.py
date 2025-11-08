"""Build canonical outputs for the instructional staff salary dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path

import pandas as pd


@dataclass
class SalaryBuildConfig:
    long_parquet: Path
    latest_parquet: Path
    summary_parquet: Path
    metadata_json: Path
    value_column: str = "avg_salary_9mo_all_ranks"


class IPEDSSalaryBuilder:
    """Generates latest/summary outputs for instructional staff salaries."""

    def __init__(self, config: SalaryBuildConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> dict[str, pd.DataFrame]:
        long_df = self._load_long()
        latest = self._latest_by_institution(long_df)
        summary = self._summary_by_year(long_df)

        if write_output:
            self._write_outputs(latest, summary)
            self._write_metadata(long_df, latest, summary)

        return {"long": long_df, "latest": latest, "summary": summary}

    def _load_long(self) -> pd.DataFrame:
        if not self.config.long_parquet.exists():
            raise FileNotFoundError(self.config.long_parquet)
        return pd.read_parquet(self.config.long_parquet)

    def _latest_by_institution(self, df: pd.DataFrame) -> pd.DataFrame:
        ordered = df.sort_values(["unitid", "year"])
        latest = ordered.drop_duplicates(subset=["unitid"], keep="last")
        return latest.reset_index(drop=True)

    def _summary_by_year(self, df: pd.DataFrame) -> pd.DataFrame:
        working = df.copy()
        working["sector"] = working["sector"].fillna("Unknown")
        value = self.config.value_column

        summary = (
            working.groupby(["year", "sector"], dropna=False)
            .agg(
                institution_count=("unitid", "nunique"),
                avg_value=(value, "mean"),
                median_value=(value, "median"),
                p25_value=(value, lambda s: s.quantile(0.25)),
                p75_value=(value, lambda s: s.quantile(0.75)),
            )
            .reset_index()
        )
        return summary

    def _write_outputs(self, latest: pd.DataFrame, summary: pd.DataFrame) -> None:
        self.config.latest_parquet.parent.mkdir(parents=True, exist_ok=True)
        self.config.summary_parquet.parent.mkdir(parents=True, exist_ok=True)
        latest.to_parquet(self.config.latest_parquet, index=False)
        summary.to_parquet(self.config.summary_parquet, index=False)

    def _write_metadata(
        self, long_df: pd.DataFrame, latest: pd.DataFrame, summary: pd.DataFrame
    ) -> None:
        metadata = {
            "build_ts": datetime.now(timezone.utc).isoformat(),
            "source_file": str(self.config.long_parquet),
            "source_rows": int(len(long_df)),
            "latest_rows": int(len(latest)),
            "summary_rows": int(len(summary)),
            "year_range": [
                int(long_df["year"].min()) if not long_df.empty else None,
                int(long_df["year"].max()) if not long_df.empty else None,
            ],
        }

        self.config.metadata_json.parent.mkdir(parents=True, exist_ok=True)
        self.config.metadata_json.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build canonical outputs for instructional staff salaries."
    )
    parser.add_argument(
        "--long-parquet",
        default=Path(
            "data/processed/2023/canonical/ipeds_avg_salary_instructional_staff_long.parquet"
        ),
        type=Path,
    )
    parser.add_argument(
        "--latest-parquet",
        default=Path(
            "data/processed/2023/canonical/ipeds_avg_salary_instructional_staff_latest_by_inst.parquet"
        ),
        type=Path,
    )
    parser.add_argument(
        "--summary-parquet",
        default=Path(
            "data/processed/2023/canonical/ipeds_avg_salary_instructional_staff_summary_by_year.parquet"
        ),
        type=Path,
    )
    parser.add_argument(
        "--metadata-json",
        default=Path("out/canonical/ipeds_avg_salary_instructional_staff/run_latest.json"),
        type=Path,
    )
    args = parser.parse_args()

    config = SalaryBuildConfig(
        long_parquet=args.long_parquet,
        latest_parquet=args.latest_parquet,
        summary_parquet=args.summary_parquet,
        metadata_json=args.metadata_json,
    )
    builder = IPEDSSalaryBuilder(config)
    frames = builder.run(write_output=True)
    print(
        "Built salary outputs:",
        f"long={len(frames['long'])}",
        f"latest={len(frames['latest'])}",
        f"summary={len(frames['summary'])}",
    )


if __name__ == "__main__":
    main()
