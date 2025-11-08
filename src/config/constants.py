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
EARNINGS_PREMIUM_SECTION = "Earnings Premium"
ROI_SECTION = "ROI"
COLLEGE_EXPLORER_SECTION = "College Explorer"
CANONICAL_IPEDS_SECTION = "Canonical IPEDS"


@dataclass(frozen=True)
class ValueGridChartConfig:
    """Configuration for a value grid chart."""
    label: str
    dataset_key: str
    min_enrollment: int


# Value Grid configurations
VALUE_GRID_CHART_CONFIGS = (
    ValueGridChartConfig(
        label="Cost vs Graduation Rate (4-year)",
        dataset_key="cost_vs_grad",
        min_enrollment=1000,
    ),
    ValueGridChartConfig(
        label="Cost vs Graduation Rate (2-year)",
        dataset_key="cost_vs_grad_two_year",
        min_enrollment=1000,
    ),
)

# Enrollment filter options for Value Grid
ENROLLMENT_FILTER_OPTIONS = [1, 500, 1000, 5000, 10000]
DEFAULT_ENROLLMENT_FILTER = 1000

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
PELL_TREND_FOUR_LABEL = "Pell Dollars Trend (Top 10) (4-year)"
PELL_TREND_TWO_LABEL = "Pell Dollars Trend (Top 10) (2-year)"

# Pell Grant chart labels - Consolidated (for new navigation)
PELL_TOP_DOLLARS_LABEL = "Top 25 Pell Dollar Recipients"
PELL_VS_GRAD_LABEL = "Pell Dollars vs Graduation Rate"
PELL_TREND_LABEL = "Pell Dollars Trend (Top 10)"
PELL_TREND_TOTAL_LABEL = "Pell Dollars Trend (Total)"
PELL_GRAD_RATE_LABEL = "Pell Graduation Rate"

PELL_CHARTS: List[str] = [
    PELL_TOP_DOLLARS_LABEL,
    PELL_VS_GRAD_LABEL,
    PELL_TREND_LABEL,
    PELL_TREND_TOTAL_LABEL,
    PELL_GRAD_RATE_LABEL,
]
PELL_OVERVIEW_LABEL = "Overview"


# Federal Loan chart labels - Individual (for backward compatibility)
LOAN_TOP_DOLLARS_FOUR_LABEL = "Top 25 Federal Loan Dollars (4-year)"
LOAN_TOP_DOLLARS_TWO_LABEL = "Top 25 Federal Loan Dollars (2-year)"
LOAN_VS_GRAD_FOUR_LABEL = "Federal Loans vs Graduation Rate (4-year)"
LOAN_VS_GRAD_TWO_LABEL = "Federal Loans vs Graduation Rate (2-year)"
LOAN_TREND_FOUR_LABEL = "Federal Loan Dollars Trend (Top 10) (4-year)"
LOAN_TREND_TWO_LABEL = "Federal Loan Dollars Trend (Top 10) (2-year)"

# Federal Loan chart labels - Consolidated (for new navigation)
LOAN_TOP_DOLLARS_LABEL = "Top 25 Federal Loan Dollars"
LOAN_VS_GRAD_LABEL = "Federal Loans vs Graduation Rate"
LOAN_TREND_LABEL = "Federal Loan Dollars Trend (Top 10)"
LOAN_TREND_TOTAL_LABEL = "Federal Loan Dollars Trend (Total)"

LOAN_CHARTS: List[str] = [
    LOAN_TOP_DOLLARS_LABEL,
    LOAN_VS_GRAD_LABEL,
    LOAN_TREND_LABEL,
    LOAN_TREND_TOTAL_LABEL,
]
LOAN_OVERVIEW_LABEL = "Overview"


# Distance Education chart labels
DISTANCE_TOP_ENROLLMENT_LABEL = "Top 25 Total Enrollment (Distance Education Breakdown)"
DISTANCE_ENROLLMENT_TREND_LABEL = "Total Enrollment Trend (Top 10 Institutions)"
DISTANCE_DE_TREND_LABEL = "Exclusive Distance Education Trend (Top 10 Institutions)"

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
COLLEGE_GRAD_RATES_LABEL = "Graduation Rates"
COLLEGE_DISTANCE_ED_LABEL = "Distance Education"

