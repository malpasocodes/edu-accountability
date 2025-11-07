"""Phase 05: build canonical IPEDS graduation-rate outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Any, Dict

import pandas as pd


@dataclass
class OutputBuildConfig:
    long_parquet: Path
    latest_parquet: Path
    summary_parquet: Path
    metadata_json: Path


class IPEDSGradOutputBuilder:
    """Generates canonical outputs and provenance metadata."""

    def __init__(self, config: OutputBuildConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> Dict[str, pd.DataFrame]:
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

    @staticmethod
    def _latest_by_institution(df: pd.DataFrame) -> pd.DataFrame:
        ordered = df.sort_values(["unitid", "year"])
        latest = ordered.drop_duplicates(subset=["unitid"], keep="last")
        return latest.reset_index(drop=True)

    @staticmethod
    def _summary_by_year(df: pd.DataFrame) -> pd.DataFrame:
        working = df.copy()
        working["sector"] = working["sector"].fillna("Unknown")
        summary = (
            working.groupby(["year", "sector"], dropna=False)
            .agg(
                institution_count=("unitid", "nunique"),
                avg_grad_rate=("grad_rate_150", "mean"),
                median_grad_rate=("grad_rate_150", "median"),
                p25_grad_rate=("grad_rate_150", lambda s: s.quantile(0.25)),
                p75_grad_rate=("grad_rate_150", lambda s: s.quantile(0.75)),
            )
            .reset_index()
        )
        return summary

    def _write_outputs(self, latest: pd.DataFrame, summary: pd.DataFrame) -> None:
        latest_path = self.config.latest_parquet
        summary_path = self.config.summary_parquet
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        latest.to_parquet(latest_path, index=False)
        summary.to_parquet(summary_path, index=False)

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


def main() -> None:
    config = OutputBuildConfig(
        long_parquet=Path("data/processed/2023/canonical/ipeds_grad_rates_long.parquet"),
        latest_parquet=Path(
            "data/processed/2023/canonical/ipeds_grad_rates_latest_by_inst.parquet"
        ),
        summary_parquet=Path(
            "data/processed/2023/canonical/ipeds_grad_rates_summary_by_year.parquet"
        ),
        metadata_json=Path("out/canonical/ipeds_grad/run_latest.json"),
    )

    builder = IPEDSGradOutputBuilder(config)
    frames = builder.run(write_output=True)
    print(
        "Built outputs:",
        f"long={len(frames['long'])}",
        f"latest={len(frames['latest'])}",
        f"summary={len(frames['summary'])}",
    )


if __name__ == "__main__":
    main()
