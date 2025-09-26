"""Data access helpers for processed ACT datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

DATA_VERSION = "parquet_v1"
REQUIRED_COLUMNS: List[str] = [
    "UnitID",
    "institution",
    "sector",
    "state",
    "enrollment",
    "cost",
    "graduation_rate",
    "year",
]
_METRIC_COLUMNS = ("enrollment", "cost", "graduation_rate")
_CATEGORY_COLUMNS = ("sector", "state")
_STRING_COLUMNS = ("institution",)
_INTEGER_COLUMNS = ("UnitID", "enrollment", "year")
_FLOAT_COLUMNS = ("cost", "graduation_rate")


@dataclass(frozen=True)
class DatasetConfig:
    csv_path: Path
    parquet_path: Path


PROCESSED_DATASETS: Dict[str, DatasetConfig] = {
    "cost_vs_grad": DatasetConfig(
        csv_path=PROCESSED_DIR / "tuition_vs_graduation.csv",
        parquet_path=PROCESSED_DIR / "tuition_vs_graduation.parquet",
    ),
    "cost_vs_grad_two_year": DatasetConfig(
        csv_path=PROCESSED_DIR / "tuition_vs_graduation_two_year.csv",
        parquet_path=PROCESSED_DIR / "tuition_vs_graduation_two_year.parquet",
    ),
}


def _coerce_integer(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.round().astype("Int32")


def _coerce_float(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.astype("float32")


def _coerce_string(series: pd.Series) -> pd.Series:
    stringified = series.astype("string")
    return stringified.str.strip()


def _apply_schema(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    for column in _STRING_COLUMNS:
        if column in working.columns:
            working[column] = _coerce_string(working[column])

    for column in _INTEGER_COLUMNS:
        if column in working.columns:
            working[column] = _coerce_integer(working[column])

    for column in _FLOAT_COLUMNS:
        if column in working.columns:
            working[column] = _coerce_float(working[column])

    for column in _CATEGORY_COLUMNS:
        if column in working.columns:
            working[column] = _coerce_string(working[column]).astype("category")

    return working


def _validate_parquet(baseline: pd.DataFrame, parquet_path: Path) -> None:
    loaded = pd.read_parquet(parquet_path)

    if baseline.shape[0] != loaded.shape[0]:
        raise ValueError(
            f"Row count mismatch for {parquet_path.name}: "
            f"csv={baseline.shape[0]} parquet={loaded.shape[0]}"
        )

    for column in baseline.columns:
        if column not in loaded.columns:
            raise ValueError(f"Missing column '{column}' after Parquet conversion.")

        base_non_null = int(baseline[column].notna().sum())
        loaded_non_null = int(loaded[column].notna().sum())
        if base_non_null != loaded_non_null:
            raise ValueError(
                f"Non-null count mismatch for column '{column}' in {parquet_path.name}."
            )

    for column in _METRIC_COLUMNS:
        if column in baseline.columns and column in loaded.columns:
            base_stats = (
                baseline[column]
                .astype("float64")
                .agg(["min", "max", "mean"])
                .to_numpy(dtype="float64")
            )
            loaded_stats = (
                loaded[column]
                .astype("float64")
                .agg(["min", "max", "mean"])
                .to_numpy(dtype="float64")
            )
            if not np.allclose(base_stats, loaded_stats, equal_nan=True, rtol=1e-5, atol=1e-8):
                raise ValueError(
                    f"Statistic mismatch for column '{column}' in {parquet_path.name}."
                )

    for column in _CATEGORY_COLUMNS:
        if column in baseline.columns and column in loaded.columns:
            base_values = set(baseline[column].dropna().astype(str))
            loaded_values = set(loaded[column].dropna().astype(str))
            if base_values != loaded_values:
                raise ValueError(
                    f"Categorical values mismatch for column '{column}' in {parquet_path.name}."
                )


def build_parquet_dataset(name: str, *, force: bool = False) -> Path:
    """Create or refresh the Parquet version of a processed dataset."""

    if name not in PROCESSED_DATASETS:
        raise KeyError(f"Unknown dataset '{name}'.")

    config = PROCESSED_DATASETS[name]
    csv_path = config.csv_path
    parquet_path = config.parquet_path

    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV source for '{name}': {csv_path}")

    if parquet_path.exists() and not force:
        parquet_mtime = parquet_path.stat().st_mtime
        if parquet_mtime >= csv_path.stat().st_mtime:
            return parquet_path

    raw = pd.read_csv(csv_path)
    normalized = _apply_schema(raw)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_parquet(parquet_path, compression="snappy", index=False)
    _validate_parquet(normalized, parquet_path)
    return parquet_path


def _ensure_parquet(name: str) -> Path:
    config = PROCESSED_DATASETS[name]
    parquet_path = config.parquet_path
    csv_path = config.csv_path

    if parquet_path.exists():
        if csv_path.exists():
            if parquet_path.stat().st_mtime >= csv_path.stat().st_mtime:
                return parquet_path
        else:
            return parquet_path

    return build_parquet_dataset(name)


@st.cache_data(show_spinner=False)
def _load_parquet(path: str, mtime: float, data_version: str) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    available = [column for column in REQUIRED_COLUMNS if column in frame.columns]
    if available:
        frame = frame.loc[:, available].copy()
    return frame


def load_processed(name: str) -> pd.DataFrame:
    """Load a named processed dataset, preferring Parquet with CSV fallback."""

    if name not in PROCESSED_DATASETS:
        raise KeyError(f"Unknown dataset '{name}'.")

    parquet_path = _ensure_parquet(name)
    return _load_parquet(
        str(parquet_path),
        parquet_path.stat().st_mtime,
        DATA_VERSION,
    )


def load_all_parquet() -> Iterable[Path]:
    """Return the current Parquet paths, creating them if needed."""

    for name in PROCESSED_DATASETS:
        yield _ensure_parquet(name)


if __name__ == "__main__":
    for dataset_name in PROCESSED_DATASETS:
        path = build_parquet_dataset(dataset_name, force=True)
        print(f"Built {path}")
