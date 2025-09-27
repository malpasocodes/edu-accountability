"""Value Grid section implementation."""

from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter
from src.config.constants import (
    VALUE_GRID_CONFIG_MAP,
    VALUE_GRID_OVERVIEW_LABEL,
    VALUE_GRID_SECTION,
)
from src.core.data_loader import DataLoader
from .base import BaseSection


class ValueGridSection(BaseSection):
    """Handles the College Value Grid section."""
    
    def render_overview(self) -> None:
        """Render the Value Grid overview."""
        self.render_section_header(VALUE_GRID_SECTION, VALUE_GRID_OVERVIEW_LABEL)
        
        st.markdown(
            """
            Start with the value grid to see how net price aligns with completion among
            high-enrollment institutions. Use the buttons in the sidebar to switch between
            four-year and two-year comparisons once you're ready to dive into the data.
            """
        )
        st.info(
            "Tip: Refresh processed datasets in `data/processed/` before generating new "
            "value grid exports so median benchmarks stay up to date."
        )
    
    def render_chart(self, chart_name: str) -> None:
        """Render a specific Value Grid chart."""
        self.render_section_header(VALUE_GRID_SECTION, chart_name)
        
        config = VALUE_GRID_CONFIG_MAP.get(chart_name)
        if config is None:
            st.error("Select a value grid view from the sidebar to load a chart.")
            return
        
        dataset = self.data_manager.get_value_grid_dataset(config.label)
        if dataset is None:
            st.error("Unable to locate dataset for the selected chart.")
            return
        
        self._render_value_grid_chart(config.label, dataset, config.min_enrollment)
    
    def _render_value_grid_chart(
        self, 
        label: str, 
        dataset: pd.DataFrame, 
        min_enrollment: int
    ) -> None:
        """Internal method to render the value grid chart."""
        columns_needed = {"institution", "sector", "cost", "graduation_rate"}
        missing = [column for column in columns_needed if column not in dataset.columns]
        if missing:
            st.error(
                "Cannot render cost vs graduation chart. Missing columns: " + ", ".join(missing)
            )
            return
        
        prepared = DataLoader.prepare_value_grid_dataset(label, dataset)
        
        if min_enrollment > 0 and "enrollment" in prepared.columns:
            filtered = prepared[prepared["enrollment"] >= min_enrollment]
        else:
            filtered = prepared
        
        filtered = filtered.dropna(subset=["cost", "graduation_rate"])
        if filtered.empty:
            st.warning("No institutions meet the current baseline criteria.")
            return
        
        cost_median = float(prepared["cost"].dropna().median())
        grad_median = float(prepared["graduation_rate"].dropna().median())
        
        render_cost_vs_grad_scatter(
            filtered,
            min_enrollment=min_enrollment,
            global_cost_median=cost_median,
            global_grad_median=grad_median,
            group_label=label,
        )
    
    def get_available_charts(self) -> List[str]:
        """Get available charts for Value Grid section."""
        return list(VALUE_GRID_CONFIG_MAP.keys())