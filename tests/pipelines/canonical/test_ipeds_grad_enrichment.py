"""Tests for metadata enrichment phase."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_grad.enrich_metadata import (
    IPEDSMetadataEnricher,
    MetadataEnrichmentConfig,
)


def _write_long_table(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "unitid": [111100, 222200],
            "year": [2023, 2023],
            "instnm": ["Alpha College", "Beta University"],
            "control": pd.Series([None, None], dtype="string"),
            "level": pd.Series([None, None], dtype="string"),
            "state": pd.Series([None, None], dtype="string"),
            "sector": pd.Series([None, None], dtype="string"),
            "grad_rate_150": [55.0, 72.0],
            "source_flag": ["DRVGR", "DRVGR"],
            "is_revised": [False, False],
            "cohort_reference": ["2023 cohort, total", "2023 cohort, total"],
            "load_ts": pd.Timestamp("2024-01-01"),
        }
    )
    path = tmp_path / "long.parquet"
    df.to_parquet(path, index=False)
    return path


def _write_hd(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "STATE": ["CA", "NY"],
            "LEVEL": [1, 2],
            "CONTROL": [1, 2],
            "SECTOR": [1, 5],
        }
    )
    path = tmp_path / "hd.csv"
    df.to_csv(path, index=False)
    return path


def test_enrichment_populates_metadata(tmp_path):
    long_path = _write_long_table(tmp_path)
    hd_path = _write_hd(tmp_path)

    config = MetadataEnrichmentConfig(long_parquet=long_path, hd_csv=hd_path)
    enricher = IPEDSMetadataEnricher(config)

    result = enricher.run(write_output=False)

    assert set(result["control"].unique()) == {"Public", "Private NP"}
    assert set(result["level"].unique()) == {"4-year", "2-year"}
    assert set(result["sector"].unique()) == {
        "Public, 4-year or above",
        "Private nonprofit, 2-year",
    }


def test_enrichment_can_write_new_parquet(tmp_path):
    long_path = _write_long_table(tmp_path)
    hd_path = _write_hd(tmp_path)
    output_path = tmp_path / "enriched.parquet"

    config = MetadataEnrichmentConfig(
        long_parquet=long_path, hd_csv=hd_path, output_parquet=output_path
    )
    enricher = IPEDSMetadataEnricher(config)

    enricher.run(write_output=True)

    assert output_path.exists()
    saved = pd.read_parquet(output_path)
    assert "control" in saved.columns
