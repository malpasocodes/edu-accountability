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

        # Main title
        st.title("Distance Education: Analyzing Online Learning Patterns")

        # Key insight callout
        st.info("**💡 Key Insight:** Distance education data reveals how institutions are adapting to online learning, showing enrollment patterns from the COVID-19 era through 2024 and which schools lead in online program delivery.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is Distance Education Analysis?")
        st.markdown(
            """
            This section tracks **distance education enrollment** at colleges and universities across the United States.
            The data covers **2020-2024** and categorizes students into three groups:

            - **Exclusively Distance Education**: Students taking all courses online
            - **Some Distance Education**: Students in hybrid programs mixing online and in-person
            - **No Distance Education**: Students in traditional in-person programs only

            Understanding these patterns helps illuminate how higher education delivery has evolved, particularly
            during and after the COVID-19 pandemic, and which institutions are leading in online education.
            """
        )

        st.divider()

        # Available analyses section
        st.markdown("### Three Ways to Explore Distance Education Data")
        st.markdown(
            """
            Use the **sidebar charts** to examine distance education patterns from different angles. Each analysis
            is available for both 4-year and 2-year institutions:
            """
        )

        st.markdown("")  # Spacing

        # Three analysis types in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; background-color: #fffaf5; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #ff7f0e; margin-bottom: 0.5rem;'>📊 Top 25 Distance Education Enrollment</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>See which institutions have the highest distance education enrollment.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Stacked bars show exclusive, some, and no distance education.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f8faff; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>📈 Total Enrollment Trend</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Track overall enrollment changes from 2020-2024.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Shows year-over-year enrollment patterns for top institutions.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #2ca02c; margin-bottom: 0.5rem;'>📉 Distance Education Trend</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Track exclusive distance education enrollment over time.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Shows how online-only enrollment evolved 2020-2024.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # How to use section
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Start with Top 25 Distance Education Enrollment** to identify institutions with the largest online presence.
            Then explore the **Total Enrollment Trend** to see how overall student populations changed during the pandemic period.
            Finally, use the **Distance Education Trend** to track the specific growth of exclusively online programs.

            **Each chart includes tabs** at the top for 4-year and 2-year institutions, allowing you to compare
            patterns across different institutional types.
            """
        )

        st.divider()

        # What to look for section
        st.markdown("### What the Data Shows")
        st.markdown(
            """
            Distance education data reveals important patterns about online learning adoption:

            - **High distance education enrollment** indicates institutional commitment to online delivery
            - **COVID-19 impact** is visible in 2020-2021 shifts toward online learning
            - **Post-pandemic patterns** show whether online enrollment sustained or returned to pre-pandemic levels
            - **Institutional differences** emerge between traditional colleges and online-focused institutions
            """
        )

        st.divider()

        # Data disclaimer
        st.markdown("### Data Source & Notes")
        st.info(
            "**Data Source:** IPEDS Distance Education surveys, 2020-2024. "
            "Enrollment data includes breakdowns by distance education participation level (exclusive, some, none). "
            "Data reflects fall enrollment snapshots for each year."
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