"""Constants and configuration for the College Accountability Dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


# Section identifiers
OVERVIEW_SECTION = "Project Overview"
VALUE_GRID_SECTION = "College Value Grid"
FEDERAL_LOANS_SECTION = "Federal Loans"
PELL_SECTION = "Pell Grants"
DISTANCE_EDUCATION_SECTION = "Distance Education"
COLLEGE_EXPLORER_SECTION = "College Explorer"


@dataclass(frozen=True)
class ValueGridChartConfig:
    """Configuration for a value grid chart."""
    label: str
    dataset_key: str
    min_enrollment: int


# Value Grid configurations
VALUE_GRID_CHART_CONFIGS = (
    ValueGridChartConfig(
        label="Cost vs Graduation (4-year)",
        dataset_key="cost_vs_grad",
        min_enrollment=1000,
    ),
    ValueGridChartConfig(
        label="Cost vs Graduation (2-year)",
        dataset_key="cost_vs_grad_two_year",
        min_enrollment=0,
    ),
)

VALUE_GRID_OVERVIEW_LABEL = "Overview"
VALUE_GRID_CONFIG_MAP: Dict[str, ValueGridChartConfig] = {
    config.label: config for config in VALUE_GRID_CHART_CONFIGS
}
FOUR_YEAR_VALUE_GRID_LABEL = VALUE_GRID_CHART_CONFIGS[0].label
TWO_YEAR_VALUE_GRID_LABEL = VALUE_GRID_CHART_CONFIGS[1].label


# Pell Grant chart labels - Individual (for backward compatibility)
PELL_TOP_DOLLARS_FOUR_LABEL = "Top 25 Pell Dollar Recipients (4-year)"
PELL_TOP_DOLLARS_TWO_LABEL = "Top 25 Pell Dollar Recipients (2-year)"
PELL_VS_GRAD_FOUR_LABEL = "Pell Dollars vs Graduation Rate (4-year)"
PELL_VS_GRAD_TWO_LABEL = "Pell Dollars vs Graduation Rate (2-year)"
PELL_TREND_FOUR_LABEL = "Pell Dollars Trend (4-year)"
PELL_TREND_TWO_LABEL = "Pell Dollars Trend (2-year)"

# Pell Grant chart labels - Consolidated (for new navigation)
PELL_TOP_DOLLARS_LABEL = "Top 25 Pell Dollar Recipients"
PELL_VS_GRAD_LABEL = "Pell Dollars vs Graduation Rate"
PELL_TREND_LABEL = "Pell Dollars Trend"
PELL_GRAD_RATE_LABEL = "Pell Graduation Rate"

PELL_CHARTS: List[str] = [
    PELL_TOP_DOLLARS_LABEL,
    PELL_VS_GRAD_LABEL,
    PELL_TREND_LABEL,
    PELL_GRAD_RATE_LABEL,
]
PELL_OVERVIEW_LABEL = "Overview"


# Federal Loan chart labels - Individual (for backward compatibility)
LOAN_TOP_DOLLARS_FOUR_LABEL = "Top 25 Federal Loan Dollars (4-year)"
LOAN_TOP_DOLLARS_TWO_LABEL = "Top 25 Federal Loan Dollars (2-year)"
LOAN_VS_GRAD_FOUR_LABEL = "Federal Loans vs Graduation Rate (4-year)"
LOAN_VS_GRAD_TWO_LABEL = "Federal Loans vs Graduation Rate (2-year)"
LOAN_TREND_FOUR_LABEL = "Federal Loan Dollars Trend (4-year)"
LOAN_TREND_TWO_LABEL = "Federal Loan Dollars Trend (2-year)"

# Federal Loan chart labels - Consolidated (for new navigation)
LOAN_TOP_DOLLARS_LABEL = "Top 25 Federal Loan Dollars"
LOAN_VS_GRAD_LABEL = "Federal Loans vs Graduation Rate"
LOAN_TREND_LABEL = "Federal Loan Dollars Trend"

LOAN_CHARTS: List[str] = [
    LOAN_TOP_DOLLARS_LABEL,
    LOAN_VS_GRAD_LABEL,
    LOAN_TREND_LABEL,
]
LOAN_OVERVIEW_LABEL = "Overview"


# Distance Education chart labels
DISTANCE_TOP_ENROLLMENT_LABEL = "Top 25 Distance Education Enrollment"
DISTANCE_ENROLLMENT_TREND_LABEL = "Total Enrollment Trend"
DISTANCE_DE_TREND_LABEL = "Distance Education Trend"

DISTANCE_CHARTS: List[str] = [
    DISTANCE_TOP_ENROLLMENT_LABEL,
    DISTANCE_ENROLLMENT_TREND_LABEL,
    DISTANCE_DE_TREND_LABEL,
]
DISTANCE_OVERVIEW_LABEL = "Overview"


# College Explorer labels
COLLEGE_EXPLORER_OVERVIEW_LABEL = "Overview"
COLLEGE_SUMMARY_LABEL = "Summary"
COLLEGE_LOANS_PELL_LABEL = "Federal Loans and Pell Grants"

COLLEGE_EXPLORER_CHARTS: List[str] = [
    COLLEGE_SUMMARY_LABEL,
    COLLEGE_LOANS_PELL_LABEL,
]


# Session state defaults
DEFAULT_SESSION_STATE: Dict[str, str] = {
    "active_section": OVERVIEW_SECTION,
    "value_grid_chart": VALUE_GRID_OVERVIEW_LABEL,
    "loan_chart": LOAN_OVERVIEW_LABEL,
    "pell_chart": PELL_OVERVIEW_LABEL,
    "distance_chart": DISTANCE_OVERVIEW_LABEL,
    "college_explorer_chart": COLLEGE_EXPLORER_OVERVIEW_LABEL,
}