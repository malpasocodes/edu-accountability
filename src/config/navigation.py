"""Navigation configuration for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .constants import (
    OVERVIEW_SECTION,
    VALUE_GRID_SECTION,
    FEDERAL_LOANS_SECTION,
    PELL_SECTION,
    VALUE_GRID_OVERVIEW_LABEL,
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    LOAN_OVERVIEW_LABEL,
    LOAN_CHARTS,
    PELL_OVERVIEW_LABEL,
    PELL_CHARTS,
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
    
    @classmethod
    def get_sections(cls) -> List[SectionConfig]:
        """Get all configured sections in navigation order."""
        return [
            cls.OVERVIEW,
            cls.VALUE_GRID,
            cls.FEDERAL_LOANS,
            cls.PELL_GRANTS,
        ]
    
    @classmethod
    def get_section_by_name(cls, name: str) -> Optional[SectionConfig]:
        """Get a section configuration by its name."""
        for section in cls.get_sections():
            if section.name == name:
                return section
        return None