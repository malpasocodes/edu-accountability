"""Overview section implementation."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection


class OverviewSection(BaseSection):
    """Handles the overview/landing page section."""
    
    def render_overview(self) -> None:
        """Render the overview page content."""
        st.title("EDU Accountability Dashboard")
        st.caption(
            "Data driven insights to track college accountability, affordability, and outcomes."
        )
        
        st.subheader("Mission")
        st.markdown(
            """
            The EDU Accountability Dashboard delivers independent, data-driven analysis of 
            higher education with a focus on accountability, affordability, and outcomes.
            Our audience includes policymakers, researchers, and taxpayers who seek greater transparency
            and effectiveness in postsecondary education. We take no advocacy position on specific 
            institutions, programs, metrics, or policies. Our goal is to provide clear and well-documented 
            methods that support policy discussions, strengthen institutional accountability, 
            and improve public understanding of the value of higher education.

            """
        )
        
        st.subheader("Current Focus")
        st.markdown(
            """
            **1. Metrics for Accountability**  
We are refining measures that capture affordability, completion, and post-graduation outcomes. These metrics are designed to make comparisons across institutions more transparent, reproducible, and useful for policymakers and researchers.  

**2. Government Funding of Higher Education**  
We are analyzing the flow of federal support—especially through student loans and Pell Grants—to better understand how public resources shape affordability and access. Tracking these funding streams alongside institutional outcomes provides a fuller picture of higher education's value and accountability.  
        """
        )
        
        st.subheader("Disclaimer")
        st.markdown(
            """
            The EDU Accountability Dashboard is a work in progress. Data and analyses presented here are intended solely 
            for research and policy purposes and should not be used to make enrollment or investment decisions about 
            individual colleges or programs. Metrics are derived from public datasets (e.g. IPEDS, U.S. Census) and may 
            not capture all factors influencing educational or economic outcomes. While we strive for accuracy, users are 
            responsible for independently verifying the data and analysis before drawing conclusions or making decisions.

            """
        )
        
        st.subheader("Getting Started")
        st.markdown(
            """
            **How to use the dashboard**

            - Choose **College Value Grid** to compare net price against graduation outcomes for four-year and two-year institutions.
            - Review **Federal Loans** to see which institutions draw the largest federal loan volumes.
            - Open **Pell Grants** to review award concentrations, multi-year trends, and outcome relationships.
           
            """
        )
    
    def render_chart(self, chart_name: str) -> None:
        """
        Overview section has no charts.
        
        Args:
            chart_name: Name of the chart (unused)
        """
        self.render_overview()
    
    def get_available_charts(self) -> List[str]:
        """
        Get available charts for overview section.
        
        Returns:
            Empty list as overview has no charts
        """
        return []