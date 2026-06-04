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
        "fulltime_faculty": 180,
        "parttime_faculty": 20,
        "total_faculty": 200,
        "pct_parttime": 10.0,
    },
    # Tiny 4-year school below the min-total threshold
    {
        "UnitID": 4,
        "institution": "Tiny Seminary",
        "state": "AZ",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
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
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=25, min_total=50
        )
        assert not result.chart_data.empty
        # Community CC (2-year) must not appear
        assert "Community CC" not in set(result.chart_data["Institution"])

    def test_two_year_filter_only_two_year(self):
        result = _prepare_faculty_ranking(
            _make_df(), "two_year", top_n=25, min_total=50
        )
        assert set(result.chart_data["Institution"]) == {"Community CC"}

    def test_min_total_filter_drops_tiny_schools(self):
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=25, min_total=50
        )
        # Tiny Seminary (total_faculty=10) is below threshold and excluded
        assert "Tiny Seminary" not in set(result.chart_data["Institution"])

    def test_ranked_descending_by_pct(self):
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=25, min_total=50
        )
        pcts = list(result.chart_data["pct_parttime"])
        assert pcts == sorted(pcts, reverse=True)
        # Highest reliance should rank first
        assert result.chart_data.iloc[0]["Institution"] == "Adjunct Heavy U"

    def test_top_n_limits_rows(self):
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=1, min_total=50
        )
        assert len(result.chart_data) == 1
        assert result.chart_data.iloc[0]["Institution"] == "Adjunct Heavy U"

    def test_total_considered_counts_eligible(self):
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=25, min_total=50
        )
        # 3 eligible 4-year schools (Tiny Seminary excluded by min_total)
        assert result.total_considered == 3

    def test_empty_input_returns_empty(self):
        result = _prepare_faculty_ranking(
            pd.DataFrame(), "four_year", top_n=25, min_total=50
        )
        assert result.chart_data.empty
        assert result.table_data.empty

    def test_table_has_friendly_columns(self):
        result = _prepare_faculty_ranking(
            _make_df(), "four_year", top_n=25, min_total=50
        )
        assert "% Part-time" in result.table_data.columns
        assert "Total instructional" in result.table_data.columns
