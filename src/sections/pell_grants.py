"""Pell Grants section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from src.charts.pell_top_dollars_chart import render_pell_top_dollars_chart
from src.charts.pell_vs_grad_scatter_chart import render_pell_vs_grad_scatter
from src.charts.pell_trend_chart import render_pell_trend_chart
from src.config.constants import (
    PELL_SECTION,
    PELL_OVERVIEW_LABEL,
    PELL_TOP_DOLLARS_FOUR_LABEL,
    PELL_TOP_DOLLARS_TWO_LABEL,
    PELL_VS_GRAD_FOUR_LABEL,
    PELL_VS_GRAD_TWO_LABEL,
    PELL_TREND_FOUR_LABEL,
    PELL_TREND_TWO_LABEL,
    PELL_CHARTS,
)
from src.ui.renderers import render_dataframe
from .base import BaseSection


class PellGrantsSection(BaseSection):
    """Handles the Pell Grants section."""
    
    def render_overview(self) -> None:
        """Render the Pell Grants overview."""
        self.render_section_header(PELL_SECTION, PELL_OVERVIEW_LABEL)
        
        st.markdown(
            """
            Review Pell Grant distributions to understand where need-based aid concentrates. Use
            the chart buttons to spotlight top recipients, examine graduation relationships, and
            trace award trends across institutional sectors.
            """
        )
        st.info(
            "Pell figures come from processed extracts in this repository. Refresh the "
            "underlying data before publishing new findings."
        )
    
    def render_chart(self, chart_name: str) -> None:
        """Render a specific Pell Grants chart."""
        self.render_section_header(PELL_SECTION, chart_name)
        
        if chart_name == PELL_TOP_DOLLARS_FOUR_LABEL:
            self._render_pell_top_dollars("top_four", chart_name)
        elif chart_name == PELL_TOP_DOLLARS_TWO_LABEL:
            self._render_pell_top_dollars("top_two", chart_name)
        elif chart_name == PELL_VS_GRAD_FOUR_LABEL:
            self._render_pell_vs_grad("scatter_four", "four_year", chart_name)
        elif chart_name == PELL_VS_GRAD_TWO_LABEL:
            self._render_pell_vs_grad("scatter_two", "two_year", chart_name)
        elif chart_name == PELL_TREND_FOUR_LABEL:
            self._render_pell_trend("trend_four", chart_name)
        elif chart_name == PELL_TREND_TWO_LABEL:
            self._render_pell_trend("trend_two", chart_name)
        else:
            st.info(
                f"{chart_name} will be available in a later phase. Until then, preview the "
                "underlying Pell dataset below."
            )
            if self.data_manager.pell_df is not None:
                render_dataframe(self.data_manager.pell_df.head(20), width="stretch")
    
    def _render_pell_top_dollars(self, resource_key: str, title: str) -> None:
        """Render Pell top dollars chart."""
        dataset = self.data_manager.get_pell_resource(resource_key)
        if dataset is not None:
            render_pell_top_dollars_chart(dataset, top_n=25, title=title)
        else:
            sector = "four-year" if "four" in resource_key else "two-year"
            st.warning(
                f"Missing processed dataset for {sector} institutions. "
                "Run `python data/processed/build_pell_top_dollars.py` to regenerate."
            )
    
    def _render_pell_vs_grad(self, resource_key: str, sector: str, title: str) -> None:
        """Render Pell vs graduation chart."""
        dataset = self.data_manager.get_pell_resource(resource_key)
        if dataset is not None:
            metadata = self.data_manager.get_metadata_for_sector(sector)
            if metadata is not None:
                render_pell_vs_grad_scatter(
                    dataset,
                    title=title,
                    metadata_df=metadata,
                )
            else:
                st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
        else:
            sector_label = "4-year" if "four" in resource_key else "2-year"
            st.warning(
                f"Pell vs graduation dataset ({sector_label}) not found. "
                "Run `python data/processed/build_pell_vs_grad_scatter.py` to generate it."
            )
    
    def _render_pell_trend(self, resource_key: str, title: str) -> None:
        """Render Pell trend chart."""
        dataset = self.data_manager.get_pell_resource(resource_key)
        if dataset is not None:
            render_pell_trend_chart(dataset, title=title)
        else:
            sector = "4-year" if "four" in resource_key else "2-year"
            st.warning(
                f"Pell trend dataset ({sector}) not found. "
                "Run `python data/processed/build_pell_top_dollars.py` to regenerate."
            )
    
    def get_available_charts(self) -> List[str]:
        """Get available charts for Pell Grants section."""
        return PELL_CHARTS