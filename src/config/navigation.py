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
    COLLEGE_EXPLORER_SECTION,
    CANONICAL_IPEDS_SECTION,
    SCORECARD_SECTION,
    VALUE_GRID_OVERVIEW_LABEL,
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    LOAN_OVERVIEW_LABEL,
    LOAN_CHARTS,
    PELL_OVERVIEW_LABEL,
    PELL_CHARTS,
    DISTANCE_OVERVIEW_LABEL,
    DISTANCE_CHARTS,
    COLLEGE_EXPLORER_OVERVIEW_LABEL,
    COLLEGE_EXPLORER_CHARTS,
    CANONICAL_IPEDS_OVERVIEW_LABEL,
    CANONICAL_DATASETS,
    SCORECARD_OVERVIEW_LABEL,
    SCORECARD_DATASETS,
)
from .feature_flags import (
    ENABLE_CANONICAL_IPEDS_SECTION,
    ENABLE_CANONICAL_SCORECARD_SECTION,
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

    CANONICAL_IPEDS = SectionConfig(
        name=CANONICAL_IPEDS_SECTION,
        icon="🧪",
        label="Canonical IPEDS",
        overview_chart=ChartConfig(
            label=CANONICAL_IPEDS_OVERVIEW_LABEL,
            key="nav_canonical_ipeds_overview",
            description="Canonical dataset explorer",
        ),
        charts=[
            ChartConfig(
                label=dataset,
                key=f"nav_canonical_{index}",
                description=None,
            )
            for index, dataset in enumerate(CANONICAL_DATASETS)
        ],
        session_key="canonical_ipeds_chart",
        description="Alpha pilots powered by canonical IPEDS datasets",
    )

    SCORECARD = SectionConfig(
        name=SCORECARD_SECTION,
        icon="📚",
        label="Canonical Scorecard",
        overview_chart=ChartConfig(
            label=SCORECARD_OVERVIEW_LABEL,
            key="nav_scorecard_overview",
            description="Median debt and 3-year repayment status",
        ),
        charts=[
            ChartConfig(label=label, key=f"nav_scorecard_{i}")
            for i, label in enumerate(SCORECARD_DATASETS)
        ],
        session_key="scorecard_chart",
        description="Canonical Scorecard metrics",
    )

    @classmethod
    def get_sections(cls) -> List[SectionConfig]:
        """Get all configured sections in navigation order."""
        sections = [
            cls.OVERVIEW,
            cls.VALUE_GRID,
            cls.FEDERAL_LOANS,
            cls.PELL_GRANTS,
            cls.DISTANCE_EDUCATION,
            cls.COLLEGE_EXPLORER,
        ]
        if ENABLE_CANONICAL_IPEDS_SECTION:
            sections.append(cls.CANONICAL_IPEDS)
        if ENABLE_CANONICAL_SCORECARD_SECTION:
            sections.append(cls.SCORECARD)
        return sections
    
    @classmethod
    def get_section_by_name(cls, name: str) -> Optional[SectionConfig]:
        """Get a section configuration by its name."""
        for section in cls.get_sections():
            if section.name == name:
                return section
        return None
