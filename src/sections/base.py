"""Base class for dashboard sections."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

import streamlit as st

from src.core.data_manager import DataManager


class BaseSection(ABC):
    """Abstract base class for dashboard sections."""
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize the section.
        
        Args:
            data_manager: The data manager instance
        """
        self.data_manager = data_manager
    
    @abstractmethod
    def render_overview(self) -> None:
        """Render the overview for this section."""
        pass
    
    @abstractmethod
    def render_chart(self, chart_name: str) -> None:
        """
        Render a specific chart within this section.
        
        Args:
            chart_name: Name of the chart to render
        """
        pass
    
    @abstractmethod
    def get_available_charts(self) -> List[str]:
        """
        Get list of available charts for this section.
        
        Returns:
            List of chart names
        """
        pass
    
    def render(self, active_chart: Optional[str] = None) -> None:
        """
        Main render method for the section.
        
        Args:
            active_chart: Currently active chart, None for overview
        """
        if active_chart is None or active_chart == "Overview":
            self.render_overview()
        else:
            if active_chart in self.get_available_charts():
                self.render_chart(active_chart)
            else:
                st.error(f"Unknown chart: {active_chart}")
    
    def render_section_header(self, section_name: str, chart_name: str) -> None:
        """
        Render a standard section header.

        Args:
            section_name: Name of the section
            chart_name: Name of the current chart
        """
        st.markdown(
            f'<p style="font-size: 0.9rem; color: #808080; margin-bottom: 0.5rem;">{section_name} » {chart_name}</p>',
            unsafe_allow_html=True
        )