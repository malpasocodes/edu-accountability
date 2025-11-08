"""Metadata enrichment for IPEDS SFA pipelines (percent Pell/loans)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse

import pandas as pd

from src.pipelines.canonical.ipeds_grad.enrich_metadata import (
    CONTROL_MAP,
    LEVEL_MAP,
    SECTOR_MAP,
)


@dataclass
class SFAMetadataConfig:
    long_parquet: Path
    hd_csv: Path
    output_parquet: Path | None = None


class SFAMetadataEnricher:
    """Applies HD metadata to SFA canonical datasets."""

    def __init__(self, config: SFAMetadataConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        base_df = self._load_long().drop(columns=["control", "level", "state", "sector"], errors="ignore")
        hd_df = self._load_hd()

        enriched = base_df.merge(hd_df, on="unitid", how="left", validate="many_to_one")

        columns = [
            "unitid",
            "year",
            "instnm",
            "control",
            "level",
            "state",
            "sector",
        ]
        remaining = [c for c in enriched.columns if c not in columns]
        enriched = enriched[columns + remaining]

        if write_output:
            output_path = self.config.output_parquet or self.config.long_parquet
            output_path.parent.mkdir(parents=True, exist_ok=True)
            enriched.to_parquet(output_path, index=False)

        return enriched

    def _load_long(self) -> pd.DataFrame:
        if not self.config.long_parquet.exists():
            raise FileNotFoundError(self.config.long_parquet)
        return pd.read_parquet(self.config.long_parquet)

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich SFA canonical datasets with HD metadata.")
    parser.add_argument(
        "--dataset",
        choices=["pell", "loans"],
        default="pell",
    )
    args = parser.parse_args()

    mapping = {
        "pell": SFAMetadataConfig(
            long_parquet=Path("data/processed/2023/canonical/ipeds_percent_pell_long.parquet"),
            hd_csv=Path("data/raw/ipeds/2023/institutions.csv"),
        ),
        "loans": SFAMetadataConfig(
            long_parquet=Path("data/processed/2023/canonical/ipeds_percent_loans_long.parquet"),
            hd_csv=Path("data/raw/ipeds/2023/institutions.csv"),
        ),
    }
    config = mapping[args.dataset]
    enricher = SFAMetadataEnricher(config)
    df = enricher.run(write_output=True)
    print(f"Enriched {len(df)} rows for dataset {args.dataset}")


if __name__ == "__main__":
    main()
