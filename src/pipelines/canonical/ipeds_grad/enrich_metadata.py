"""Phase 03 metadata enrichment for IPEDS graduation rates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd


CONTROL_MAP: Dict[int, str] = {1: "Public", 2: "Private NP", 3: "Private FP"}
LEVEL_MAP: Dict[int, str] = {1: "4-year", 2: "2-year", 3: "<2-year"}
SECTOR_MAP: Dict[int, str] = {
    1: "Public, 4-year or above",
    2: "Private nonprofit, 4-year or above",
    3: "Private for-profit, 4-year or above",
    4: "Public, 2-year",
    5: "Private nonprofit, 2-year",
    6: "Private for-profit, 2-year",
    7: "Public, less-than 2-year",
    8: "Private nonprofit, less-than 2-year",
    9: "Private for-profit, less-than 2-year",
}


@dataclass
class MetadataEnrichmentConfig:
    """Configuration for metadata enrichment."""

    long_parquet: Path
    hd_csv: Path
    output_parquet: Path | None = None


class IPEDSMetadataEnricher:
    """Joins institutional metadata onto the canonical long table."""

    def __init__(self, config: MetadataEnrichmentConfig):
        self.config = config

    def run(self, *, write_output: bool = True) -> pd.DataFrame:
        long_df = self._load_long()
        base_df = long_df.drop(columns=["control", "level", "state", "sector"], errors="ignore")
        hd_df = self._load_hd()

        enriched = base_df.merge(
            hd_df, on="unitid", how="left", validate="many_to_one"
        )

        column_order = [
            "unitid",
            "year",
            "instnm",
            "control",
            "level",
            "state",
            "sector",
        ]
        remaining_cols = [c for c in enriched.columns if c not in column_order]
        enriched = enriched[column_order + remaining_cols]

        missing = enriched["control"].isna().sum()
        if missing:
            print(f"Warning: {missing} rows missing HD metadata.")

        if write_output:
            output_path = self.config.output_parquet or self.config.long_parquet
            output_path.parent.mkdir(parents=True, exist_ok=True)
            enriched.to_parquet(output_path, index=False)

        return enriched

    def _load_long(self) -> pd.DataFrame:
        if not self.config.long_parquet.exists():
            raise FileNotFoundError(self.config.long_parquet)
        df = pd.read_parquet(self.config.long_parquet)
        if "unitid" not in df.columns:
            raise ValueError("Canonical long table missing 'unitid'.")
        return df

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
    config = MetadataEnrichmentConfig(
        long_parquet=Path("data/processed/2023/canonical/ipeds_grad_rates_long.parquet"),
        hd_csv=Path("data/raw/ipeds/2023/institutions.csv"),
    )

    enricher = IPEDSMetadataEnricher(config)
    enriched = enricher.run(write_output=True)
    print(f"Enriched rows: {len(enriched)}")


if __name__ == "__main__":
    main()
