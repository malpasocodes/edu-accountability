"""Tests for faculty composition (adjunct reliance) chart data preparation."""

import pandas as pd

from src.charts.faculty_composition_chart import _prepare_faculty_ranking

FACULTY_DATA = [
    # 4-year institutions
    {
        "UnitID": 1,
        "institution": "Adjunct Heavy U",
        "state": "TX",
        "SECTOR": 3,
        "sector": "Private, for-profit",
        "enrollment": 8000,
        "fulltime_faculty": 10,
        "parttime_faculty": 190,
        "total_faculty": 200,
        "pct_parttime": 95.0,
    },
    {
        "UnitID": 2,
        "institution": "Balanced State",
        "state": "CA",
        "SECTOR": 1,
        "sector": "Public",
        "enrollment": 20000,
        "fulltime_faculty": 600,
        "parttime_faculty": 400,
        "total_faculty": 1000,
        "pct_parttime": 40.0,
    },
    {
        "UnitID": 3,
        "institution": "Full Time College",
        "state": "NY",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
        "enrollment": 3000,
        "fulltime_faculty": 180,
        "parttime_faculty": 20,
        "total_faculty": 200,
        "pct_parttime": 10.0,
    },
    # Small-enrollment 4-year school with heavy adjunct use (above staff floor)
    {
        "UnitID": 6,
        "institution": "Tiny Enrollment U",
        "state": "OR",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
        "enrollment": 200,
        "fulltime_faculty": 5,
        "parttime_faculty": 95,
        "total_faculty": 100,
        "pct_parttime": 95.0,
    },
    # Tiny 4-year school below the min-total (staff) threshold
    {
        "UnitID": 4,
        "institution": "Tiny Seminary",
        "state": "AZ",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
        "enrollment": 500,
        "fulltime_faculty": 1,
        "parttime_faculty": 9,
        "total_faculty": 10,
        "pct_parttime": 90.0,
    },
    # 2-year institution
    {
        "UnitID": 5,
        "institution": "Community CC",
        "state": "FL",
        "SECTOR": 4,
        "sector": "Public",
        "enrollment": 12000,
        "fulltime_faculty": 100,
        "parttime_faculty": 300,
        "total_faculty": 400,
        "pct_parttime": 75.0,
    },
]


def _make_df():
    return pd.DataFrame(FACULTY_DATA)


class TestPrepareFacultyRanking:
    def test_four_year_filter_excludes_two_year(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        assert not result.chart_data.empty
        # Community CC (2-year) must not appear
        assert "Community CC" not in set(result.chart_data["Institution"])

    def test_two_year_filter_only_two_year(self):
        result = _prepare_faculty_ranking(_make_df(), "two_year", 25, 50, 0)
        assert set(result.chart_data["Institution"]) == {"Community CC"}

    def test_min_total_filter_drops_tiny_staff_schools(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        # Tiny Seminary (total_faculty=10) is below threshold and excluded
        assert "Tiny Seminary" not in set(result.chart_data["Institution"])

    def test_enrollment_filter_drops_small_enrollment_schools(self):
        # With a 1,000-undergrad floor, Tiny Enrollment U (200) drops out...
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 1000)
        names = set(result.chart_data["Institution"])
        assert "Tiny Enrollment U" not in names
        assert "Adjunct Heavy U" in names

    def test_enrollment_filter_off_includes_small_schools(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        assert "Tiny Enrollment U" in set(result.chart_data["Institution"])

    def test_min_enrollment_recorded_on_result(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 5000)
        assert result.min_enrollment == 5000

    def test_ranked_descending_by_pct(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        pcts = list(result.chart_data["pct_parttime"])
        assert pcts == sorted(pcts, reverse=True)
        # Highest reliance should rank first
        assert result.chart_data.iloc[0]["pct_parttime"] == 95.0

    def test_top_n_limits_rows(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 1, 50, 0)
        assert len(result.chart_data) == 1

    def test_top_n_zero_shows_all_eligible(self):
        # 4 eligible 4-year schools (Tiny Seminary excluded by staff floor)
        result = _prepare_faculty_ranking(_make_df(), "four_year", 0, 50, 0)
        assert len(result.chart_data) == result.total_considered == 4

    def test_empty_input_returns_empty(self):
        result = _prepare_faculty_ranking(pd.DataFrame(), "four_year", 25, 50, 0)
        assert result.chart_data.empty
        assert result.table_data.empty

    def test_table_has_friendly_columns(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        assert "% Part-time" in result.table_data.columns
        assert "Total instructional" in result.table_data.columns

    def test_table_and_chart_include_enrollment(self):
        result = _prepare_faculty_ranking(_make_df(), "four_year", 25, 50, 0)
        assert "Undergrad Enrollment" in result.table_data.columns
        assert "enrollment" in result.chart_data.columns
