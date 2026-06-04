"""Tests for the adjunct-reliance-vs-graduation scatter data preparation."""

import pandas as pd

from src.charts.faculty_grad_chart import _prepare_grad_scatter

FACULTY_DATA = [
    {
        "UnitID": 1,
        "institution": "Big Adjunct U",
        "state": "TX",
        "SECTOR": 3,
        "sector": "Private, for-profit",
        "enrollment": 30000,
        "graduation_rate": 25.0,
        "pct_parttime": 96.0,
    },
    {
        "UnitID": 2,
        "institution": "Strong Public",
        "state": "CA",
        "SECTOR": 1,
        "sector": "Public",
        "enrollment": 20000,
        "graduation_rate": 70.0,
        "pct_parttime": 35.0,
    },
    {
        "UnitID": 3,
        "institution": "Small Private",
        "state": "NY",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
        "enrollment": 400,
        "graduation_rate": 55.0,
        "pct_parttime": 45.0,
    },
    # No graduation rate -> excluded from the segment entirely
    {
        "UnitID": 4,
        "institution": "No Grad Data U",
        "state": "AZ",
        "SECTOR": 2,
        "sector": "Private, not-for-profit",
        "enrollment": 5000,
        "graduation_rate": None,
        "pct_parttime": 60.0,
    },
    # 2-year school
    {
        "UnitID": 5,
        "institution": "Community CC",
        "state": "FL",
        "SECTOR": 4,
        "sector": "Public",
        "enrollment": 12000,
        "graduation_rate": 30.0,
        "pct_parttime": 75.0,
    },
]


def _make_df():
    return pd.DataFrame(FACULTY_DATA)


class TestPrepareGradScatter:
    def test_four_year_excludes_two_year(self):
        result = _prepare_grad_scatter(_make_df(), "four_year", 0)
        assert "Community CC" not in set(result.points["institution"])

    def test_drops_rows_without_graduation_rate(self):
        result = _prepare_grad_scatter(_make_df(), "four_year", 0)
        assert "No Grad Data U" not in set(result.points["institution"])
        # 3 four-year schools have grad rates
        assert result.segment_size == 3

    def test_medians_from_full_segment_not_enrollment_filtered(self):
        # Median pct of the 3 four-year schools: 35, 45, 96 -> 45
        result = _prepare_grad_scatter(_make_df(), "four_year", 10000)
        assert result.pct_median == 45.0
        assert result.grad_median == 55.0
        # but Small Private (400 UG) is filtered out of the plotted points
        assert "Small Private" not in set(result.points["institution"])

    def test_enrollment_filter_off_includes_small(self):
        result = _prepare_grad_scatter(_make_df(), "four_year", 0)
        assert "Small Private" in set(result.points["institution"])

    def test_points_have_expected_columns(self):
        result = _prepare_grad_scatter(_make_df(), "four_year", 0)
        for col in (
            "institution",
            "sector",
            "enrollment",
            "graduation_rate",
            "pct_parttime",
        ):
            assert col in result.points.columns

    def test_empty_input_returns_empty(self):
        result = _prepare_grad_scatter(pd.DataFrame(), "four_year", 0)
        assert result.points.empty
        assert result.segment_size == 0
