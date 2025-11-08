"""Build canonical outputs for IPEDS retention cohorts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import json
import subprocess
from pathlib import Path

import pandas as pd


@dataclass
class RetentionBuildConfig:
    long_parquet: Path
    latest_parquet: Path
    summary_parquet: Path
    metadata_json: Path
    value_column: str
    summary_prefix: str


class RetentionOutputBuilder:
    """Generate latest/summary tables plus provenance metadata."""

    def __init__(self, config: RetentionBuildConfig):
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
        prefix = self.config.summary_prefix

        summary = (
            working.groupby(["year", "sector"], dropna=False)
            .agg(
                institution_count=("unitid", "nunique"),
                **{
                    f"avg_{prefix}": (value, "mean"),
                    f"median_{prefix}": (value, "median"),
                    f"p25_{prefix}": (value, lambda s: s.quantile(0.25)),
                    f"p75_{prefix}": (value, lambda s: s.quantile(0.75)),
                },
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
            "year_range": [int(long_df["year"].min()), int(long_df["year"].max())],
            "git_sha": self._git_sha(),
        }
        self.config.metadata_json.parent.mkdir(parents=True, exist_ok=True)
        self.config.metadata_json.write_text(json.dumps(metadata, indent=2))

    @staticmethod
    def _git_sha() -> str:
        try:
            return (
                subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
                .strip()
            )
        except Exception:
            return "unknown"


def _build_config(dataset: str) -> RetentionBuildConfig:
    processed_dir = Path("data/processed/2023/canonical")
    out_dir = Path("out/canonical")

    if dataset == "counts":
        return RetentionBuildConfig(
            long_parquet=processed_dir / "ipeds_retention_full_time_long.parquet",
            latest_parquet=processed_dir
            / "ipeds_retention_full_time_latest_by_inst.parquet",
            summary_parquet=processed_dir
            / "ipeds_retention_full_time_summary_by_year.parquet",
            metadata_json=out_dir / "ipeds_retention" / "run_latest.json",
            value_column="retained_students_full_time",
            summary_prefix="retained_students",
        )
    if dataset == "pct":
        return RetentionBuildConfig(
            long_parquet=processed_dir / "ipeds_retention_rate_full_time_long.parquet",
            latest_parquet=processed_dir
            / "ipeds_retention_rate_full_time_latest_by_inst.parquet",
            summary_parquet=processed_dir
            / "ipeds_retention_rate_full_time_summary_by_year.parquet",
            metadata_json=out_dir / "ipeds_retention_rate" / "run_latest.json",
            value_column="retention_rate_full_time",
            summary_prefix="retention_rate",
        )
    raise ValueError(f"Unsupported dataset: {dataset}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build canonical outputs for retention datasets."
    )
    parser.add_argument(
        "--dataset",
        choices=["counts", "pct"],
        default="counts",
        help="Which retention dataset to process (counts or percentages).",
    )
    args = parser.parse_args()

    builder = RetentionOutputBuilder(_build_config(args.dataset))
    frames = builder.run(write_output=True)
    print(
        f"Built retention outputs for {args.dataset}:",
        f"long={len(frames['long'])}",
        f"latest={len(frames['latest'])}",
        f"summary={len(frames['summary'])}",
    )


if __name__ == "__main__":
    main()
