"""Pell Grants section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from src.charts.pell_top_dollars_chart import render_pell_top_dollars_chart
from src.charts.pell_vs_grad_scatter_chart import render_pell_vs_grad_scatter
from src.charts.pell_trend_chart import render_pell_trend_chart
from src.charts.pell_trend_total_chart import render_pell_trend_total_chart
from src.charts.pell_grad_rate_scatter_chart import render_pell_grad_rate_scatter
from src.config.constants import (
    PELL_SECTION,
    PELL_OVERVIEW_LABEL,
    PELL_TOP_DOLLARS_LABEL,
    PELL_VS_GRAD_LABEL,
    PELL_TREND_LABEL,
    PELL_TREND_TOTAL_LABEL,
    PELL_GRAD_RATE_LABEL,
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

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    🎯 Pell Grants Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Examine where need-based aid concentrates and how those grants connect to student success.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Key insight callout
        st.info("**💡 Key Insight:** Pell Grant data shows where need-based federal aid concentrates, revealing which institutions serve the most low-income students and how grant patterns relate to student outcomes.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is Pell Grants Analysis?")
        st.markdown(
            """
            This section tracks **Pell Grant dollars** awarded to students at colleges and universities across
            the United States. The data covers **2008-2022** and shows which institutions serve the most low-income
            students, how grant aid relates to graduation rates, and how need-based aid patterns have evolved over time.

            Pell Grants are the federal government's primary need-based aid program for undergraduate students.
            Understanding where these dollars flow helps illuminate access for low-income students and institutional
            commitment to serving economically disadvantaged populations.
            """
        )

        st.divider()

        # Available analyses section
        st.markdown("### Four Ways to Explore Pell Grant Data")
        st.markdown(
            """
            Use the **sidebar charts** to examine Pell Grant patterns from different angles. Each analysis
            is available for both 4-year and 2-year institutions:
            """
        )

        st.markdown("")  # Spacing

        # Four analysis types in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #9467bd; border-radius: 10px; background-color: #faf9ff; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #9467bd; margin-bottom: 0.75rem;'>📊 Top 25 Pell Dollar Recipients</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>See which institutions receive the most Pell Grant dollars.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Stacked bars show yearly breakdown (2008-2022).</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #2ca02c; margin-bottom: 0.75rem;'>📈 Pell Dollars vs Graduation Rate</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>Compare Pell volumes against graduation outcomes.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Bubble size shows enrollment scale.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; background-color: #fffaf5; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #ff7f0e; margin-bottom: 0.75rem;'>📉 Pell Dollars Trend (Top 10)</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>Track how Pell volumes change over time for top 10 institutions.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Shows year-over-year patterns and shifts.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #9467bd; border-radius: 10px; background-color: #faf8ff; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #9467bd; margin-bottom: 0.75rem;'>📊 Pell Dollars Trend (Total)</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>See aggregate Pell grant dollar totals summed across all institutions per year.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Shows overall aid patterns and national trends (2008-2022).</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # How to use section
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Start with Top 25 Pell Dollar Recipients** to identify institutions serving the most low-income students.
            Then explore the **vs Graduation Rate** chart to see how need-based aid concentrations relate to student outcomes.
            Finally, use the **Trend** chart to understand how these patterns have evolved over the past 15 years.

            **Each chart includes tabs** at the top for 4-year and 2-year institutions, allowing you to compare
            patterns across different institutional types.
            """
        )

        st.divider()

        # What to look for section
        st.markdown("### What the Data Shows")
        st.markdown(
            """
            Pell Grant data reveals important patterns about access and equity:

            - **High Pell volumes** indicate institutions serving large numbers of low-income students
            - **Pell vs graduation trends** show whether aid concentration aligns with degree completion
            - **Multi-year patterns** reveal how institutions' commitment to low-income access has shifted
            - **Sector differences** emerge between public, private nonprofit, and for-profit colleges
            """
        )

        st.divider()

        # Data disclaimer
        st.markdown("### Data Source & Notes")
        st.info(
            "**Data Source:** IPEDS (Integrated Postsecondary Education Data System), 2008-2022. "
            "Pell totals reflect annual grant dollars awarded to students at each institution. "
            "For high-stakes decisions, validate against the latest Department of Education releases."
        )
    
    def render_chart(self, chart_name: str) -> None:
        """Render a specific Pell Grants chart."""
        self.render_section_header(PELL_SECTION, chart_name)

        # Handle consolidated chart names with tabs
        if chart_name == PELL_TOP_DOLLARS_LABEL:
            self._render_pell_top_dollars_with_tabs(chart_name)
        elif chart_name == PELL_VS_GRAD_LABEL:
            self._render_pell_vs_grad_with_tabs(chart_name)
        elif chart_name == PELL_TREND_LABEL:
            self._render_pell_trend_with_tabs(chart_name)
        elif chart_name == PELL_TREND_TOTAL_LABEL:
            self._render_pell_trend_total_with_tabs(chart_name)
        elif chart_name == PELL_GRAD_RATE_LABEL:
            self._render_pell_grad_rate_with_tabs(chart_name)
        # Handle individual chart names for backward compatibility
        elif chart_name == PELL_TOP_DOLLARS_FOUR_LABEL:
            self._render_pell_top_dollars("four_year", chart_name)
        elif chart_name == PELL_TOP_DOLLARS_TWO_LABEL:
            self._render_pell_top_dollars("two_year", chart_name)
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
    
    def _render_pell_top_dollars(self, sector: str, title: str) -> None:
        """Render Pell top dollars chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None and self.data_manager.pell_df is not None:
            render_pell_top_dollars_chart(
                self.data_manager.pell_df,
                metadata,
                top_n=25,
                title=title
            )
        else:
            if metadata is None:
                st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
            else:
                st.error("Missing raw Pell data.")
    
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
    
    def _render_pell_top_dollars_with_tabs(self, title: str) -> None:
        """Render Pell top dollars chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_pell_top_dollars("four_year", f"{title} (4-year)")

        with tab2:
            self._render_pell_top_dollars("two_year", f"{title} (2-year)")
    
    def _render_pell_vs_grad_with_tabs(self, title: str) -> None:
        """Render Pell vs graduation chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])
        
        with tab1:
            self._render_pell_vs_grad("scatter_four", "four_year", f"{title} (4-year)")
        
        with tab2:
            self._render_pell_vs_grad("scatter_two", "two_year", f"{title} (2-year)")
    
    def _render_pell_trend_with_tabs(self, title: str) -> None:
        """Render Pell trend chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_pell_trend("trend_four", f"{title} (4-year)")

        with tab2:
            self._render_pell_trend("trend_two", f"{title} (2-year)")

    def _render_pell_trend_total_with_tabs(self, title: str) -> None:
        """Render total Pell trend chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_pell_trend_total("four_year", f"{title} (4-year)")

        with tab2:
            self._render_pell_trend_total("two_year", f"{title} (2-year)")

    def _render_pell_trend_total(self, sector: str, title: str) -> None:
        """Render total Pell trend chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_pell_trend_total_chart(
                self.data_manager.pell_df,
                metadata,
                title=title,
                sector=sector,
            )
        else:
            st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")

    def _render_pell_grad_rate_with_tabs(self, title: str) -> None:
        """Render Pell graduation rate scatter chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_pell_grad_rate("grad_rate_four", "four_year", f"{title} (4-year)")

        with tab2:
            self._render_pell_grad_rate("grad_rate_two", "two_year", f"{title} (2-year)")

    def _render_pell_grad_rate(self, resource_key: str, sector: str, title: str) -> None:
        """Render Pell graduation rate scatter chart."""
        dataset = self.data_manager.get_pell_resource(resource_key)
        if dataset is not None:
            metadata = self.data_manager.get_metadata_for_sector(sector)
            if metadata is not None:
                render_pell_grad_rate_scatter(
                    dataset,
                    title=title,
                    metadata_df=metadata,
                )
            else:
                st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")
        else:
            sector_label = "4-year" if "four" in resource_key else "2-year"
            st.warning(
                f"Pell graduation rate dataset ({sector_label}) not found. "
                "Run `python data/processed/build_pell_grad_rate_scatter.py` to generate it."
            )
    
    def get_available_charts(self) -> List[str]:
        """Get available charts for Pell Grants section."""
        return PELL_CHARTS
