"""Tests for SFAPercentExtractor."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_sfa.extraction import (
    SFAPercentExtractionConfig,
    SFAPercentExtractor,
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
