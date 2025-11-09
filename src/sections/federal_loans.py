"""Federal Loans section implementation."""

from __future__ import annotations

from typing import List, Optional

import streamlit as st

from src.charts.loan_top_dollars_chart import render_loan_top_dollars_chart
from src.charts.loan_trend_chart import render_loan_trend_chart
from src.charts.loan_trend_total_chart import render_loan_trend_total_chart
from src.charts.loan_vs_grad_scatter_chart import render_loan_vs_grad_scatter
from src.config.constants import (
    FEDERAL_LOANS_SECTION,
    FOUR_YEAR_VALUE_GRID_LABEL,
    TWO_YEAR_VALUE_GRID_LABEL,
    LOAN_OVERVIEW_LABEL,
    LOAN_TOP_DOLLARS_LABEL,
    LOAN_VS_GRAD_LABEL,
    LOAN_TREND_LABEL,
    LOAN_TREND_TOTAL_LABEL,
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

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    💳 Federal Loans Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Follow federal lending patterns to see where student debt concentrates and how it shifts over time.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Key insight callout
        st.info("**💡 Key Insight:** Federal loan data reveals which institutions carry the highest student debt burdens and how those patterns relate to graduation outcomes and change over time.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is Federal Loans Analysis?")
        st.markdown(
            """
            This section tracks **federal student loan dollars** disbursed to students at colleges and universities
            across the United States. The data covers **2008-2022** and shows which institutions have the highest
            loan volumes, how those loans relate to graduation rates, and how debt patterns have evolved over time.

            Federal loans represent a significant source of financial aid and a key measure of student debt burden.
            Understanding where these dollars flow helps illuminate affordability challenges and institutional reliance
            on federal lending.
            """
        )

        st.divider()

        # Available analyses section
        st.markdown("### Four Ways to Explore Federal Loan Data")
        st.markdown(
            """
            Use the **sidebar charts** to examine federal loan patterns from different angles. Each analysis
            is available for both 4-year and 2-year institutions:
            """
        )

        st.markdown("")  # Spacing

        # Four analysis types in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f8faff; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #1f77b4; margin-bottom: 0.75rem;'>📊 Largest Federal Loan Portfolios</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>See which institutions receive the most federal loan dollars, aggregated across all available years.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Choose Top 10/25/50/100 institutions and compare totals by sector.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem; height: 260px; display: flex; flex-direction: column; justify-content: space-between;'>
                    <div>
                        <h4 style='color: #2ca02c; margin-bottom: 0.75rem;'>📈 Federal Loans vs Graduation Rate</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>Compare loan volumes against graduation outcomes.</p>
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
                        <h4 style='color: #ff7f0e; margin-bottom: 0.75rem;'>📉 Federal Loan Dollars Trend (Top 10)</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>Track how loan volumes change over time for top 10 institutions.</p>
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
                        <h4 style='color: #9467bd; margin-bottom: 0.75rem;'>📊 Federal Loan Dollars Trend (Total)</h4>
                        <p style='color: #000000; margin-bottom: 0.75rem;'>See aggregate federal loan dollar totals summed across all institutions per year.</p>
                    </div>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Shows overall lending patterns and national trends (2008-2022).</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # How to use section
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Start with Largest Federal Loan Portfolios** to identify institutions with the highest debt volumes.
            Then explore the **vs Graduation Rate** chart to see how loan burdens relate to student outcomes.
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
            Federal loan data reveals important patterns about affordability and access:

            - **High loan volumes** may indicate large enrollment, high costs, or limited grant aid
            - **Loan vs graduation trends** show whether debt burden aligns with degree completion
            - **Multi-year patterns** reveal how institutions' reliance on federal loans has shifted
            - **Sector differences** emerge between public, private nonprofit, and for-profit colleges
            """
        )

        st.divider()

        # Data disclaimer
        st.markdown("### Data Source & Notes")
        st.info(
            "**Data Source:** IPEDS (Integrated Postsecondary Education Data System), 2008-2022. "
            "Loan totals reflect annual federal loan dollars disbursed to students at each institution. "
            "For high-stakes decisions, validate against the latest Department of Education releases."
        )
    
    def render_chart(self, chart_name: str) -> None:
        """Render a specific Federal Loans chart."""
        self.render_section_header(FEDERAL_LOANS_SECTION, chart_name)
        
        if self.data_manager.loan_df is None or self.data_manager.loan_df.empty:
            st.warning(
                "Loan dataset is unavailable. Confirm `data/raw/fsa/loantotals.csv` exists and reload."
            )
            return
        
        # Handle consolidated chart names with tabs
        if chart_name == LOAN_TOP_DOLLARS_LABEL:
            self._render_loan_top_dollars_with_tabs(chart_name)
        elif chart_name == LOAN_VS_GRAD_LABEL:
            self._render_loan_vs_grad_with_tabs(chart_name)
        elif chart_name == LOAN_TREND_LABEL:
            self._render_loan_trend_with_tabs(chart_name)
        elif chart_name == LOAN_TREND_TOTAL_LABEL:
            self._render_loan_trend_total_with_tabs(chart_name)
        # Handle individual chart names for backward compatibility
        elif chart_name == LOAN_TOP_DOLLARS_FOUR_LABEL:
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
    
    def _render_loan_top_dollars(self, sector: str, title: str, *, top_n: Optional[int] = None) -> None:
        """Render loan top dollars chart."""
        if top_n is None:
            top_options = [10, 25, 50, 100]
            default_index = top_options.index(25)
            top_n = st.selectbox(
                "Select ranking depth",
                options=top_options,
                index=default_index,
                format_func=lambda value: f"Top {value}",
                key=f"loan_top_portfolios_{sector}_top_n",
                help="Change how many institutions appear in the ranking.",
            )
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_loan_top_dollars_chart(
                self.data_manager.loan_df,
                metadata,
                top_n=top_n,
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
    
    def _render_loan_top_dollars_with_tabs(self, title: str) -> None:
        """Render loan top dollars chart with 4-year and 2-year tabs."""
        top_options = [10, 25, 50, 100]
        default_index = top_options.index(25)
        top_n = st.selectbox(
            "Show largest federal loan portfolios",
            options=top_options,
            index=default_index,
            format_func=lambda value: f"Top {value}",
            key="loan_top_portfolios_top_n",
        )
        tab1, tab2 = st.tabs(["4-year", "2-year"])
        
        with tab1:
            self._render_loan_top_dollars("four_year", f"{title} (4-year)", top_n=top_n)
        
        with tab2:
            self._render_loan_top_dollars("two_year", f"{title} (2-year)", top_n=top_n)
    
    def _render_loan_vs_grad_with_tabs(self, title: str) -> None:
        """Render loan vs graduation chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])
        
        with tab1:
            self._render_loan_vs_grad("four_year", f"{title} (4-year)")
        
        with tab2:
            self._render_loan_vs_grad("two_year", f"{title} (2-year)")
    
    def _render_loan_trend_with_tabs(self, title: str) -> None:
        """Render loan trend chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_loan_trend("four_year", f"{title} (4-year)")

        with tab2:
            self._render_loan_trend("two_year", f"{title} (2-year)")

    def _render_loan_trend_total_with_tabs(self, title: str) -> None:
        """Render total loan trend chart with 4-year and 2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_loan_trend_total("four_year", f"{title} (4-year)")

        with tab2:
            self._render_loan_trend_total("two_year", f"{title} (2-year)")

    def _render_loan_trend_total(self, sector: str, title: str) -> None:
        """Render total loan trend chart."""
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is not None:
            render_loan_trend_total_chart(
                self.data_manager.loan_df,
                metadata,
                title=title,
                sector=sector,
            )
        else:
            st.error(f"Missing metadata for {sector.replace('_', '-')} institutions.")

    def get_available_charts(self) -> List[str]:
        """Get available charts for Federal Loans section."""
        return LOAN_CHARTS
