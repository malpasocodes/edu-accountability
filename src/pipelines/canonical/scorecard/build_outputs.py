"""Build outputs for canonical College Scorecard metrics.

Creates latest-per-institution and year/level/control summaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json

import pandas as pd


@dataclass
class ScorecardBuildConfig:
    long_parquet: Path
    latest_parquet: Path
    summary_parquet: Path
    metadata_json: Path


class ScorecardBuilder:
    def __init__(self, config: ScorecardBuildConfig):
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
        ordered = df.sort_values(["unitid", "year"])  # ascending
        latest = ordered.drop_duplicates(subset=["unitid"], keep="last")
        return latest.reset_index(drop=True)

    def _summary_by_year(self, df: pd.DataFrame) -> pd.DataFrame:
        working = df.copy()
        # Aggregations: median debt (median), repayment shares (mean)
        repay_cols = [c for c in df.columns if c.startswith("repay_3yr_")]
        agg = {
            "median_debt_completers": "median",
        }
        agg.update({c: "mean" for c in repay_cols})

        summary = (
            working.groupby(["year", "level", "control"], dropna=False)
            .agg(agg)
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
            "year_range": [
                int(long_df["year"].min()) if not long_df.empty else None,
                int(long_df["year"].max()) if not long_df.empty else None,
            ],
            "repayment_horizon": "3-year",
        }

        self.config.metadata_json.parent.mkdir(parents=True, exist_ok=True)
        self.config.metadata_json.write_text(json.dumps(metadata, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build canonical Scorecard outputs.")
    parser.add_argument(
        "--long-parquet",
        type=Path,
        default=Path("data/processed/2023/canonical/scorecard_debt_repayment_long.parquet"),
    )
    parser.add_argument(
        "--latest-parquet",
        type=Path,
        default=Path("data/processed/2023/canonical/scorecard_debt_repayment_latest_by_inst.parquet"),
    )
    parser.add_argument(
        "--summary-parquet",
        type=Path,
        default=Path("data/processed/2023/canonical/scorecard_debt_repayment_summary_by_year.parquet"),
    )
    parser.add_argument(
        "--metadata-json",
        type=Path,
        default=Path("out/canonical/scorecard_debt_repayment/run_latest.json"),
    )
    args = parser.parse_args()

    cfg = ScorecardBuildConfig(
        long_parquet=args.long_parquet,
        latest_parquet=args.latest_parquet,
        summary_parquet=args.summary_parquet,
        metadata_json=args.metadata_json,
    )
    builder = ScorecardBuilder(cfg)
    frames = builder.run(write_output=True)
    print(
        "Built Scorecard outputs:",
        f"long={len(frames['long'])}",
        f"latest={len(frames['latest'])}",
        f"summary={len(frames['summary'])}",
    )


if __name__ == "__main__":
    main()

