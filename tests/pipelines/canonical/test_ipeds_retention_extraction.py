"""Tests for the IPEDS retention extraction and outputs."""

from pathlib import Path

import pandas as pd
import pytest

from src.pipelines.canonical.ipeds_retention.extraction import (
    FULL_TIME_PATTERN,
    FULL_TIME_RATE_PATTERN,
    IPEDSRetentionExtractionConfig,
    IPEDSRetentionExtractor,
)
from src.pipelines.canonical.ipeds_retention.build_outputs import (
    RetentionBuildConfig,
    RetentionOutputBuilder,
)


def _write_sample_counts(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "Institution Name": ["Alpha", "Beta"],
            "Full-time fall 2022 cohort (EF2023D)": [500, 250],
            "Full-time fall 2021 cohort (EF2022D_RV)": [480, None],
        }
    )
    csv = tmp_path / "retention_counts.csv"
    df.to_csv(csv, index=False)
    return csv


def _write_sample_pct(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "UnitID": [111100, 222200],
            "Institution Name": ["Alpha", "Beta"],
            "Full-time retention rate  2022 (EF2022D_RV)": [78.5, 65.2],
            "Full-time retention rate (EF2021D_RV)": [77.0, None],
        }
    )
    csv = tmp_path / "retention_pct.csv"
    df.to_csv(csv, index=False)
    return csv


def test_retention_counts_extractor_builds_long(tmp_path):
    csv = _write_sample_counts(tmp_path)
    output = tmp_path / "retention_long.parquet"
    config = IPEDSRetentionExtractionConfig(
        wide_csv=csv,
        value_column="retained_students_full_time",
        column_pattern=FULL_TIME_PATTERN,
        cohort_label_template="Full-time fall {year} cohort ({source_flag})",
        output_path=output,
        round_values=True,
        value_dtype="Int64",
        year_offset_from_source=1,
    )
    extractor = IPEDSRetentionExtractor(config)

    df = extractor.run(write_output=True)

    assert len(df) == 3  # drops single null entry
    assert set(df["year"].unique()) == {2021, 2022}
    assert df.loc[df["year"] == 2022, "retained_students_full_time"].tolist() == [
        500,
        250,
    ]
    assert output.exists()


def test_retention_pct_extractor_handles_missing_year(tmp_path):
    csv = _write_sample_pct(tmp_path)
    config = IPEDSRetentionExtractionConfig(
        wide_csv=csv,
        value_column="retention_rate_full_time",
        column_pattern=FULL_TIME_RATE_PATTERN,
        cohort_label_template="Full-time retention rate {year} ({source_flag})",
        value_dtype="float32",
        year_offset_from_source=0,
    )
    extractor = IPEDSRetentionExtractor(config)

    df = extractor.run(write_output=False)

    assert set(df["year"].unique()) == {2021, 2022}
    assert df.loc[df["year"] == 2022, "retention_rate_full_time"].tolist() == pytest.approx(
        [78.5, 65.2]
    )
    # Column missing explicit year should derive from source flag
    assert df.loc[df["year"] == 2021, "retention_rate_full_time"].tolist() == [77.0]


def test_retention_builder_outputs(tmp_path):
    long_path = tmp_path / "retention_long.parquet"
    long_df = pd.DataFrame(
        {
            "unitid": [111100, 111100, 222200],
            "year": [2021, 2022, 2022],
            "instnm": ["Alpha", "Alpha", "Beta"],
            "control": ["Public", "Public", "Private"],
            "level": ["4-year", "4-year", "4-year"],
            "state": ["CA", "CA", "NY"],
            "sector": ["Public, 4-year or above"] * 3,
            "retained_students_full_time": [480, 500, 250],
            "source_flag": ["EF2022D", "EF2023D", "EF2023D"],
            "is_revised": [True, False, False],
            "cohort_reference": ["Full-time fall 2021 cohort (EF2022D_RV)"] * 2
            + ["Full-time fall 2022 cohort (EF2023D)"],
            "load_ts": [pd.Timestamp("2025-01-01")] * 3,
        }
    )
    long_df.to_parquet(long_path, index=False)

    latest_path = tmp_path / "latest.parquet"
    summary_path = tmp_path / "summary.parquet"
    metadata_path = tmp_path / "run.json"

    builder = RetentionOutputBuilder(
        RetentionBuildConfig(
            long_parquet=long_path,
            latest_parquet=latest_path,
            summary_parquet=summary_path,
            metadata_json=metadata_path,
            value_column="retained_students_full_time",
            summary_prefix="retained_students",
        )
    )

    outputs = builder.run(write_output=True)

    assert latest_path.exists()
    assert summary_path.exists()
    assert metadata_path.exists()
    assert len(outputs["latest"]) == 2
    summary = outputs["summary"]
    assert set(summary["year"].unique()) == {2021, 2022}
    assert "avg_retained_students" in summary.columns
    assert (summary["institution_count"] > 0).all()


def test_retention_pct_builder_names_columns(tmp_path):
    long_path = tmp_path / "retention_pct_long.parquet"
    long_df = pd.DataFrame(
        {
            "unitid": [111100, 111100],
            "year": [2021, 2022],
            "instnm": ["Alpha", "Alpha"],
            "control": ["Public", "Public"],
            "level": ["4-year", "4-year"],
            "state": ["CA", "CA"],
            "sector": ["Public, 4-year or above", "Public, 4-year or above"],
            "retention_rate_full_time": [78.5, 80.0],
            "source_flag": ["EF2022D", "EF2023D"],
            "is_revised": [True, False],
            "cohort_reference": [
                "Full-time retention rate 2021 (EF2022D_RV)",
                "Full-time retention rate 2022 (EF2023D)",
            ],
            "load_ts": [pd.Timestamp("2025-01-01")] * 2,
        }
    )
    long_df.to_parquet(long_path, index=False)

    latest_path = tmp_path / "pct_latest.parquet"
    summary_path = tmp_path / "pct_summary.parquet"
    metadata_path = tmp_path / "pct_run.json"

    builder = RetentionOutputBuilder(
        RetentionBuildConfig(
            long_parquet=long_path,
            latest_parquet=latest_path,
            summary_parquet=summary_path,
            metadata_json=metadata_path,
            value_column="retention_rate_full_time",
            summary_prefix="retention_rate",
        )
    )

    summary = builder.run(write_output=True)["summary"]
    assert "avg_retention_rate" in summary.columns
    assert "median_retention_rate" in summary.columns
