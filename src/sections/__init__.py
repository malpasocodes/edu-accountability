"""Dashboard sections package."""

from .base import BaseSection
from .overview import OverviewSection
from .value_grid import ValueGridSection
from .federal_loans import FederalLoansSection
from .pell_grants import PellGrantsSection
from .distance_education import DistanceEducationSection
from .earnings_premium_analysis import EarningsPremiumAnalysisSection as EarningsPremiumSection
from .roi import ROISection
from .college_explorer import CollegeExplorerSection
from .graduation_alpha import GraduationAlphaSection

__all__ = [
    "BaseSection",
    "OverviewSection",
    "ValueGridSection",
    "FederalLoansSection",
    "PellGrantsSection",
    "DistanceEducationSection",
    "EarningsPremiumSection",
    "ROISection",
    "CollegeExplorerSection",
    "GraduationAlphaSection",
]
