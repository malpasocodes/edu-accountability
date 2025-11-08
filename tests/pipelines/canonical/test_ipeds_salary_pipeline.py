"""Tests for the instructional staff salary canonical pipeline."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_salary.build_outputs import (
    IPEDSSalaryBuilder,
    SalaryBuildConfig,
)
from src.pipelines.canonical.ipeds_salary.extraction import (
    IPEDSSalaryExtractionConfig,
    IPEDSSalaryExtractor,
)


def _write_sample_wide(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "Institution Name": ["Alpha", "Beta"],
            "Average salary (DRVHR2023)": [90000, 80000],
            "Average salary (DRVHR2022_RV)": [85000, None],
        }
    )
    path = tmp_path / "salary.csv"
    df.to_csv(path, index=False)
    return path


def _write_hd(tmp_path: Path) -> Path:
    hd_df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "STATE": ["CA", "NY"],
            "LEVEL": [1, 2],
            "CONTROL": [1, 2],
            "SECTOR": [1, 5],
        }
    )
    path = tmp_path / "institutions.csv"
    hd_df.to_csv(path, index=False)
    return path


def test_extractor_creates_long_table(tmp_path):
    wide_csv = _write_sample_wide(tmp_path)
    hd_csv = _write_hd(tmp_path)
    output = tmp_path / "long.parquet"

    config = IPEDSSalaryExtractionConfig(
        wide_csv=wide_csv,
        hd_csv=hd_csv,
        output_path=output,
    )
    extractor = IPEDSSalaryExtractor(config)
    df = extractor.run(write_output=True)

    assert len(df) == 3
    assert set(df["year"].unique()) == {2022, 2023}
    assert "control" in df.columns
    assert output.exists()


def test_builder_outputs_latest_and_summary(tmp_path):
    long_path = tmp_path / "long.parquet"
    data = pd.DataFrame(
        {
            "unitid": [111100, 111100, 222200],
            "year": [2022, 2023, 2023],
            "instnm": ["Alpha", "Alpha", "Beta"],
            "control": ["Public", "Public", "Private NP"],
            "level": ["4-year", "4-year", "2-year"],
            "state": ["CA", "CA", "NY"],
            "sector": ["Public, 4-year or above", "Public, 4-year or above", "Private nonprofit, 2-year"],
            "avg_salary_9mo_all_ranks": [85000.0, 90000.0, 80000.0],
            "source_flag": ["DRVHR2022", "DRVHR2023", "DRVHR2023"],
            "is_revised": [True, False, False],
            "cohort_reference": ["2022 Salary", "2023 Salary", "2023 Salary"],
            "load_ts": [pd.Timestamp("2024-01-01")]*3,
        }
    )
    data.to_parquet(long_path, index=False)

    config = SalaryBuildConfig(
        long_parquet=long_path,
        latest_parquet=tmp_path / "latest.parquet",
        summary_parquet=tmp_path / "summary.parquet",
        metadata_json=tmp_path / "meta.json",
    )
    builder = IPEDSSalaryBuilder(config)
    frames = builder.run(write_output=True)

    assert len(frames["latest"]) == 2
    summary = frames["summary"]
    assert set(summary["year"].unique()) == {2022, 2023}
    assert config.latest_parquet.exists()
    assert config.summary_parquet.exists()
    assert config.metadata_json.exists()
