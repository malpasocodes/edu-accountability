"""Data loading utilities with caching support."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from .exceptions import DataLoadError


class DataLoader:
    """Handles loading and caching of datasets."""
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_csv(path_str: str, description: str = "") -> pd.DataFrame:
        """
        Load a CSV file with Streamlit caching.
        
        Args:
            path_str: String path to the CSV file
            description: Optional description for error messages
            
        Returns:
            Loaded DataFrame
            
        Raises:
            DataLoadError: If the file cannot be loaded
        """
        path = Path(path_str)
        if not path.exists():
            error_msg = f"Dataset not found at {path}"
            if description:
                error_msg = f"{description} not found at {path}"
            raise DataLoadError(error_msg)
        
        try:
            return pd.read_csv(path)
        except Exception as e:
            error_msg = f"Failed to load CSV from {path}: {e}"
            if description:
                error_msg = f"Failed to load {description}: {e}"
            raise DataLoadError(error_msg) from e
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def load_parquet(path_str: str, description: str = "") -> pd.DataFrame:
        """
        Load a Parquet file with Streamlit caching.
        
        Args:
            path_str: String path to the Parquet file
            description: Optional description for error messages
            
        Returns:
            Loaded DataFrame
            
        Raises:
            DataLoadError: If the file cannot be loaded
        """
        path = Path(path_str)
        if not path.exists():
            error_msg = f"Parquet file not found at {path}"
            if description:
                error_msg = f"{description} not found at {path}"
            raise DataLoadError(error_msg)
        
        try:
            return pd.read_parquet(path)
        except Exception as e:
            error_msg = f"Failed to load Parquet from {path}: {e}"
            if description:
                error_msg = f"Failed to load {description}: {e}"
            raise DataLoadError(error_msg) from e
    
    @staticmethod
    def load_optional_csv(
        path: Path, 
        description: str = ""
    ) -> Optional[pd.DataFrame]:
        """
        Try to load a CSV file, returning None if it doesn't exist.
        
        Args:
            path: Path to the CSV file
            description: Optional description for logging
            
        Returns:
            DataFrame if successful, None otherwise
        """
        if not path.exists():
            return None
        
        try:
            return DataLoader.load_csv(str(path), description)
        except DataLoadError:
            return None
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def prepare_value_grid_dataset(label: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare dataset for cost vs graduation rendering.
        
        Args:
            label: Label for cache differentiation
            df: Input DataFrame
            
        Returns:
            Prepared DataFrame with numeric columns
        """
        _ = label  # differentiate cache entries per label
        
        working = df.copy()
        
        # Convert columns to numeric types
        if "enrollment" in working.columns:
            working["enrollment"] = pd.to_numeric(
                working["enrollment"], errors="coerce"
            ).fillna(0)
        
        if "cost" in working.columns:
            working["cost"] = pd.to_numeric(
                working["cost"], errors="coerce"
            )
        
        if "graduation_rate" in working.columns:
            working["graduation_rate"] = pd.to_numeric(
                working["graduation_rate"], errors="coerce"
            )
        
        return working