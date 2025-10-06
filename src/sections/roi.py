"""ROI section implementation - California institutions only."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection
from src.config.constants import (
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
)


class ROISection(BaseSection):
    """Handles the ROI section for California institutions."""

    def render_overview(self) -> None:
        """Render the ROI overview page."""
        self.render_section_header("ROI", "Overview")

        # Hero section
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
            <h1 style='margin: 0; color: white;'>💰 Return on Investment Analysis</h1>
            <p style='font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;'>
                Analyze earnings outcomes and investment payback for California colleges
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Key insight callout
        st.info("""
        **🎯 Key Insight**: ROI varies significantly based on local economic conditions.
        This analysis compares statewide vs county-based high school earnings baselines
        to show how geography affects perceived value.
        """)

        # What is this section
        st.markdown("## What is ROI Analysis?")
        st.markdown("""
        Return on Investment (ROI) measures **how long it takes to recoup** the cost of
        a college education through increased earnings compared to a high school baseline.

        **Formula**: `ROI (years) = Total Program Cost / Earnings Premium`

        Where:
        - **Total Program Cost** = Net price per year × program length
        - **Earnings Premium** = Graduate earnings - High school baseline earnings
        """)

        # Methodology box
        st.markdown("""
        <div style='border: 2px solid #667eea; border-radius: 8px; padding: 1.5rem;
                    background-color: #f8f9ff; margin: 1.5rem 0;'>
            <h3 style='margin-top: 0; color: #667eea;'>📊 Dual Baseline Methodology</h3>
            <p>
                This analysis uses <strong>two baseline approaches</strong>:
            </p>
            <ul>
                <li><strong>Statewide Baseline</strong>: California median HS earnings ($24,939)</li>
                <li><strong>Regional Baseline</strong>: County-specific median HS earnings</li>
            </ul>
            <p>
                Comparing these reveals how local economic conditions impact ROI rankings.
                An institution in a high-wage county may show better ROI using regional baseline.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Data coverage
        st.markdown("## Data Coverage")

        # Load ROI data for summary stats
        roi_df = self.data_manager.load_roi_metrics()

        if not roi_df.empty:
            # Filter out invalid ROI (999 flag values)
            valid_roi = roi_df[roi_df['roi_statewide_years'] < 999]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Institutions", f"{len(roi_df)}")
            with col2:
                st.metric("California Only", "Yes ✓")
            with col3:
                median_roi = valid_roi['roi_statewide_years'].median()
                st.metric("Median ROI", f"{median_roi:.1f} years")
            with col4:
                best_roi = valid_roi['roi_statewide_years'].min()
                st.metric("Best ROI", f"{best_roi:.1f} years")
        else:
            st.warning("ROI data not available. Run `python src/data/build_roi_metrics.py` to generate.")

        # How to explore
        st.markdown("## How to Explore This Section")
        st.markdown("""
        Use the sidebar charts to analyze ROI from different perspectives:

        - **Cost vs Earnings Quadrant**: Visualize the relationship between program cost
          and earnings outcomes. Identify high-value institutions (high earnings, low cost).

        - **Top 25 ROI Rankings**: See which institutions offer the fastest payback period.
          Compare statewide vs regional rankings.

        - **ROI by Sector**: Understand ROI distribution across public, private nonprofit, and
          private for-profit institutions.
        """)

        st.markdown("---")

        # Data source attribution
        st.markdown("## Data Sources")
        st.markdown("""
        - **Earnings Data**: College Scorecard (median earnings 10 years after entry)
        - **Cost Data**: IPEDS (net price)
        - **Baseline Earnings**: U.S. Census Bureau ACS 5-year estimates
        - **Coverage**: California Associate's degree-granting institutions
        - **Last Updated**: 2024

        *Migrated from the [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis) repository.*
        """)

        # Disclaimer
        st.warning("""
        **⚠️ Important Limitations**:
        - ROI analysis is limited to **California institutions only** (116 community and technical colleges)
        - Earnings data represents cohorts from 10+ years ago
        - Individual outcomes vary based on field of study, local labor markets, and personal circumstances
        - This is one metric among many for evaluating college value
        """)

    def render_chart(self, chart_name: str) -> None:
        """Render a specific ROI chart."""
        self.render_section_header("ROI", chart_name)

        # Load ROI data
        roi_data = self.data_manager.load_roi_metrics()

        if roi_data.empty:
            st.error("ROI data not available. Run `python src/data/build_roi_metrics.py` to generate.")
            return

        # California-only reminder
        st.info("📍 **California Institutions Only** - This analysis covers 116 California community and technical colleges.")

        # Render appropriate chart
        if chart_name == ROI_QUADRANT_LABEL:
            self._render_quadrant_chart(roi_data)
        elif chart_name == ROI_RANKINGS_LABEL:
            self._render_rankings_chart(roi_data)
        elif chart_name == ROI_DISTRIBUTION_LABEL:
            self._render_distribution_chart(roi_data)
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_quadrant_chart(self, data) -> None:
        """Render cost vs earnings quadrant chart with baseline tabs."""
        from src.charts.roi_quadrant_chart import render_roi_quadrant_chart

        st.markdown("""
        Visualize the relationship between program cost and earnings outcomes.
        Institutions in the **top-left quadrant** offer the best value
        (high earnings, low cost).
        """)

        # Tabs for statewide vs regional baseline
        tab1, tab2 = st.tabs(["Statewide Baseline", "Regional Baseline"])

        with tab1:
            render_roi_quadrant_chart(
                data,
                baseline="statewide",
                title="Cost vs Earnings Quadrant",
            )

        with tab2:
            render_roi_quadrant_chart(
                data,
                baseline="regional",
                title="Cost vs Earnings Quadrant",
            )

    def _render_rankings_chart(self, data) -> None:
        """Render ROI rankings with baseline and top/bottom tabs."""
        from src.charts.roi_rankings_chart import render_roi_rankings_chart

        st.markdown("""
        Compare institutions by years to recoup investment. Lower ROI = faster payback.
        """)

        # Tabs for statewide vs regional baseline
        baseline_tab1, baseline_tab2 = st.tabs(["Statewide Baseline", "Regional Baseline"])

        with baseline_tab1:
            st.markdown("#### Statewide Baseline Rankings")
            # Nested tabs for top vs bottom
            view_tab1, view_tab2 = st.tabs(["Top 25 (Best ROI)", "Bottom 25 (Worst ROI)"])

            with view_tab1:
                render_roi_rankings_chart(
                    data,
                    baseline="statewide",
                    view="top",
                    n=25,
                    title="Top 25 ROI Rankings",
                )

            with view_tab2:
                render_roi_rankings_chart(
                    data,
                    baseline="statewide",
                    view="bottom",
                    n=25,
                    title="Bottom 25 ROI Rankings",
                )

        with baseline_tab2:
            st.markdown("#### Regional Baseline Rankings")
            # Nested tabs for top vs bottom
            view_tab1, view_tab2 = st.tabs(["Top 25 (Best ROI)", "Bottom 25 (Worst ROI)"])

            with view_tab1:
                render_roi_rankings_chart(
                    data,
                    baseline="regional",
                    view="top",
                    n=25,
                    title="Top 25 ROI Rankings",
                )

            with view_tab2:
                render_roi_rankings_chart(
                    data,
                    baseline="regional",
                    view="bottom",
                    n=25,
                    title="Bottom 25 ROI Rankings",
                )

    def _render_distribution_chart(self, data) -> None:
        """Render ROI distribution by sector."""
        from src.charts.roi_distribution_chart import render_roi_distribution_chart

        st.markdown("""
        Understand how ROI varies across public, private nonprofit, and private for-profit institutions.
        Box plots show median, quartiles, and outliers.
        """)

        # Tabs for statewide vs regional baseline
        tab1, tab2 = st.tabs(["Statewide Baseline", "Regional Baseline"])

        with tab1:
            render_roi_distribution_chart(
                data,
                baseline="statewide",
                title="ROI Distribution by Sector",
            )

        with tab2:
            render_roi_distribution_chart(
                data,
                baseline="regional",
                title="ROI Distribution by Sector",
            )

    def get_available_charts(self) -> List[str]:
        """Get available charts for ROI section."""
        return [
            ROI_QUADRANT_LABEL,
            ROI_RANKINGS_LABEL,
            ROI_DISTRIBUTION_LABEL,
        ]
