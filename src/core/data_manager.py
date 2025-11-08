"""Central data management for the dashboard."""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import re

import pandas as pd
import streamlit as st

from src.config.constants import (
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    VALUE_GRID_CHART_CONFIGS,
)
from src.config.data_sources import DataSources
from src.config.feature_flags import USE_CANONICAL_GRAD_DATA
from src.data.datasets import load_processed
from .data_loader import DataLoader
from .exceptions import DataLoadError


class DataManager:
    """Manages all data loading and caching for the dashboard."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.loader = DataLoader()
        self.pell_df: Optional[pd.DataFrame] = None
        self.loan_df: Optional[pd.DataFrame] = None
        self.distance_df: Optional[pd.DataFrame] = None
        self.institutions_df: Optional[pd.DataFrame] = None
        self.pellgradrates_df: Optional[pd.DataFrame] = None
        self.roi_df: Optional[pd.DataFrame] = None
        self.value_grid_datasets: Dict[str, pd.DataFrame] = {}
        self.pell_resources: Dict[str, Optional[pd.DataFrame]] = {}
        self.canonical_grad_df: Optional[pd.DataFrame] = None
        self.headcount_df: Optional[pd.DataFrame] = None
        self.headcount_fallback_map: Optional[pd.Series] = None
        self.errors: list[str] = []
    
    def load_all_data(self) -> None:
        """
        Load all required and optional datasets.
        
        This method loads data in priority order:
        1. Required raw datasets (Pell)
        2. Optional raw datasets (Loans)  
        3. Processed value grid datasets
        4. Processed Pell datasets
        """
        self.errors.clear()
        
        # Load required raw datasets
        self._load_pell_raw()
        self._load_loan_raw()
        self._load_distance_raw()
        self._load_institutions_raw()
        self._load_pellgradrates_raw()
        self._load_headcount_data()
        self._load_canonical_grad_data()

        # Load value grid datasets
        self._load_value_grid_datasets()
        
        # Load processed Pell datasets
        self._load_pell_processed_datasets()
    
    def _load_pell_raw(self) -> None:
        """Load the raw Pell dataset."""
        try:
            self.pell_df = self.loader.load_csv(
                str(DataSources.PELL_RAW.path),
                DataSources.PELL_RAW.description
            )
        except DataLoadError as e:
            self.errors.append(str(e))
            raise
    
    def _load_loan_raw(self) -> None:
        """Load the raw loan dataset (optional)."""
        try:
            self.loan_df = self.loader.load_csv(
                str(DataSources.LOAN_RAW.path),
                DataSources.LOAN_RAW.description
            )
        except DataLoadError:
            # Loan data is optional
            self.loan_df = pd.DataFrame()

    def _load_distance_raw(self) -> None:
        """Load the raw distance education dataset (optional)."""
        try:
            self.distance_df = self.loader.load_csv(
                str(DataSources.DISTANCE_RAW.path),
                DataSources.DISTANCE_RAW.description
            )
        except DataLoadError:
            # Distance education data is optional
            self.distance_df = pd.DataFrame()

    def _load_institutions_raw(self) -> None:
        """Load the raw institutions dataset."""
        try:
            self.institutions_df = self.loader.load_csv(
                str(DataSources.INSTITUTIONS_RAW.path),
                DataSources.INSTITUTIONS_RAW.description
            )
        except DataLoadError as e:
            # Institutions data is important for College Explorer
            self.errors.append(f"Failed to load institutions data: {str(e)}")
            self.institutions_df = pd.DataFrame()

    def _load_pellgradrates_raw(self) -> None:
        """Load the raw Pell graduation rates dataset (optional)."""
        try:
            self.pellgradrates_df = self.loader.load_csv(
                str(DataSources.PELL_GRAD_RATES_RAW.path),
                DataSources.PELL_GRAD_RATES_RAW.description
            )
        except DataLoadError:
            # Pell graduation rates data is optional
            self.pellgradrates_df = pd.DataFrame()

    def _load_headcount_data(self) -> None:
        """Load undergraduate headcount information used for z-score filtering."""

        ft_ug_headcount = self._load_ft_ug_12month_headcount()
        fallback_series = self._build_enrollment_headcount_fallback()

        if ft_ug_headcount.empty:
            if fallback_series is None:
                self.headcount_df = pd.DataFrame()
            else:
                self.headcount_df = pd.DataFrame(
                    columns=["unitid", "year", "ft_ug_headcount", "headcount_source"]
                )
            self.headcount_fallback_map = fallback_series
            return

        if fallback_series is not None:
            ft_ug_headcount["fallback_headcount"] = ft_ug_headcount["unitid"].map(
                fallback_series
            )
        else:
            ft_ug_headcount["fallback_headcount"] = np.nan

        self.headcount_df = ft_ug_headcount
        self.headcount_fallback_map = fallback_series

    def _load_ft_ug_12month_headcount(self) -> pd.DataFrame:
        """Load the 12-month FT undergraduate unduplicated headcount file."""

        source = DataSources.FT_UG_HEADCOUNT_RAW
        path = source.path
        if not path.exists():
            return pd.DataFrame()

        try:
            raw = self.loader.load_csv(str(path), source.description)
        except DataLoadError:
            return pd.DataFrame()

        id_vars = ["UnitID", "Institution Name"]
        columns = [col for col in raw.columns if col not in id_vars and col.strip()]

        pattern = re.compile(r"\(DRVEF12(\d{4})(?:_RV)?\)")
        records: list[pd.DataFrame] = []

        for column in columns:
            match = pattern.search(column)
            if not match:
                continue
            year = int(match.group(1))
            temp = raw[id_vars + [column]].copy()
            temp["year"] = year
            temp["ft_ug_headcount"] = pd.to_numeric(temp[column], errors="coerce")
            records.append(temp[["UnitID", "Institution Name", "year", "ft_ug_headcount"]])

        if not records:
            return pd.DataFrame()

        long_df = pd.concat(records, ignore_index=True)
        long_df = long_df.dropna(subset=["ft_ug_headcount"])
        long_df.rename(
            columns={
                "UnitID": "unitid",
                "Institution Name": "instnm",
            },
            inplace=True,
        )
        long_df["headcount_source"] = "FT_UG_12M"
        return long_df

    def _build_enrollment_headcount_fallback(self) -> Optional[pd.Series]:
        """Create fallback headcounts from fall enrollment data."""

        try:
            enrollment_df = self.loader.load_csv(
                str(DataSources.ENROLLMENT_RAW.path),
                DataSources.ENROLLMENT_RAW.description,
            )
        except DataLoadError:
            return None

        working = enrollment_df.copy()
        working.rename(columns={"UnitID": "unitid"}, inplace=True)
        for column in ("ENR_UG", "ENR_TOTAL"):
            if column in working.columns:
                working[column] = pd.to_numeric(working[column], errors="coerce")

        working["fallback_headcount"] = working["ENR_UG"].where(
            working["ENR_UG"].notna(), working["ENR_TOTAL"]
        )

        fallback = working[["unitid", "fallback_headcount"]].dropna()
        if fallback.empty:
            return None

        series = fallback.set_index("unitid")["fallback_headcount"]
        series = series.astype("float32")
        return series

    def _load_canonical_grad_data(self) -> None:
        """Load canonical graduation datasets when enabled."""

        if not USE_CANONICAL_GRAD_DATA:
            self.canonical_grad_df = pd.DataFrame()
            return

        canonical_source = DataSources.CANONICAL_GRAD_LATEST
        try:
            self.canonical_grad_df = self.loader.load_parquet(
                str(canonical_source.path),
                canonical_source.description,
            )
        except DataLoadError:
            self.canonical_grad_df = pd.DataFrame()
            self.errors.append(
                "Canonical graduation data is enabled but could not be loaded."
            )

    def _load_value_grid_datasets(self) -> None:
        """Load value grid datasets using existing load_processed function."""
        for config in VALUE_GRID_CHART_CONFIGS:
            try:
                self.value_grid_datasets[config.label] = load_processed(
                    config.dataset_key
                )
            except FileNotFoundError as e:
                error_msg = f"Missing processed dataset for {config.label}"
                self.errors.append(error_msg)
                raise DataLoadError(error_msg) from e
    
    def _load_pell_processed_datasets(self) -> None:
        """Load all processed Pell datasets."""
        pell_sources = DataSources.get_pell_resources_map()
        
        # Raw data is already loaded
        self.pell_resources["raw"] = self.pell_df
        
        # Load optional processed datasets
        optional_sources = {
            "top_all": DataSources.PELL_TOP_DOLLARS,
            "top_four": DataSources.PELL_TOP_DOLLARS_FOUR,
            "top_two": DataSources.PELL_TOP_DOLLARS_TWO,
            "trend_four": DataSources.PELL_TREND_FOUR,
            "trend_two": DataSources.PELL_TREND_TWO,
            "scatter_all": DataSources.PELL_VS_GRAD,
            "scatter_four": DataSources.PELL_VS_GRAD_FOUR,
            "scatter_two": DataSources.PELL_VS_GRAD_TWO,
            "grad_rate_four": DataSources.PELL_GRAD_RATE_FOUR,
            "grad_rate_two": DataSources.PELL_GRAD_RATE_TWO,
        }
        
        for key, source in optional_sources.items():
            self.pell_resources[key] = self.loader.load_optional_csv(
                source.path,
                source.description
            )
    
    def get_value_grid_dataset(self, label: str) -> Optional[pd.DataFrame]:
        """Get a value grid dataset by label."""
        return self.value_grid_datasets.get(label)
    
    def get_pell_resource(self, key: str) -> Optional[pd.DataFrame]:
        """Get a Pell resource by key."""
        return self.pell_resources.get(key)

    def get_distance_data(self) -> Optional[pd.DataFrame]:
        """Get the distance education dataset."""
        return self.distance_df
    
    def get_metadata_for_sector(
        self, 
        sector: str
    ) -> Optional[pd.DataFrame]:
        """
        Get metadata DataFrame for a given sector.
        
        Args:
            sector: Either "four_year" or "two_year"
            
        Returns:
            DataFrame with metadata for the sector
        """
        if sector == "four_year":
            return self.value_grid_datasets.get(FOUR_YEAR_VALUE_GRID_LABEL)
        elif sector == "two_year":
            return self.value_grid_datasets.get(TWO_YEAR_VALUE_GRID_LABEL)
        return None
    
    def has_errors(self) -> bool:
        """Check if any errors occurred during loading."""
        return len(self.errors) > 0
    
    def get_errors(self) -> list[str]:
        """Get list of errors that occurred during loading."""
        return self.errors.copy()
    
    def display_errors(self) -> None:
        """Display any loading errors in the Streamlit sidebar."""
        if self.has_errors():
            for error in self.errors:
                st.sidebar.error(error)

    @st.cache_data(ttl=3600)
    def load_roi_metrics(_self) -> pd.DataFrame:
        """
        Load ROI metrics for California institutions.

        This is a cached method that loads the processed ROI dataset
        from epanalysis migration.

        Returns:
            DataFrame with ROI data for 116 CA institutions
        """
        try:
            roi_df = pd.read_parquet('data/processed/roi_metrics.parquet')
            return roi_df
        except FileNotFoundError:
            st.warning("ROI data not available. Run `python src/data/build_roi_metrics.py` to generate.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading ROI data: {e}")
            return pd.DataFrame()

    def get_institution_roi(self, unit_id: int) -> Optional[pd.Series]:
        """
        Get ROI metrics for a specific institution.

        Args:
            unit_id: IPEDS UnitID

        Returns:
            Series with ROI data if available, None if institution not in CA ROI dataset
        """
        if self.roi_df is None:
            self.roi_df = self.load_roi_metrics()

        if self.roi_df.empty:
            return None

        institution_roi = self.roi_df[self.roi_df['UnitID'] == unit_id]

        if institution_roi.empty:
            return None

        return institution_roi.iloc[0]
