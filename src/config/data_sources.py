"""Data source configuration for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


def get_project_root() -> Path:
    """Get the project root directory."""
    # Navigate up from src/config to project root
    return Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class DataSourceConfig:
    """Configuration for a data source file."""
    path: Path
    description: str
    required: bool = True


class DataSources:
    """Central configuration for all data sources."""
    
    _project_root = get_project_root()
    _data_dir = _project_root / "data"
    _raw_dir = _data_dir / "raw"
    _processed_dir = _data_dir / "processed"
    _ipeds_dir = _raw_dir / "ipeds" / "2023"
    _fsa_dir = _raw_dir / "fsa"
    
    # Raw data sources - FSA
    PELL_RAW = DataSourceConfig(
        path=_fsa_dir / "pelltotals.csv",
        description="Pell grant totals by institution",
        required=True
    )
    
    LOAN_RAW = DataSourceConfig(
        path=_fsa_dir / "loantotals.csv",
        description="Federal loan totals by institution",
        required=False
    )
    
    # Raw data sources - IPEDS
    COST_RAW = DataSourceConfig(
        path=_ipeds_dir / "cost.csv",
        description="Cost data by institution",
        required=True
    )
    
    ENROLLMENT_RAW = DataSourceConfig(
        path=_ipeds_dir / "enrollment.csv",
        description="Enrollment data by institution",
        required=True
    )
    
    GRADRATES_RAW = DataSourceConfig(
        path=_ipeds_dir / "gradrates.csv",
        description="Graduation rates by institution",
        required=True
    )
    
    INSTITUTIONS_RAW = DataSourceConfig(
        path=_ipeds_dir / "institutions.csv",
        description="Institution metadata",
        required=True
    )

    DISTANCE_RAW = DataSourceConfig(
        path=_ipeds_dir / "distanced.csv",
        description="Distance education enrollment data",
        required=False
    )
    
    # Processed data sources - Pell
    PELL_TOP_DOLLARS = DataSourceConfig(
        path=_processed_dir / "pell_top_dollars.csv",
        description="Top Pell dollar recipients (all)",
        required=False
    )
    
    PELL_TOP_DOLLARS_FOUR = DataSourceConfig(
        path=_processed_dir / "pell_top_dollars_four_year.csv",
        description="Top Pell dollar recipients (4-year)",
        required=False
    )
    
    PELL_TOP_DOLLARS_TWO = DataSourceConfig(
        path=_processed_dir / "pell_top_dollars_two_year.csv",
        description="Top Pell dollar recipients (2-year)",
        required=False
    )
    
    PELL_TREND_FOUR = DataSourceConfig(
        path=_processed_dir / "pell_top_dollars_trend_four_year.csv",
        description="Pell dollar trends (4-year)",
        required=False
    )
    
    PELL_TREND_TWO = DataSourceConfig(
        path=_processed_dir / "pell_top_dollars_trend_two_year.csv",
        description="Pell dollar trends (2-year)",
        required=False
    )
    
    PELL_VS_GRAD = DataSourceConfig(
        path=_processed_dir / "pell_vs_grad_scatter.csv",
        description="Pell vs graduation rates (all)",
        required=False
    )
    
    PELL_VS_GRAD_FOUR = DataSourceConfig(
        path=_processed_dir / "pell_vs_grad_scatter_four_year.csv",
        description="Pell vs graduation rates (4-year)",
        required=False
    )
    
    PELL_VS_GRAD_TWO = DataSourceConfig(
        path=_processed_dir / "pell_vs_grad_scatter_two_year.csv",
        description="Pell vs graduation rates (2-year)",
        required=False
    )
    
    # Processed data sources - Value Grid
    TUITION_VS_GRAD = DataSourceConfig(
        path=_processed_dir / "tuition_vs_graduation.csv",
        description="Tuition vs graduation rates (4-year)",
        required=False
    )
    
    TUITION_VS_GRAD_PARQUET = DataSourceConfig(
        path=_processed_dir / "tuition_vs_graduation.parquet",
        description="Tuition vs graduation rates (4-year, Parquet)",
        required=False
    )
    
    TUITION_VS_GRAD_TWO = DataSourceConfig(
        path=_processed_dir / "tuition_vs_graduation_two_year.csv",
        description="Tuition vs graduation rates (2-year)",
        required=False
    )
    
    TUITION_VS_GRAD_TWO_PARQUET = DataSourceConfig(
        path=_processed_dir / "tuition_vs_graduation_two_year.parquet",
        description="Tuition vs graduation rates (2-year, Parquet)",
        required=False
    )
    
    @classmethod
    def get_pell_resources_map(cls) -> Dict[str, DataSourceConfig]:
        """Get a mapping of Pell resource keys to their configurations."""
        return {
            "raw": cls.PELL_RAW,
            "top_all": cls.PELL_TOP_DOLLARS,
            "top_four": cls.PELL_TOP_DOLLARS_FOUR,
            "top_two": cls.PELL_TOP_DOLLARS_TWO,
            "trend_four": cls.PELL_TREND_FOUR,
            "trend_two": cls.PELL_TREND_TWO,
            "scatter_all": cls.PELL_VS_GRAD,
            "scatter_four": cls.PELL_VS_GRAD_FOUR,
            "scatter_two": cls.PELL_VS_GRAD_TWO,
        }
    
    @classmethod
    def get_all_sources(cls) -> Dict[str, DataSourceConfig]:
        """Get all data source configurations."""
        return {
            "pell_raw": cls.PELL_RAW,
            "loan_raw": cls.LOAN_RAW,
            "cost_raw": cls.COST_RAW,
            "enrollment_raw": cls.ENROLLMENT_RAW,
            "gradrates_raw": cls.GRADRATES_RAW,
            "institutions_raw": cls.INSTITUTIONS_RAW,
            "pell_top_dollars": cls.PELL_TOP_DOLLARS,
            "pell_top_dollars_four": cls.PELL_TOP_DOLLARS_FOUR,
            "pell_top_dollars_two": cls.PELL_TOP_DOLLARS_TWO,
            "pell_trend_four": cls.PELL_TREND_FOUR,
            "pell_trend_two": cls.PELL_TREND_TWO,
            "pell_vs_grad": cls.PELL_VS_GRAD,
            "pell_vs_grad_four": cls.PELL_VS_GRAD_FOUR,
            "pell_vs_grad_two": cls.PELL_VS_GRAD_TWO,
            "tuition_vs_grad": cls.TUITION_VS_GRAD,
            "tuition_vs_grad_parquet": cls.TUITION_VS_GRAD_PARQUET,
            "tuition_vs_grad_two": cls.TUITION_VS_GRAD_TWO,
            "tuition_vs_grad_two_parquet": cls.TUITION_VS_GRAD_TWO_PARQUET,
            "distance_raw": cls.DISTANCE_RAW,
        }