COLLEGE_EXPLORER_CHARTS: List[str] = [
    COLLEGE_SUMMARY_LABEL,
    COLLEGE_LOANS_PELL_LABEL,
    COLLEGE_GRAD_RATES_LABEL,
    COLLEGE_DISTANCE_ED_LABEL,
]

CANONICAL_IPEDS_OVERVIEW_LABEL = "Overview"
CANONICAL_DATASET_GRAD = "Graduation Rates"
CANONICAL_DATASET_PELL = "Percent Pell"
CANONICAL_DATASET_LOANS = "Percent Loans"
CANONICAL_DATASET_RETENTION = "Retention Cohort Size (Full-time)"
CANONICAL_DATASET_RETENTION_RATE = "Retention Rate (Full-time)"
CANONICAL_DATASETS: List[str] = [
    CANONICAL_DATASET_GRAD,
    CANONICAL_DATASET_PELL,
    CANONICAL_DATASET_LOANS,
    CANONICAL_DATASET_RETENTION,
    CANONICAL_DATASET_RETENTION_RATE,
]

# Earnings Premium Analysis labels (National - Section 9)
EARNINGS_PREMIUM_OVERVIEW_LABEL = "Overview"
EP_NATIONAL_OVERVIEW_LABEL = "Risk Distribution"
EP_OVERVIEW_RISK_MAP_LABEL = "Risk Map"
EP_INSTITUTION_LOOKUP_LABEL = "Institution Lookup"
EP_STATE_ANALYSIS_LABEL = "State Analysis"
EP_SECTOR_COMPARISON_LABEL = "Sector Comparison"
EP_RISK_QUADRANTS_LABEL = "Risk Quadrants"
EP_PROGRAM_DISTRIBUTION_LABEL = "Program Distribution"
EP_METHODOLOGY_LABEL = "Methodology & Limitations"

# Phase 1 MVP Charts (Phase 2 adds State Analysis and Sector Comparison, Phase 3 adds Risk Quadrants, Phase 4 adds Program Distribution)
EARNINGS_PREMIUM_CHARTS: List[str] = [
    EP_OVERVIEW_RISK_MAP_LABEL,
    EP_INSTITUTION_LOOKUP_LABEL,
    EP_STATE_ANALYSIS_LABEL,
    EP_SECTOR_COMPARISON_LABEL,
    EP_RISK_QUADRANTS_LABEL,
    EP_PROGRAM_DISTRIBUTION_LABEL,
    EP_METHODOLOGY_LABEL,
]

# Legacy EP labels (California institutions - deprecated, kept for backward compatibility)
ROI_EARNINGS_PREMIUM_LABEL = "Earnings Premium (All)"
ROI_EARNINGS_PREMIUM_RANKINGS_LABEL = "Earnings Premium Rankings"

# ROI labels (California institutions only - migrated from epanalysis)
ROI_OVERVIEW_LABEL = "Overview"
ROI_QUADRANT_LABEL = "Cost vs Earnings Quadrant"
ROI_RANKINGS_LABEL = "Top 25 ROI Rankings"
ROI_DISTRIBUTION_LABEL = "ROI by Sector"

ROI_CHARTS: List[str] = [
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
]

# College Explorer - ROI tab
COLLEGE_EXPLORER_ROI_LABEL = "Earnings & ROI"


# Session state defaults
DEFAULT_SESSION_STATE: Dict[str, str] = {
    "active_section": OVERVIEW_SECTION,
    "value_grid_chart": VALUE_GRID_OVERVIEW_LABEL,
    "value_grid_enrollment_filter": DEFAULT_ENROLLMENT_FILTER,
    "loan_chart": LOAN_OVERVIEW_LABEL,
    "pell_chart": PELL_OVERVIEW_LABEL,
    "distance_chart": DISTANCE_OVERVIEW_LABEL,
    "earnings_premium_chart": EARNINGS_PREMIUM_OVERVIEW_LABEL,
    "roi_chart": ROI_OVERVIEW_LABEL,
    "college_explorer_chart": COLLEGE_EXPLORER_OVERVIEW_LABEL,
    "canonical_ipeds_chart": CANONICAL_IPEDS_OVERVIEW_LABEL,
}
