"""Tests for shared YoY trend classification utility."""

import pandas as pd
import pytest

from src.charts.trend_utils import YOY_PCT_THRESHOLD, classify_yoy_direction


class TestClassifyYoyDirection:
    def test_increase_above_threshold(self):
        s = pd.Series([1.0, 5.0, 100.0])
        result = classify_yoy_direction(s)
        assert list(result) == ["Increase", "Increase", "Increase"]

    def test_decrease_below_threshold(self):
        s = pd.Series([-1.0, -5.0, -100.0])
        result = classify_yoy_direction(s)
        assert list(result) == ["Decrease", "Decrease", "Decrease"]

    def test_same_within_threshold(self):
        s = pd.Series([0.0, 0.3, -0.3, 0.49, -0.49])
        result = classify_yoy_direction(s)
        assert all(v == "Same" for v in result)

    def test_boundary_values(self):
        s = pd.Series([YOY_PCT_THRESHOLD, -YOY_PCT_THRESHOLD])
        result = classify_yoy_direction(s)
        # +0.5 is the right edge of "Same" bin (exclusive upper) → "Same"
        # -0.5 is the left edge of "Decrease" bin → "Decrease"
        assert list(result) == ["Same", "Decrease"]

    def test_just_above_threshold(self):
        s = pd.Series([YOY_PCT_THRESHOLD + 0.01, -(YOY_PCT_THRESHOLD + 0.01)])
        result = classify_yoy_direction(s)
        assert list(result) == ["Increase", "Decrease"]

    def test_nan_classified_as_same(self):
        s = pd.Series([float("nan"), None])
        result = classify_yoy_direction(s)
        assert list(result) == ["Same", "Same"]

    def test_empty_series(self):
        s = pd.Series([], dtype=float)
        result = classify_yoy_direction(s)
        assert len(result) == 0

    def test_returns_string_dtype(self):
        s = pd.Series([1.0, 0.0, -1.0])
        result = classify_yoy_direction(s)
        assert result.dtype == object  # string dtype in pandas
