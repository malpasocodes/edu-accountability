"""Federal Loans section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from src.charts.loan_top_dollars_chart import render_loan_top_dollars_chart
from src.charts.loan_trend_chart import render_loan_trend_chart
from src.charts.loan_vs_grad_scatter_chart import render_loan_vs_grad_scatter
from src.config.constants import (
    FEDERAL_LOANS_SECTION,
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    LOAN_OVERVIEW_LABEL,
    LOAN_TOP_DOLLARS_FOUR_LABEL,
    LOAN_TOP_DOLLARS_TWO_LABEL,
    LOAN_VS_GRAD_FOUR_LABEL,
    LOAN_VS_GRAD_TWO_LABEL,
    LOAN_TREND_FOUR_LABEL,
    LOAN_TREND_TWO_LABEL,
    LOAN_CHARTS,
)
from .base import BaseSection


class FederalLoansSection(BaseSection):
    """Handles the Federal Loans section."""
    
    def render_overview(self) -> None:
        """Render the Federal Loans overview."""
        self.render_section_header(FEDERAL_LOANS_SECTION, LOAN_OVERVIEW_LABEL)
        
        st.markdown(
            """
            Explore how federal lending patterns shape affordability by using the chart buttons
            in the sidebar. Start with the top-dollar views to see which institutions borrow the
            most, then compare graduation outcomes or multi-year trends to understand how debt
            exposure shifts over time.
            """
        )
        st.info(
            "Reminder: Loan totals reflect processed IPEDS extracts. "
            "Validate against the latest Department of Education releases for high-stakes decisions."
        )
    
    def render_chart(self, chart_name: str) -> None:
        """Render a specific Federal Loans chart."""
        self.render_section_header(FEDERAL_LOANS_SECTION, chart_name)
        
        if self.data_manager.loan_df is None or self.data_manager.loan_df.empty:
            st.warning(
                "Loan dataset is unavailable. Confirm `data/raw/loantotals.csv` exists and reload."
            )
            return
        
        if chart_name == LOAN_TOP_DOLLARS_FOUR_LABEL:
            self._render_loan_top_dollars("four_year", chart_name)
        elif chart_name == LOAN_TOP_DOLLARS_TWO_LABEL:
            self._render_loan_top_dollars("two_year", chart_name)
        elif chart_name == LOAN_VS_GRAD_FOUR_LABEL:
            self._render_loan_vs_grad("four_year", chart_name)
        elif chart_name == LOAN_VS_GRAD_TWO_LABEL:
            self._render_loan_vs_grad("two_year", chart_name)
        elif chart_name == LOAN_TREND_FOUR_LABEL:
            self._render_loan_trend("four_year", chart_name)
        elif chart_name == LOAN_TREND_TWO_LABEL:
            self._render_loan_trend("two_year", chart_name)
    
    def _render_loan_top_dollars(self, sector: str, title: str) -> None:
        """Render loan top dollars chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_loan_top_dollars_chart(
                self.data_manager.loan_df,
                metadata,
                top_n=25,
                title=title,
            )
        else:
            st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
    
    def _render_loan_vs_grad(self, sector: str, title: str) -> None:
        """Render loan vs graduation chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_loan_vs_grad_scatter(
                self.data_manager.loan_df,
                metadata,
                title=title,
            )
        else:
            st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
    
    def _render_loan_trend(self, sector: str, title: str) -> None:
        """Render loan trend chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_loan_trend_chart(
                self.data_manager.loan_df,
                metadata,
                title=title,
            )
        else:
            st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
    
    def get_available_charts(self) -> List[str]:
        """Get available charts for Federal Loans section."""
        return LOAN_CHARTS