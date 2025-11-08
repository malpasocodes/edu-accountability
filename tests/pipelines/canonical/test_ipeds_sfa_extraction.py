"""Tests for SFAPercentExtractor."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_sfa.extraction import (
    SFAPercentExtractionConfig,
    SFAPercentExtractor,
)
from src.pipelines.canonical.ipeds_sfa.enrich_metadata import (
    SFAMetadataConfig,
    SFAMetadataEnricher,
)


def _write_sample(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "Institution Name": ["Alpha", "Beta"],
            "Percent Pell (SFA2223)": [55, 60],
            "Percent Pell (SFA2122_RV)": [50, None],
        }
    )
    path = tmp_path / "pell.csv"
    df.to_csv(path, index=False)
    return path


def test_extractor_builds_long_table(tmp_path):
    csv = _write_sample(tmp_path)
    output = tmp_path / "pell_long.parquet"
    config = SFAPercentExtractionConfig(
        wide_csv=csv,
        value_column="percent_pell",
        output_path=output,
        metric_label="Pell",
    )

    extractor = SFAPercentExtractor(config)
    df = extractor.run(write_output=True)

    assert len(df) == 3  # drops one null
    assert set(df["year"].unique()) == {2022, 2023}
    assert df.loc[df["year"] == 2023, "percent_pell"].tolist() == [55.0, 60.0]
    assert output.exists()


def test_extractor_sets_metadata(tmp_path):
    csv = _write_sample(tmp_path)
    config = SFAPercentExtractionConfig(
        wide_csv=csv,
        value_column="percent_pell",
        metric_label="Pell",
    )
    extractor = SFAPercentExtractor(config)
    df = extractor.run(write_output=False)

    sample = df.iloc[0]
    assert sample["source_flag"] == "SFA"
    assert sample["cohort_reference"].endswith("Pell")
    assert "control" in df.columns


def test_metadata_enrichment(tmp_path):
    long_path = tmp_path / "long.parquet"
    data = pd.DataFrame(
        {
            "unitid": [111100],
            "year": [2023],
            "instnm": ["Alpha"],
            "control": [pd.NA],
            "level": [pd.NA],
            "state": [pd.NA],
            "sector": [pd.NA],
            "percent_pell": [55.0],
            "source_flag": ["SFA"],
            "is_revised": [False],
            "cohort_reference": ["2022-23 Pell"],
            "load_ts": [pd.Timestamp("2025-01-01")],
        }
    )
    data.to_parquet(long_path, index=False)

    hd_path = tmp_path / "hd.csv"
    hd_df = pd.DataFrame(
        {
            "UnitID": [111100],
            "STATE": ["CA"],
            "LEVEL": [1],
            "CONTROL": [1],
            "SECTOR": [1],
        }
    )
    hd_df.to_csv(hd_path, index=False)

    config = SFAMetadataConfig(long_parquet=long_path, hd_csv=hd_path)
    enricher = SFAMetadataEnricher(config)
    enriched = enricher.run(write_output=False)

    row = enriched.iloc[0]
    assert row["control"] == "Public"
    assert row["state"] == "CA"
