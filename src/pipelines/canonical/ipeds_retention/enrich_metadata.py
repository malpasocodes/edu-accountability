"""Metadata enrichment wrapper for retention cohorts."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipelines.canonical.ipeds_grad.enrich_metadata import (
    IPEDSMetadataEnricher,
    MetadataEnrichmentConfig,
)


def _build_config(dataset: str) -> MetadataEnrichmentConfig:
    processed_dir = Path("data/processed/2023/canonical")
    file_map = {
        "counts": processed_dir / "ipeds_retention_full_time_long.parquet",
        "pct": processed_dir / "ipeds_retention_rate_full_time_long.parquet",
    }
    try:
        long_path = file_map[dataset]
    except KeyError as exc:
        raise ValueError(f"Unsupported dataset: {dataset}") from exc

    return MetadataEnrichmentConfig(
        long_parquet=long_path,
        hd_csv=Path("data/raw/ipeds/2023/institutions.csv"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich retention canonical datasets with HD metadata."
    )
    parser.add_argument(
        "--dataset",
        choices=["counts", "pct"],
        default="counts",
        help="Which retention dataset to enrich.",
    )
    args = parser.parse_args()

    config = _build_config(args.dataset)
    enricher = IPEDSMetadataEnricher(config)
    enriched = enricher.run(write_output=True)
    print(
        f"Enriched {len(enriched)} retention rows with metadata for dataset {args.dataset}."
    )


if __name__ == "__main__":
    main()
