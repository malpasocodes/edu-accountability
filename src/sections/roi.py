"""ROI section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection


class ROISection(BaseSection):
    """Handles the ROI section."""

    def render_overview(self) -> None:
        """Render the ROI overview."""
        self.render_section_header("ROI", "Overview")

        st.markdown("## Coming Soon")
        st.info("The ROI (Return on Investment) section is under development.")

    def render_chart(self, chart_name: str) -> None:
        """Render a specific ROI chart."""
        self.render_section_header("ROI", chart_name)
        st.info("This chart is coming soon.")

    def get_available_charts(self) -> List[str]:
        """Get available charts for ROI section."""
        return []
