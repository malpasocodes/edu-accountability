"""Build canonical outputs for SFA percentage datasets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path

import pandas as pd


@dataclass
class SFABuildConfig:
    long_parquet: Path
    latest_parquet: Path
    summary_parquet: Path
    metadata_json: Path
    value_column: str


class SFABuilder:
    def __init__(self, config: SFABuildConfig):
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

    def _write_metadata(self, long_df: pd.DataFrame, latest: pd.DataFrame, summary: pd.DataFrame) -> None:
        metadata = {
            "build_ts": datetime.now(timezone.utc).isoformat(),
            "source_file": str(self.config.long_parquet),
            "source_rows": int(len(long_df)),
            "latest_rows": int(len(latest)),
            "summary_rows": int(len(summary)),
            "year_range": [int(long_df["year"].min()), int(long_df["year"].max())],
        }

        self.config.metadata_json.parent.mkdir(parents=True, exist_ok=True)
        self.config.metadata_json.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical outputs for SFA datasets.")
    parser.add_argument("--dataset", choices=["pell", "loans"], default="pell")
    args = parser.parse_args()

    mapping = {
        "pell": SFABuildConfig(
            long_parquet=Path("data/processed/2023/canonical/ipeds_percent_pell_long.parquet"),
            latest_parquet=Path("data/processed/2023/canonical/ipeds_percent_pell_latest_by_inst.parquet"),
            summary_parquet=Path("data/processed/2023/canonical/ipeds_percent_pell_summary_by_year.parquet"),
            metadata_json=Path("out/canonical/ipeds_pell/run_latest.json"),
            value_column="percent_pell",
        ),
        "loans": SFABuildConfig(
            long_parquet=Path("data/processed/2023/canonical/ipeds_percent_loans_long.parquet"),
            latest_parquet=Path("data/processed/2023/canonical/ipeds_percent_loans_latest_by_inst.parquet"),
            summary_parquet=Path("data/processed/2023/canonical/ipeds_percent_loans_summary_by_year.parquet"),
            metadata_json=Path("out/canonical/ipeds_loans/run_latest.json"),
            value_column="percent_loans",
        ),
    }

    config = mapping[args.dataset]
    builder = SFABuilder(config)
    frames = builder.run(write_output=True)
    print(
        f"Built {args.dataset} outputs:",
        f"long={len(frames['long'])}",
        f"latest={len(frames['latest'])}",
        f"summary={len(frames['summary'])}",
    )


if __name__ == "__main__":
    main()
