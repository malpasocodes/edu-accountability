"""Shared utilities for year-over-year trend classification."""

from __future__ import annotations

import re
from typing import Iterable, List

import pandas as pd

# Matches federal-aid year columns named like "YR2022" (case-insensitive).
YEAR_COLUMN_PATTERN = re.compile(r"^YR(\d{4})$", re.IGNORECASE)

# Percent-change threshold for classifying YoY direction.
# Changes within +/- this value are labeled "Same".
# 0.5% balances noise suppression with meaningful signal for both
# dollar-denominated (Pell/Loans in billions) and headcount (enrollment) series.
YOY_PCT_THRESHOLD = 0.5


def classify_yoy_direction(pct_change: pd.Series) -> pd.Series:
    """Classify year-over-year percent changes as Increase / Same / Decrease.

    Args:
        pct_change: Series of percent-change values (e.g. 5.2 means +5.2%).
            NaN values are classified as "Same".

    Returns:
        Categorical Series with values "Decrease", "Same", or "Increase".
    """
    return pd.cut(
        pct_change,
        bins=[-float("inf"), -YOY_PCT_THRESHOLD, YOY_PCT_THRESHOLD, float("inf")],
        labels=["Decrease", "Same", "Increase"],
        include_lowest=True,
    ).fillna("Same").astype(str)


def _identify_year_columns(columns: Iterable[str]) -> List[tuple[int, str]]:
    """Return (year, column_name) pairs for YR#### columns, sorted by year."""
    discovered: List[tuple[int, str]] = []
    for column in columns:
        normalized = column.strip()
        match = YEAR_COLUMN_PATTERN.match(normalized)
        if match:
            year = int(match.group(1))
            discovered.append((year, column))
    return sorted(discovered)


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    """Coerce UnitID values to nullable Int64, preserving exact values."""
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")
