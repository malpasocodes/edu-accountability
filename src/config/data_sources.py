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

    _fsa_dir = _raw_dir / "ipeds" / "fsa"
    if not _fsa_dir.exists():
        _fsa_dir = _raw_dir / "fsa"
    _epanalysis_dir = _raw_dir / "epanalysis"
    _canonical_dir = _processed_dir / "2023" / "canonical"

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

    RETENTION_RATE_PCT_RAW = DataSourceConfig(
        path=_raw_dir / "ipeds" / "retention_rate_pctgs.csv",
        description="Full-time retention rate percentages by institution",
        required=False,
    )

    PELL_GRAD_RATES_RAW = DataSourceConfig(
        path=_ipeds_dir / "pellgradrates.csv",
        description="Graduation rates for overall and Pell students",
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

    PELL_GRAD_RATE_FOUR = DataSourceConfig(
        path=_processed_dir / "pell_grad_rate_scatter_four_year.csv",
        description="Pell graduation rate scatter (4-year)",
        required=False
    )

    PELL_GRAD_RATE_TWO = DataSourceConfig(
        path=_processed_dir / "pell_grad_rate_scatter_two_year.csv",
        description="Pell graduation rate scatter (2-year)",
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

    # Canonical IPEDS graduation outputs
    CANONICAL_GRAD_LONG = DataSourceConfig(
        path=_canonical_dir / "ipeds_grad_rates_long.parquet",
        description="Canonical IPEDS graduation rates (long format)",
        required=False,
    )

    CANONICAL_GRAD_LATEST = DataSourceConfig(
        path=_canonical_dir / "ipeds_grad_rates_latest_by_inst.parquet",
        description="Canonical IPEDS graduation rates (latest per institution)",
        required=False,
    )

    CANONICAL_GRAD_SUMMARY = DataSourceConfig(
        path=_canonical_dir / "ipeds_grad_rates_summary_by_year.parquet",
        description="Canonical IPEDS graduation rates summary by year/sector",
        required=False,
    )

    CANONICAL_PELL_LONG = DataSourceConfig(
        path=_canonical_dir / "ipeds_percent_pell_long.parquet",
        description="Canonical percent Pell (long)",
        required=False,
    )

    CANONICAL_PELL_SUMMARY = DataSourceConfig(
        path=_canonical_dir / "ipeds_percent_pell_summary_by_year.parquet",
        description="Canonical percent Pell summary",
        required=False,
    )

    CANONICAL_LOANS_LONG = DataSourceConfig(
        path=_canonical_dir / "ipeds_percent_loans_long.parquet",
        description="Canonical percent federal loans (long)",
        required=False,
    )

    CANONICAL_LOANS_SUMMARY = DataSourceConfig(
        path=_canonical_dir / "ipeds_percent_loans_summary_by_year.parquet",
        description="Canonical percent federal loans summary",
        required=False,
    )

    CANONICAL_RETENTION_LONG = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_full_time_long.parquet",
        description="Canonical IPEDS retention cohorts (full-time) long",
        required=False,
    )

    CANONICAL_RETENTION_LATEST = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_full_time_latest_by_inst.parquet",
        description="Canonical IPEDS retention cohorts latest per institution",
        required=False,
    )

    CANONICAL_RETENTION_SUMMARY = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_full_time_summary_by_year.parquet",
        description="Canonical IPEDS retention cohorts summary by year",
        required=False,
    )

    CANONICAL_RETENTION_RATE_LONG = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_rate_full_time_long.parquet",
        description="Canonical IPEDS retention rate (full-time) long",
        required=False,
    )

    CANONICAL_RETENTION_RATE_LATEST = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_rate_full_time_latest_by_inst.parquet",
        description="Canonical IPEDS retention rate latest per institution",
        required=False,
    )

    CANONICAL_RETENTION_RATE_SUMMARY = DataSourceConfig(
        path=_canonical_dir / "ipeds_retention_rate_full_time_summary_by_year.parquet",
        description="Canonical IPEDS retention rate summary by year",
        required=False,
    )

    # ROI data sources - epanalysis migration
    ROI_METRICS_RAW = DataSourceConfig(
        path=_epanalysis_dir / "roi-metrics.csv",
        description="ROI metrics from epanalysis (116 CA institutions)",
        required=False
    )

    ROI_METRICS_PARQUET = DataSourceConfig(
        path=_processed_dir / "roi_metrics.parquet",
        description="Processed ROI metrics (116 CA institutions, Parquet)",
        required=False
    )

    OPEID_MAPPING = DataSourceConfig(
        path=_epanalysis_dir / "opeid_unitid_mapping.csv",
        description="OPEID to UnitID mapping for CA institutions",
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
            "grad_rate_four": cls.PELL_GRAD_RATE_FOUR,
            "grad_rate_two": cls.PELL_GRAD_RATE_TWO,
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
            "pell_grad_rate_four": cls.PELL_GRAD_RATE_FOUR,
            "pell_grad_rate_two": cls.PELL_GRAD_RATE_TWO,
            "tuition_vs_grad": cls.TUITION_VS_GRAD,
            "tuition_vs_grad_parquet": cls.TUITION_VS_GRAD_PARQUET,
            "tuition_vs_grad_two": cls.TUITION_VS_GRAD_TWO,
            "tuition_vs_grad_two_parquet": cls.TUITION_VS_GRAD_TWO_PARQUET,
            "distance_raw": cls.DISTANCE_RAW,
            "pell_grad_rates_raw": cls.PELL_GRAD_RATES_RAW,
            "retention_rate_pct_raw": cls.RETENTION_RATE_PCT_RAW,
            "roi_metrics_raw": cls.ROI_METRICS_RAW,
            "roi_metrics_parquet": cls.ROI_METRICS_PARQUET,
            "opeid_mapping": cls.OPEID_MAPPING,
            "canonical_retention_long": cls.CANONICAL_RETENTION_LONG,
            "canonical_retention_latest": cls.CANONICAL_RETENTION_LATEST,
            "canonical_retention_summary": cls.CANONICAL_RETENTION_SUMMARY,
            "canonical_retention_rate_long": cls.CANONICAL_RETENTION_RATE_LONG,
            "canonical_retention_rate_latest": cls.CANONICAL_RETENTION_RATE_LATEST,
            "canonical_retention_rate_summary": cls.CANONICAL_RETENTION_RATE_SUMMARY,
        }
