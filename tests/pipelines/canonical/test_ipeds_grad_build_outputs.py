"""Tests for Phase 05 canonical outputs."""

from pathlib import Path

import pandas as pd

from src.pipelines.canonical.ipeds_grad.build_outputs import (
    IPEDSGradOutputBuilder,
    OutputBuildConfig,
)


def _write_long(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "unitid": [1, 1, 2, 2, 3],
            "year": [2021, 2022, 2021, 2023, 2023],
            "instnm": ["A", "A", "B", "B", "C"],
            "control": ["Public"] * 5,
            "level": ["4-year"] * 5,
            "state": ["CA", "CA", "NY", "NY", "WA"],
            "sector": ["Public, 4-year or above"] * 5,
            "grad_rate_150": [50.0, 60.0, 65.0, 70.0, 80.0],
            "source_flag": ["DRVGR"] * 5,
            "is_revised": [False] * 5,
            "cohort_reference": ["2021", "2022", "2021", "2023", "2023"],
            "load_ts": pd.Timestamp("2024-01-01"),
        }
    )
    path = tmp_path / "long.parquet"
    df.to_parquet(path, index=False)
    return path


def test_latest_by_institution(tmp_path):
    long_path = _write_long(tmp_path)
    config = OutputBuildConfig(
        long_parquet=long_path,
        latest_parquet=tmp_path / "latest.parquet",
        summary_parquet=tmp_path / "summary.parquet",
        metadata_json=tmp_path / "run.json",
    )
    builder = IPEDSGradOutputBuilder(config)

    frames = builder.run(write_output=True)

    latest = frames["latest"]
    assert len(latest) == 3
    assert latest.loc[latest["unitid"] == 1, "year"].item() == 2022
    assert latest.loc[latest["unitid"] == 2, "year"].item() == 2023
    assert config.latest_parquet.exists()
    assert config.summary_parquet.exists()
    assert config.metadata_json.exists()


def test_summary_contains_group_stats(tmp_path):
    long_path = _write_long(tmp_path)
    config = OutputBuildConfig(
        long_parquet=long_path,
        latest_parquet=tmp_path / "latest.parquet",
        summary_parquet=tmp_path / "summary.parquet",
        metadata_json=tmp_path / "run.json",
    )
    builder = IPEDSGradOutputBuilder(config)
    frames = builder.run(write_output=False)

    summary = frames["summary"]
    assert {"year", "sector", "institution_count", "avg_grad_rate"}.issubset(
        summary.columns
    )
    row = summary[(summary["year"] == 2023) & (summary["sector"] == "Public, 4-year or above")]
    assert not row.empty
    assert row["institution_count"].item() == 2
    assert round(row["avg_grad_rate"].item(), 1) == 75.0
