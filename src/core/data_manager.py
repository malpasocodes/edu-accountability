"""Central data management for the dashboard."""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd
import streamlit as st

from src.config.constants import (
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    VALUE_GRID_CHART_CONFIGS,
)
from src.config.data_sources import DataSources
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
        self.value_grid_datasets: Dict[str, pd.DataFrame] = {}
        self.pell_resources: Dict[str, Optional[pd.DataFrame]] = {}
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