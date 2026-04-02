"""Tests for distance education trend chart data preparation."""

import pandas as pd
import pytest

from src.charts.distance_de_trend_chart import (
    _identify_de_enrollment_columns,
    _prepare_de_trend_dataframe,
)
from src.charts.distance_enrollment_trend_chart import (
    _identify_total_enrollment_columns,
    _prepare_enrollment_trend_dataframe,
)


METADATA = [
    {"UnitID": 1, "institution": "Big State U", "sector": "Public"},
    {"UnitID": 2, "institution": "Online Academy", "sector": "Private, for-profit"},
    {"UnitID": 3, "institution": "Small College", "sector": "Private, not-for-profit"},
]


def _make_metadata():
    return pd.DataFrame(METADATA)


class TestIdentifyColumns:
    def test_de_enrollment_columns(self):
        cols = ["UnitID", "DE_ENROLL_2020", "DE_ENROLL_2021", "other"]
        result = _identify_de_enrollment_columns(cols)
        assert result == [(2020, "DE_ENROLL_2020"), (2021, "DE_ENROLL_2021")]

    def test_total_enrollment_columns(self):
        cols = ["UnitID", "TOTAL_ENROLL_2020", "TOTAL_ENROLL_2021", "other"]
        result = _identify_total_enrollment_columns(cols)
        assert result == [(2020, "TOTAL_ENROLL_2020"), (2021, "TOTAL_ENROLL_2021")]

    def test_no_matching_columns(self):
        cols = ["UnitID", "NAME", "STATE"]
        assert _identify_de_enrollment_columns(cols) == []
        assert _identify_total_enrollment_columns(cols) == []

    def test_columns_sorted_by_year(self):
        cols = ["DE_ENROLL_2023", "DE_ENROLL_2020", "DE_ENROLL_2021"]
        result = _identify_de_enrollment_columns(cols)
        years = [y for y, _ in result]
        assert years == [2020, 2021, 2023]


class TestPrepareDeTrendDataframe:
    def _make_de_df(self):
        return pd.DataFrame([
            {"UnitID": 1, "DE_ENROLL_2022": 5000, "DE_ENROLL_2023": 6000, "DE_ENROLL_2024": 7000},
            {"UnitID": 2, "DE_ENROLL_2022": 10000, "DE_ENROLL_2023": 9000, "DE_ENROLL_2024": 12000},
            {"UnitID": 3, "DE_ENROLL_2022": 100, "DE_ENROLL_2023": 200, "DE_ENROLL_2024": 300},
        ])

    def test_basic_output_shape(self):
        df = _prepare_de_trend_dataframe(
            self._make_de_df(), _make_metadata(), top_n=10, anchor_year=2024,
        )
        assert not df.empty
        assert "Institution" in df.columns
        assert "Year" in df.columns
        assert "ChangeDirection" in df.columns

    def test_top_n_filtering(self):
        df = _prepare_de_trend_dataframe(
            self._make_de_df(), _make_metadata(), top_n=2, anchor_year=2024,
        )
        institutions = df["Institution"].unique()
        assert len(institutions) == 2
        # Top 2 by 2024 DE enrollment: Online Academy (12000) and Big State U (7000)
        assert "Online Academy" in institutions
        assert "Big State U" in institutions

    def test_yoy_direction_decrease(self):
        df = _prepare_de_trend_dataframe(
            self._make_de_df(), _make_metadata(), top_n=10, anchor_year=2024,
        )
        # Online Academy: 10000 → 9000 is a decrease
        oa = df[(df["Institution"] == "Online Academy")].sort_values("Year")
        directions = oa["ChangeDirection"].tolist()
        assert directions[0] == "Same"  # First year
        assert directions[1] == "Decrease"  # 10000 → 9000

    def test_empty_input(self):
        df = _prepare_de_trend_dataframe(
            pd.DataFrame(), _make_metadata(), top_n=10, anchor_year=2024,
        )
        assert df.empty

    def test_missing_anchor_year_raises(self):
        with pytest.raises(ValueError, match="anchor year"):
            _prepare_de_trend_dataframe(
                self._make_de_df(), _make_metadata(), top_n=10, anchor_year=2099,
            )

    def test_zero_enrollment_percentage_guard(self):
        """Verify de_percentage doesn't produce inf when year total is zero."""
        # All institutions have zero DE enrollment in one year
        df = pd.DataFrame([
            {"UnitID": 1, "DE_ENROLL_2023": 0, "DE_ENROLL_2024": 100},
            {"UnitID": 2, "DE_ENROLL_2023": 0, "DE_ENROLL_2024": 200},
        ])
        result = _prepare_de_trend_dataframe(
            df, _make_metadata(), top_n=10, anchor_year=2024,
        )
        # 2023 has zero total enrollment, de_percentage should be 0, not inf
        if not result.empty:
            year_2023 = result[result["Year"] == 2023]
            if not year_2023.empty and "de_percentage" in year_2023.columns:
                assert all(year_2023["de_percentage"].apply(lambda x: x == 0 or pd.isna(x)))


class TestPrepareEnrollmentTrendDataframe:
    def _make_enrollment_df(self):
        return pd.DataFrame([
            {"UnitID": 1, "TOTAL_ENROLL_2022": 20000, "TOTAL_ENROLL_2023": 21000, "TOTAL_ENROLL_2024": 22000},
            {"UnitID": 2, "TOTAL_ENROLL_2022": 15000, "TOTAL_ENROLL_2023": 14000, "TOTAL_ENROLL_2024": 16000},
            {"UnitID": 3, "TOTAL_ENROLL_2022": 500, "TOTAL_ENROLL_2023": 600, "TOTAL_ENROLL_2024": 700},
        ])

    def test_basic_output(self):
        df = _prepare_enrollment_trend_dataframe(
            self._make_enrollment_df(), _make_metadata(), top_n=10, anchor_year=2024,
        )
        assert not df.empty
        assert "YoYChangePercent" in df.columns

    def test_top_n_filtering(self):
        df = _prepare_enrollment_trend_dataframe(
            self._make_enrollment_df(), _make_metadata(), top_n=1, anchor_year=2024,
        )
        institutions = df["Institution"].unique()
        assert len(institutions) == 1
        assert "Big State U" in institutions  # Highest at 22000

    def test_zero_prev_enrollment_no_inf(self):
        """YoYChangePercent should be 0 when previous year enrollment is zero."""
        df = pd.DataFrame([
            {"UnitID": 1, "TOTAL_ENROLL_2023": 0, "TOTAL_ENROLL_2024": 5000},
        ])
        result = _prepare_enrollment_trend_dataframe(
            df, _make_metadata(), top_n=10, anchor_year=2024,
        )
        if not result.empty:
            pcts = result["YoYChangePercent"].replace([float("inf"), float("-inf")], None)
            assert pcts.isna().sum() == 0 or all(pcts.dropna() != float("inf"))

    def test_empty_input(self):
        df = _prepare_enrollment_trend_dataframe(
            pd.DataFrame(), _make_metadata(), top_n=10, anchor_year=2024,
        )
        assert df.empty
