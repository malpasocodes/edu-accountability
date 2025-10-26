"""Navigation configuration for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .constants import (
    OVERVIEW_SECTION,
    VALUE_GRID_SECTION,
    FEDERAL_LOANS_SECTION,
    PELL_SECTION,
    DISTANCE_EDUCATION_SECTION,
    EARNINGS_PREMIUM_SECTION,
    ROI_SECTION,
    COLLEGE_EXPLORER_SECTION,
    VALUE_GRID_OVERVIEW_LABEL,
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    LOAN_OVERVIEW_LABEL,
    LOAN_CHARTS,
    PELL_OVERVIEW_LABEL,
    PELL_CHARTS,
    DISTANCE_OVERVIEW_LABEL,
    DISTANCE_CHARTS,
    EARNINGS_PREMIUM_OVERVIEW_LABEL,
    EARNINGS_PREMIUM_CHARTS,
    EP_OVERVIEW_RISK_MAP_LABEL,
    EP_INSTITUTION_LOOKUP_LABEL,
    EP_STATE_ANALYSIS_LABEL,
    EP_SECTOR_COMPARISON_LABEL,
    EP_RISK_QUADRANTS_LABEL,
    EP_METHODOLOGY_LABEL,
    ROI_OVERVIEW_LABEL,
    ROI_CHARTS,
    COLLEGE_EXPLORER_OVERVIEW_LABEL,
    COLLEGE_EXPLORER_CHARTS,
)


@dataclass(frozen=True)
class ChartConfig:
    """Configuration for a chart within a section."""
    label: str
    key: str
    description: Optional[str] = None


@dataclass(frozen=True)
class SectionConfig:
    """Configuration for a dashboard section."""
    name: str
    icon: str
    label: str
    overview_chart: ChartConfig
    charts: List[ChartConfig]
    session_key: str
    description: Optional[str] = None


class NavigationConfig:
    """Central navigation configuration for the dashboard."""
    
    OVERVIEW = SectionConfig(
        name=OVERVIEW_SECTION,
        icon="🏠",
        label="Home",
        overview_chart=ChartConfig(
            label="Overview",
            key="overview",
            description="Project context and navigation tips"
        ),
        charts=[],
        session_key="",
        description="Landing page with project information"
    )
    
    VALUE_GRID = SectionConfig(
        name=VALUE_GRID_SECTION,
        icon="📊",
        label="College Value Grid",
        overview_chart=ChartConfig(
            label=VALUE_GRID_OVERVIEW_LABEL,
            key="nav_value_grid_overview",
            description="How net price aligns with completion"
        ),
        charts=[
            ChartConfig(
                label=FOUR_YEAR_VALUE_GRID_LABEL,
                key="nav_value_grid_four",
                description="Four-year institution analysis"
            ),
            ChartConfig(
                label=TWO_YEAR_VALUE_GRID_LABEL,
                key="nav_value_grid_two",
                description="Two-year institution analysis"
            ),
        ],
        session_key="value_grid_chart",
        description="Compare net price against graduation outcomes"
    )
    
    FEDERAL_LOANS = SectionConfig(
        name=FEDERAL_LOANS_SECTION,
        icon="💵",
        label="Federal Loans",
        overview_chart=ChartConfig(
            label=LOAN_OVERVIEW_LABEL,
            key="nav_loans_overview",
            description="Federal lending patterns and affordability"
        ),
        charts=[
            ChartConfig(
                label=chart_label,
                key=f"nav_loans_{index}",
                description=None
            )
            for index, chart_label in enumerate(LOAN_CHARTS)
        ],
        session_key="loan_chart",
        description="Analyze federal loan distributions and trends"
    )
    
    PELL_GRANTS = SectionConfig(
        name=PELL_SECTION,
        icon="🎓",
        label="Pell Grants",
        overview_chart=ChartConfig(
            label=PELL_OVERVIEW_LABEL,
            key="nav_pell_overview",
            description="Need-based aid distributions"
        ),
        charts=[
            ChartConfig(
                label=chart_label,
                key=f"nav_pell_{index}",
                description=None
            )
            for index, chart_label in enumerate(PELL_CHARTS)
        ],
        session_key="pell_chart",
        description="Review Pell Grant distributions and outcomes"
    )

    DISTANCE_EDUCATION = SectionConfig(
        name=DISTANCE_EDUCATION_SECTION,
        icon="💻",
        label="Distance Education",
        overview_chart=ChartConfig(
            label=DISTANCE_OVERVIEW_LABEL,
            key="nav_distance_overview",
            description="Online and hybrid learning patterns"
        ),
        charts=[
            ChartConfig(
                label=chart_label,
                key=f"nav_distance_{index}",
                description=None
            )
            for index, chart_label in enumerate(DISTANCE_CHARTS)
        ],
        session_key="distance_chart",
        description="Explore distance education enrollment patterns"
    )

    EARNINGS_PREMIUM = SectionConfig(
        name=EARNINGS_PREMIUM_SECTION,
        icon="📈",
        label="Earnings Premium Analysis",
        overview_chart=ChartConfig(
            label=EARNINGS_PREMIUM_OVERVIEW_LABEL,
            key="nav_earnings_premium_overview",
            description="Institutional EP risk assessment (2026 requirements)"
        ),
        charts=[
            ChartConfig(
                label=EP_OVERVIEW_RISK_MAP_LABEL,
                key="nav_ep_overview_risk_map",
                description="National risk map and summary statistics"
            ),
            ChartConfig(
                label=EP_INSTITUTION_LOOKUP_LABEL,
                key="nav_ep_institution_lookup",
                description="Search institutions and view risk assessments"
            ),
            ChartConfig(
                label=EP_STATE_ANALYSIS_LABEL,
                key="nav_ep_state_analysis",
                description="Deep dive into EP risk by state"
            ),
            ChartConfig(
                label=EP_SECTOR_COMPARISON_LABEL,
                key="nav_ep_sector_comparison",
                description="Compare risk across institutional types"
            ),
            ChartConfig(
                label=EP_RISK_QUADRANTS_LABEL,
                key="nav_ep_risk_quadrants",
                description="Scatter plots by risk category with sector colors"
            ),
            ChartConfig(
                label=EP_METHODOLOGY_LABEL,
                key="nav_ep_methodology",
                description="Data sources, calculations, and limitations"
            ),
        ],
        session_key="earnings_premium_chart",
        description="Assess institutional readiness for July 1, 2026 EP requirements"
    )

    ROI = SectionConfig(
        name=ROI_SECTION,
        icon="💰",
        label="ROI",
        overview_chart=ChartConfig(
            label=ROI_OVERVIEW_LABEL,
            key="nav_roi_overview",
            description="Return on investment analysis"
        ),
        charts=[
            ChartConfig(
                label=chart_label,
                key=f"nav_roi_{index}",
                description=None
            )
            for index, chart_label in enumerate(ROI_CHARTS)
        ],
        session_key="roi_chart",
        description="Analyze return on investment for higher education"
    )

    COLLEGE_EXPLORER = SectionConfig(
        name=COLLEGE_EXPLORER_SECTION,
        icon="🔍",
        label="College Explorer",
        overview_chart=ChartConfig(
            label=COLLEGE_EXPLORER_OVERVIEW_LABEL,
            key="nav_college_explorer_overview",
            description="Explore individual college data"
        ),
        charts=[
            ChartConfig(
                label=chart_label,
                key=f"nav_college_explorer_{index}",
                description=None
            )
            for index, chart_label in enumerate(COLLEGE_EXPLORER_CHARTS)
        ],
        session_key="college_explorer_chart",
        description="Get detailed information on individual colleges"
    )

    @classmethod
    def get_sections(cls) -> List[SectionConfig]:
        """Get all configured sections in navigation order."""
        return [
            cls.OVERVIEW,
            cls.VALUE_GRID,
            cls.FEDERAL_LOANS,
            cls.PELL_GRANTS,
            cls.DISTANCE_EDUCATION,
            cls.EARNINGS_PREMIUM,
            cls.ROI,
            cls.COLLEGE_EXPLORER,
        ]
    
    @classmethod
    def get_section_by_name(cls, name: str) -> Optional[SectionConfig]:
        """Get a section configuration by its name."""
        for section in cls.get_sections():
            if section.name == name:
                return section
        return None