"""Distance Education section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from src.charts.distance_top_enrollment_chart import render_distance_top_enrollment_chart
from src.charts.distance_enrollment_trend_chart import render_distance_enrollment_trend_chart
from src.charts.distance_de_trend_chart import render_distance_de_trend_chart
from .base import BaseSection


class DistanceEducationSection(BaseSection):
    """Handles the Distance Education section."""

    def render_overview(self) -> None:
        """Render the Distance Education overview."""
        self.render_section_header("Distance Education", "Overview")

        st.markdown(
            """
            Explore how institutions are utilizing distance education delivery methods to serve students.
            These visualizations show enrollment patterns across different types of distance education
            participation: exclusive distance education, partial distance education, and traditional in-person learning.
            """
        )
        st.info(
            "Distance education data comes from IPEDS Distance Education surveys. Data includes "
            "enrollment breakdowns by institutional delivery methods from 2020-2024."
        )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Distance Education chart."""
        self.render_section_header("Distance Education", chart_name)

        # Handle chart routing
        if chart_name == "Top 25 Distance Education Enrollment":
            self._render_distance_top_enrollment_with_tabs(chart_name)
        elif chart_name == "Total Enrollment Trend":
            self._render_enrollment_trend_with_tabs(chart_name)
        elif chart_name == "Distance Education Trend":
            self._render_de_trend_with_tabs(chart_name)
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_distance_top_enrollment_with_tabs(self, title: str) -> None:
        """Render top enrollment chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_distance_top_enrollment("four_year", f"{title} (4-year)")

        with tab2:
            self._render_distance_top_enrollment("two_year", f"{title} (2-year)")

    def _render_distance_top_enrollment(self, sector: str, title: str) -> None:
        """Render distance education top enrollment chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_top_enrollment_chart(
                distance_data,
                metadata,
                top_n=25,
                title=title,
                year=2024  # Use most recent year
            )
        except Exception as e:
            st.error(f"Error rendering chart: {e}")

    def _render_enrollment_trend_with_tabs(self, title: str) -> None:
        """Render enrollment trend chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_enrollment_trend("four_year", f"{title} (4-year)")

        with tab2:
            self._render_enrollment_trend("two_year", f"{title} (2-year)")

    def _render_enrollment_trend(self, sector: str, title: str) -> None:
        """Render enrollment trend chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_enrollment_trend_chart(
                distance_data,
                metadata,
                title=title,
                top_n=10,
                anchor_year=2024
            )
        except Exception as e:
            st.error(f"Error rendering enrollment trend chart: {e}")

    def _render_de_trend_with_tabs(self, title: str) -> None:
        """Render DE trend chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_de_trend("four_year", f"{title} (4-year)")

        with tab2:
            self._render_de_trend("two_year", f"{title} (2-year)")

    def _render_de_trend(self, sector: str, title: str) -> None:
        """Render DE trend chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_de_trend_chart(
                distance_data,
                metadata,
                title=title,
                top_n=10,
                anchor_year=2024
            )
        except Exception as e:
            st.error(f"Error rendering DE trend chart: {e}")

    def get_available_charts(self) -> List[str]:
        """Get available charts for distance education section."""
        return [
            "Overview",
            "Top 25 Distance Education Enrollment",
            "Total Enrollment Trend",
            "Distance Education Trend"
        ]