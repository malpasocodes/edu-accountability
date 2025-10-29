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
            <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 2rem;'>
                <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 0.5rem; font-weight: 700;'>
                    📊 EDU Accountability Lab <span style='color: #ff0000;'>(Beta)</span>
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

            - **Earnings Premium & ROI**: We are building tools that compare post-graduation earnings to educational costs and aid profiles. These analyses surface institutions delivering strong wage gains relative to investment, helping stakeholders gauge long-term value across different student populations.

            - **Equity and Subgroup Outcomes**: We are examining how affordability, funding, and outcomes vary across student subgroups (e.g., income levels, race/ethnicity, first-generation status). Highlighting these differential impacts provides a more complete understanding of equity in higher education.
            """
        )
        
        # Important Notice section - display full disclaimer
        from src.ui.disclaimer import render_disclaimer_summary
        render_disclaimer_summary()
        
        # Interactive Navigation Cards
        st.subheader("Explore the Dashboard")
        st.markdown("**Choose a section to begin your analysis:**")

        card_definitions = [
            {
                "title": "🎓 College Value Grid",
                "border": "#2ca02c",
                "header_color": "#2ca02c",
                "background": "#f8fff8",
                "headline": "Compare cost against graduation outcomes for institutions",
                "detail": "Analyze cost vs. graduation rates across sectors",
            },
            {
                "title": "💳 Federal Loans",
                "border": "#1f77b4",
                "header_color": "#1f77b4",
                "background": "#f8faff",
                "headline": "Explore institutions with largest federal loan volumes",
                "detail": "Track loan trends and institutional patterns",
            },
            {
                "title": "🎯 Pell Grants",
                "border": "#9467bd",
                "header_color": "#9467bd",
                "background": "#faf9ff",
                "headline": "Review award concentrations and multi-year trends",
                "detail": "Analyze grant distributions and outcomes",
            },
            {
                "title": "💻 Distance Education",
                "border": "#ff7f0e",
                "header_color": "#ff7f0e",
                "background": "#fffaf5",
                "headline": "Explore online and hybrid learning enrollment patterns",
                "detail": "Analyze distance education participation trends",
            },
            {
                "title": "💼 Earnings Premium",
                "border": "#d62728",
                "header_color": "#d62728",
                "background": "#fff5f5",
                "headline": "Assess wage outcomes relative to peer institutions",
                "detail": "Evaluate post-graduation earnings premiums across cohorts",
            },
            {
                "title": "📈 ROI",
                "border": "#17becf",
                "header_color": "#17becf",
                "background": "#f0fbfd",
                "headline": "Combine cost, aid, and outcomes into ROI metrics",
                "detail": "Compare long-term value indicators for institutions",
            },
        ]

        for row_start in range(0, len(card_definitions), 3):
            columns = st.columns(3)
            for column, card in zip(columns, card_definitions[row_start : row_start + 3]):
                with column:
                    with st.container():
                        card_html = f"""
                        <div style='padding: 1.5rem; border: 2px solid {card["border"]}; border-radius: 10px; text-align: center; background-color: {card["background"]}; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column;'>
                            <h3 style='color: {card["header_color"]}; margin-bottom: 1rem;'>{card["title"]}</h3>
                            <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                                <p style='color: #000000; margin-bottom: 1rem;'>{card["headline"]}</p>
                                <p style='font-size: 0.9rem; color: #000000; margin: 0;'>{card["detail"]}</p>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

        # Contact section at bottom
        st.markdown("---")
        st.markdown(
            """
            📬 **Contact**
            For questions, data verification, or to report a potential inaccuracy, please email **[support@edu-accountability.com](mailto:support@edu-accountability.com)**.
            Your feedback helps us improve the clarity and reliability of this work.
            """
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
