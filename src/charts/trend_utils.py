"""Shared utilities for year-over-year trend classification."""

from __future__ import annotations

import pandas as pd

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
