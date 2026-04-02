"""Tests for loan trend chart data preparation."""

import pandas as pd
import pytest

from src.charts.loan_trend_chart import _prepare_loan_trend_dataframe
from src.charts.loan_trend_total_chart import _prepare_loan_trend_total_dataframe


def _make_loan_df(rows):
    """Build a minimal loan DataFrame with YR columns."""
    return pd.DataFrame(rows)


def _make_metadata_df(rows):
    """Build a minimal metadata DataFrame."""
    return pd.DataFrame(rows)


LOAN_DATA = [
    {"UnitID": 1, "YR2020": 1_000_000_000, "YR2021": 1_200_000_000, "YR2022": 1_500_000_000},
    {"UnitID": 2, "YR2020": 500_000_000, "YR2021": 400_000_000, "YR2022": 600_000_000},
    {"UnitID": 3, "YR2020": 200_000_000, "YR2021": 250_000_000, "YR2022": 300_000_000},
]

METADATA = [
    {"UnitID": 1, "institution": "Big State U", "sector": "Public"},
    {"UnitID": 2, "institution": "Private College", "sector": "Private, not-for-profit"},
    {"UnitID": 3, "institution": "Tech Institute", "sector": "Public"},
]


class TestPrepareLoanTrendDataframe:
    def test_basic_output_columns(self):
        df, anchor = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=10,
        )
        expected = {
            "UnitID", "Institution", "Sector", "Year",
            "LoanDollarsBillions", "AnchorYear", "ChangeDirection", "YoYChangePercent",
        }
        assert set(df.columns) == expected

    def test_anchor_year_is_max(self):
        df, anchor = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=10,
        )
        assert anchor == 2022

    def test_top_n_filters_institutions(self):
        df, _ = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=2,
        )
        institutions = df["Institution"].unique()
        assert len(institutions) == 2
        # Top 2 by 2022 dollars: Big State U (1.5B) and Private College (600M)
        assert "Big State U" in institutions
        assert "Private College" in institutions

    def test_yoy_change_direction(self):
        df, _ = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=10,
        )
        # Big State U: 2020→2021 increase, 2021→2022 increase
        bsu = df[df["Institution"] == "Big State U"].sort_values("Year")
        directions = bsu["ChangeDirection"].tolist()
        assert directions[0] == "Same"  # First year, no previous
        assert directions[1] == "Increase"
        assert directions[2] == "Increase"

    def test_first_year_marked_same(self):
        df, _ = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=10,
        )
        first_years = df.groupby("Institution").first().reset_index()
        assert all(first_years["ChangeDirection"] == "Same")
        assert all(first_years["YoYChangePercent"] == 0.0)

    def test_dollars_converted_to_billions(self):
        df, _ = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), top_n=10,
        )
        bsu_2022 = df[(df["Institution"] == "Big State U") & (df["Year"] == 2022)]
        assert pytest.approx(bsu_2022["LoanDollarsBillions"].iloc[0], rel=1e-3) == 1.5

    def test_empty_input(self):
        df, anchor = _prepare_loan_trend_dataframe(
            pd.DataFrame(), _make_metadata_df(METADATA), top_n=10,
        )
        assert df.empty
        assert anchor is None

    def test_no_metadata_match(self):
        other_metadata = [{"UnitID": 999, "institution": "No Match", "sector": "Public"}]
        df, anchor = _prepare_loan_trend_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(other_metadata), top_n=10,
        )
        assert df.empty

    def test_missing_metadata_columns_raises(self):
        bad_metadata = pd.DataFrame([{"UnitID": 1, "name": "Foo"}])
        with pytest.raises(ValueError, match="Missing metadata columns"):
            _prepare_loan_trend_dataframe(
                _make_loan_df(LOAN_DATA), bad_metadata, top_n=10,
            )


class TestPrepareLoanTrendTotalDataframe:
    def test_aggregates_by_year(self):
        df = _prepare_loan_trend_total_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), sector="four_year",
        )
        assert not df.empty
        assert list(df.columns) == [
            "Year", "TotalLoanDollarsBillions", "YoYChangePercent", "ChangeDirection",
        ]
        # 3 years of data
        assert len(df) == 3

    def test_total_sums_correctly(self):
        df = _prepare_loan_trend_total_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), sector="four_year",
        )
        row_2022 = df[df["Year"] == 2022].iloc[0]
        expected_billions = (1_500_000_000 + 600_000_000 + 300_000_000) / 1e9
        assert pytest.approx(row_2022["TotalLoanDollarsBillions"], rel=1e-3) == expected_billions

    def test_yoy_percent_change(self):
        df = _prepare_loan_trend_total_dataframe(
            _make_loan_df(LOAN_DATA), _make_metadata_df(METADATA), sector="four_year",
        )
        df = df.sort_values("Year")
        # First year has NaN pct_change → classified as Same
        assert df.iloc[0]["ChangeDirection"] == "Same"
        # 2020 total: 1.7B, 2021 total: 1.85B → increase
        assert df.iloc[1]["ChangeDirection"] == "Increase"

    def test_empty_input(self):
        df = _prepare_loan_trend_total_dataframe(
            pd.DataFrame(), _make_metadata_df(METADATA), sector="four_year",
        )
        assert df.empty
