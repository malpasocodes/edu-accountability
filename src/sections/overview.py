"""Overview section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection


class OverviewSection(BaseSection):
    """Handles the overview/landing page section."""
    
    def render_overview(self) -> None:
        """Render the overview page content."""
        # Hero Section with enhanced styling
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; margin-bottom: 2rem;'>
                <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem; font-weight: 700;'>
                    📊 EDU Accountability Lab
                </h1>
                <p style='color: #000000; font-size: 1.2rem; margin: 0; font-weight: 400;'>
                    Data-driven insights to track college accountability, affordability, and outcomes
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Mission Section
        st.subheader("Our Mission")
        st.markdown(
            """
            The EDU Accountability Lab delivers independent, data-driven analysis of
            higher education with a focus on accountability, affordability, and outcomes.
            Our audience includes policymakers, researchers, and taxpayers who seek greater transparency
            and effectiveness in postsecondary education. We take no advocacy position on specific
            institutions, programs, metrics, or policies. Our goal is to provide clear and well-documented
            methods that support policy discussions, strengthen institutional accountability,
            and improve public understanding of the value of higher education.
            """
        )
        
        # Current Focus Areas
        st.subheader("Current Focus Areas")

        st.markdown(
            """
            - **Metrics for Accountability**: We are refining measures that capture affordability, completion, and post-graduation outcomes. These metrics are designed to make comparisons across institutions more transparent, reproducible, and useful for policymakers and researchers.

            - **Government Funding Analysis**: We are analyzing the flow of federal support—especially through student loans and Pell Grants—to better understand how public resources shape affordability and access. Tracking these funding streams alongside institutional outcomes provides a fuller picture of higher education's value and accountability.
            """
        )
        
        # Disclaimer section
        st.subheader("Important Disclaimer")
        st.markdown(
            """
            The EDU Accountability Dashboard is a work in progress. Data and analyses presented here are intended solely
            for research and policy purposes and should not be used to make enrollment or investment decisions about
            individual colleges or programs. Metrics are derived from public datasets (e.g. IPEDS, U.S. Census) and may
            not capture all factors influencing educational or economic outcomes. While we strive for accuracy, users are
            responsible for independently verifying the data and analysis before drawing conclusions or making decisions.
            """
        )
        
        # Interactive Navigation Cards
        st.subheader("Explore the Dashboard")
        st.markdown("**Choose a section to begin your analysis:**")

        # Create four columns for navigation cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            with st.container():
                st.markdown(
                    """
                    <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; text-align: center; background-color: #f8fff8; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column;'>
                        <h3 style='color: #2ca02c; margin-bottom: 1rem;'>🎓 College Value Grid</h3>
                        <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                            <p style='color: #000000; margin-bottom: 1rem;'>Compare net price against graduation outcomes for institutions</p>
                            <p style='font-size: 0.9rem; color: #000000; margin: 0;'>Analyze cost vs. graduation rates across sectors</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:
            with st.container():
                st.markdown(
                    """
                    <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; text-align: center; background-color: #f8faff; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column;'>
                        <h3 style='color: #1f77b4; margin-bottom: 1rem;'>💳 Federal Loans</h3>
                        <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                            <p style='color: #000000; margin-bottom: 1rem;'>Explore institutions with largest federal loan volumes</p>
                            <p style='font-size: 0.9rem; color: #000000; margin: 0;'>Track loan trends and institutional patterns</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col3:
            with st.container():
                st.markdown(
                    """
                    <div style='padding: 1.5rem; border: 2px solid #9467bd; border-radius: 10px; text-align: center; background-color: #faf9ff; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column;'>
                        <h3 style='color: #9467bd; margin-bottom: 1rem;'>🎯 Pell Grants</h3>
                        <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                            <p style='color: #000000; margin-bottom: 1rem;'>Review award concentrations and multi-year trends</p>
                            <p style='font-size: 0.9rem; color: #000000; margin: 0;'>Analyze grant distributions and outcomes</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col4:
            with st.container():
                st.markdown(
                    """
                    <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; text-align: center; background-color: #fffaf5; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column;'>
                        <h3 style='color: #ff7f0e; margin-bottom: 1rem;'>💻 Distance Education</h3>
                        <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                            <p style='color: #000000; margin-bottom: 1rem;'>Explore online and hybrid learning enrollment patterns</p>
                            <p style='font-size: 0.9rem; color: #000000; margin: 0;'>Analyze distance education participation trends</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def render_chart(self, chart_name: str) -> None:
        """
        Overview section has no charts.

        Args:
            chart_name: Name of the chart (unused)
        """
        # chart_name is unused since overview has no charts
        _ = chart_name
        self.render_overview()
    
    def get_available_charts(self) -> List[str]:
        """
        Get available charts for overview section.
        
        Returns:
            Empty list as overview has no charts
        """
        return []