"""ROI section implementation - California institutions only."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection
from src.config.constants import (
    ROI_QUADRANT_LABEL,
    ROI_RANKINGS_LABEL,
    ROI_DISTRIBUTION_LABEL,
    ROI_EARNINGS_PREMIUM_LABEL,
    ROI_EARNINGS_PREMIUM_RANKINGS_LABEL,
)
from src.ui.disclaimer import load_disclaimer_content


class ROISection(BaseSection):
    """Handles the ROI section for California institutions."""

    def render_overview(self) -> None:
        """Render the ROI overview page - Alpha release."""
        self.render_section_header("ROI", "Overview")

        # Hero section with Alpha Release badge
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    📈 ROI Analysis <span style='color: #ff0000;'>(Alpha Release)</span>
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Measuring educational investment returns for California institutions
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Overview section
        st.markdown("### Overview")
        st.markdown("""
        This Alpha release introduces the first version of our Return on Investment (ROI) analysis for higher education programs.
        Our objective is to measure how well colleges and programs translate educational investment—tuition, time, and effort—into improved earnings over time.

        We are currently working with California institutions only. Additional states and expanded metrics will be added in future updates.

        This release provides a directional view, not an official assessment. Metrics rely on publicly available data that aggregate outcomes at the institution level, not by specific program.
        Users should treat these results as exploratory and consult the full disclaimer before drawing conclusions.
        """)

        st.markdown("---")

        # What We're Building section
        st.markdown("### What We're Building")
        st.markdown("""
        Over the coming releases, we will develop several complementary metrics to evaluate educational value, including:
        - **Earnings Premium (EP)**: Comparing graduates' median earnings to those of high-school peers.
        - **Payback Period**: Estimating how long it takes for cumulative earnings gains to offset educational costs.
        - **Cost-Adjusted ROI Index**: Integrating both earnings and cost into a single, interpretable measure.

        These measures together will help identify where students, families, and taxpayers are realizing the greatest returns—and where outcomes fall short.
        """)

        st.markdown("---")

        # A Simple Example section
        st.markdown("### A Simple Example")
        st.markdown(r"""
        Consider two California students making different educational choices:

        **Maya** enrolls in a state university with an average annual cost of \$10,000.
        After four years, she completes her degree in accounting and, five years later, earns about \$70,000 annually.

        **Jordan**, her friend who entered the workforce directly after high school, now earns \$45,000.
        Maya's earnings premium is \$25,000 per year, suggesting her degree provided strong long-term value.

        By contrast, **Leo** attends a private fine-arts college with total tuition and fees of \$60,000.
        Five years after graduation, he earns \$42,000—below Jordan's \$45,000.
        Leo's earnings premium is negative, meaning his educational investment has not yet paid off.

        These examples show how ROI helps contextualize cost and earnings together—identifying which educational paths lead to faster economic recovery and greater mobility.
        """)

        st.markdown("---")

        # How to Explore section
        st.markdown("### How to Explore")
        st.markdown("""
        Use the sidebar tools to analyze ROI across California institutions:
        - **Cost vs. Earnings Quadrant**: Compare cost and outcomes across sectors.
        - **Top ROI Rankings**: View institutions with the fastest estimated payback period.
        - **ROI by Sector**: Examine differences across public, private nonprofit, and for-profit institutions.
        """)

        st.markdown("---")

        # Data Notes section
        st.markdown("### Data Notes")
        st.markdown("""
        - **Coverage**: California community and technical colleges (327 institutions with valid IPEDS UnitIDs).
        - **Earnings**: College Scorecard median earnings 10 years after entry (`md_earn_wne_p10`).
        - **Costs**: IPEDS annual net price aggregated to total program cost.
        - **Baseline**: U.S. Census ACS 5-year median earnings for high-school graduates (state and county levels).
        - **Processing**: `src/data/build_roi_metrics.py` merges and normalizes data into `data/processed/roi_metrics.parquet`.
        - **Negative premiums**: Institutions with non-positive ROI are flagged and excluded from default charts.
        """)

        st.markdown("---")

        # Important Limitation section with red styling
        st.markdown('<h4 style="color: red;">⚠️ Important Limitation</h4>', unsafe_allow_html=True)
        st.markdown(
            """
            This Alpha release presents a preliminary analysis based on institution-level median data for California only.
            Results are illustrative and exploratory, not official or program-specific, and should not be used for compliance, ranking, or investment decisions.
            Metrics may change substantially as additional data and states are incorporated.
            Use of this section implies acceptance of the <span style="color: red;">Full Disclaimer & Terms of Use</span>.
            """,
            unsafe_allow_html=True
        )

        # Full Disclaimer expander
        with st.expander("📄 View Full Disclaimer & Terms of Use"):
            disclaimer_content = load_disclaimer_content()
            st.markdown(disclaimer_content)
            st.markdown("---")
            st.markdown(
                """
                **By accessing or using this site, you acknowledge that you have read, understood,
                and accepted these terms.** If you do not agree with these terms, you should discontinue
                use of the site immediately.
                """
            )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific ROI chart."""
        self.render_section_header("ROI", chart_name)

        # Load ROI data
        roi_data = self.data_manager.load_roi_metrics()

        if roi_data.empty:
            st.error("ROI data not available. Run `python src/data/build_roi_metrics.py` to generate.")
            return

        # California-only reminder
        st.info("📍 **California Institutions Only** - This analysis covers California community and technical colleges.")

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

    def _render_earnings_premium_table(self, data) -> None:
        """Render earnings premium comparison table."""
        import pandas as pd

        st.markdown(r"""
        ## Statewide vs Regional Earnings Premiums for California Institutions

        This comparison shows how earnings premium calculations change when using different high school baseline earnings.

        **C-Metric** uses a single statewide baseline (\$24,939) for all institutions, while **H-Metric** uses each institution's local county baseline. The **Delta** column shows which approach gives graduates a higher earnings advantage—positive values favor the statewide method, negative values favor the county method.

        This matters because it affects how institutions are evaluated and ranked for return on investment.
        """)

        # Prepare data for display
        display_df = data[['Institution', 'County', 'premium_statewide', 'premium_regional']].copy()

        # Calculate delta
        display_df['delta'] = display_df['premium_statewide'] - display_df['premium_regional']

        # Rename columns for display
        display_df = display_df.rename(columns={
            'premium_statewide': 'C-Metric (Statewide)',
            'premium_regional': 'H-Metric (Regional)',
            'delta': 'Delta'
        })

        # Configure column display
        st.dataframe(
            display_df,
            column_config={
                "Institution": st.column_config.TextColumn("Institution", width="medium"),
                "County": st.column_config.TextColumn("County", width="small"),
                "C-Metric (Statewide)": st.column_config.NumberColumn(
                    "C-Metric (Statewide)",
                    format="$%d",
                    help="Earnings premium using statewide HS baseline ($24,939)"
                ),
                "H-Metric (Regional)": st.column_config.NumberColumn(
                    "H-Metric (Regional)",
                    format="$%d",
                    help="Earnings premium using county-specific HS baseline"
                ),
                "Delta": st.column_config.NumberColumn(
                    "Delta",
                    format="$%d",
                    help="Difference: positive = statewide favors institution, negative = regional favors institution"
                ),
            },
            width="stretch",
            hide_index=True,
        )

        # Explanatory notes
        st.markdown("---")
        st.markdown(r"""
        ### About the Metrics

        - **C-Metric (Statewide Baseline)**: Uses California's statewide median high school graduate earnings (\$24,939) as the comparison point for all institutions.
        - **H-Metric (Regional Baseline)**: Uses county-specific median high school graduate earnings, accounting for local economic conditions.
        - **Delta**: Shows the difference between C-Metric and H-Metric. A positive delta means graduates appear more advantaged when compared to the statewide baseline, while a negative delta means they appear more advantaged compared to their local county baseline.

        ### Why This Matters

        Institutions in high-cost counties (like San Francisco or Santa Clara) may show better ROI when evaluated against their local baseline, since local high school graduates also earn more. Conversely, institutions in lower-cost counties may show better ROI when compared to the statewide baseline. This comparison reveals how geography influences perceived institutional value.

        ### Data Sources

        - **Earnings Data**: College Scorecard (median earnings 10 years after entry)
        - **Baseline Earnings**: U.S. Census Bureau ACS 5-year estimates
        - **Coverage**: California Associate's degree-granting institutions (116 colleges)
        """)

    def _render_earnings_premium_rankings(self, data) -> None:
        """Render side-by-side earnings premium rankings comparison."""
        import pandas as pd

        st.markdown("## Earnings Premium Rankings")
        st.markdown("Side-by-side comparison of rankings based on C-Metric (Statewide) and H-Metric (Regional) earnings premiums")

        # Create C-Metric rankings
        c_rankings = data[['Institution', 'Sector', 'premium_statewide']].copy()
        c_rankings = c_rankings.sort_values('premium_statewide', ascending=False).reset_index(drop=True)
        c_rankings['Rank'] = range(1, len(c_rankings) + 1)
        c_rankings = c_rankings[['Rank', 'Institution', 'Sector', 'premium_statewide']]
        c_rankings = c_rankings.rename(columns={'premium_statewide': 'Earnings Premium'})

        # Create H-Metric rankings
        h_rankings = data[['Institution', 'Sector', 'premium_regional']].copy()
        h_rankings = h_rankings.sort_values('premium_regional', ascending=False).reset_index(drop=True)
        h_rankings['Rank'] = range(1, len(h_rankings) + 1)
        h_rankings = h_rankings[['Rank', 'Institution', 'Sector', 'premium_regional']]
        h_rankings = h_rankings.rename(columns={'premium_regional': 'Earnings Premium'})

        # Create two columns for side-by-side display
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 C-Metric Rankings")
            st.caption("Based on Statewide Baseline ($24,939)")

            st.dataframe(
                c_rankings,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Institution": st.column_config.TextColumn("Institution", width="medium"),
                    "Sector": st.column_config.TextColumn("Sector", width="small"),
                    "Earnings Premium": st.column_config.NumberColumn(
                        "Earnings Premium",
                        format="$%d",
                        width="small"
                    ),
                },
                hide_index=True,
                height=600,
            )

        with col2:
            st.markdown("### 📊 H-Metric Rankings")
            st.caption("Based on Regional (County) Baselines")

            st.dataframe(
                h_rankings,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "Institution": st.column_config.TextColumn("Institution", width="medium"),
                    "Sector": st.column_config.TextColumn("Sector", width="small"),
                    "Earnings Premium": st.column_config.NumberColumn(
                        "Earnings Premium",
                        format="$%d",
                        width="small"
                    ),
                },
                hide_index=True,
                height=600,
            )

        # Explanatory text
        st.markdown("---")
        st.markdown(r"""
        ### Understanding the Rankings

        This side-by-side comparison reveals how baseline selection affects institutional rankings:

        - **C-Metric (Left)**: Ranks institutions by earnings premium calculated using California's statewide median high school graduate earnings (\$24,939). This provides a consistent benchmark across all institutions.

        - **H-Metric (Right)**: Ranks institutions by earnings premium calculated using county-specific median high school graduate earnings. This accounts for local economic conditions and cost of living.

        ### Key Observations

        - **Rank shifts** between the two columns indicate institutions whose value proposition changes based on geographic context
        - Institutions in **high-cost counties** (San Francisco, Santa Clara) may rank higher with H-Metric due to higher local baselines
        - Institutions in **lower-cost counties** may rank higher with C-Metric due to the statewide average being higher than their local baseline

        ### Data Sources

        - **Earnings Data**: College Scorecard (median earnings 10 years after entry)
        - **Baseline Earnings**: U.S. Census Bureau ACS 5-year estimates (statewide and county-level)
        - **Coverage**: California Associate's degree-granting institutions (116 colleges)
        """)

    def get_available_charts(self) -> List[str]:
        """Get available charts for ROI section."""
        return [
            ROI_QUADRANT_LABEL,
            ROI_RANKINGS_LABEL,
            ROI_DISTRIBUTION_LABEL,
        ]
