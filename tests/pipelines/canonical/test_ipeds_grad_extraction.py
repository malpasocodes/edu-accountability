"""Tests for IPEDS graduation-rate extraction."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_grad.extraction import (
    IPEDSGradExtractionConfig,
    IPEDSGradExtractor,
)


def _write_sample_csv(tmp_path: Path) -> Path:
    data = {
        "UnitID": [111100, 222200],
        "Institution Name": ["Alpha College", "Beta University"],
        "Graduation rate  total cohort (DRVGR2023)": [55, 72],
        "Graduation rate  total cohort (DFR2022_RV)": [50, None],
    }
    df = pd.DataFrame(data)
    csv_path = tmp_path / "sample_grad_rates.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def test_wide_to_long_parses_columns(tmp_path):
    csv_path = _write_sample_csv(tmp_path)
    config = IPEDSGradExtractionConfig(wide_csv=csv_path)
    extractor = IPEDSGradExtractor(config)

    result = extractor.run(write_output=False)

    assert len(result) == 3  # one null value is dropped
    assert set(result["year"].unique()) == {2022, 2023}
    assert set(result["source_flag"].unique()) == {"DRVGR", "DFR"}
    assert result.loc[result["year"] == 2022, "is_revised"].all()
    assert result.loc[result["year"] == 2023, "is_revised"].eq(False).all()
    assert result.loc[result["year"] == 2023, "grad_rate_150"].dtype == "float32"
    assert result["cohort_reference"].str.contains("cohort").all()


def test_write_output_creates_parquet(tmp_path):
    csv_path = _write_sample_csv(tmp_path)
    output_path = tmp_path / "ipeds_grad_rates_long.parquet"
    config = IPEDSGradExtractionConfig(wide_csv=csv_path, output_path=output_path)
    extractor = IPEDSGradExtractor(config)

    extractor.run(write_output=True)

    assert output_path.exists()
    written = pd.read_parquet(output_path)
    assert "grad_rate_150" in written.columns
