"""Earnings Premium section implementation - California institutions only."""

from __future__ import annotations

from typing import List

import streamlit as st

from .base import BaseSection
from src.config.constants import (
    ROI_EARNINGS_PREMIUM_LABEL,
    ROI_EARNINGS_PREMIUM_RANKINGS_LABEL,
)


class EarningsPremiumSection(BaseSection):
    """Handles the Earnings Premium section for California institutions."""

    def render_overview(self) -> None:
        """Render the Earnings Premium overview page (stub)."""
        self.render_section_header("Earnings Premium", "Overview")

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    💼 Earnings Premium Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Compare graduate earnings against statewide and local baselines to gauge long-term value.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            This section highlights how California community and technical colleges perform on **earnings premiums**—the
            additional income graduates earn compared to high school completers. We provide two complementary perspectives:

            - **C-Metric (Statewide baseline)**: Compares graduate earnings to California's statewide high school earnings benchmark.
            - **H-Metric (Regional baseline)**: Compares the same graduates to the median earnings of high school graduates **in their college's county**, capturing local wage conditions.

            Use the sidebar to explore:

            - **Earnings Premium (All)**: Detailed table of statewide vs regional premiums and deltas.
            - **Earnings Premium Rankings**: Side-by-side ranking views using the two baselines.
            """
        )

        st.divider()

        st.markdown("### Data Notes")
        st.markdown(
            """
            - **Data coverage:** California community, technical, and career colleges only (327 institutions).
            - **Source files:** Imported from the [epanalysis](https://github.com/malpasocodes/epanalysis) ROI project (`data/raw/epanalysis/roi-metrics.csv`).
            - **Earnings data:** College Scorecard median earnings **10 years after entry** (historical cohorts, ~2010 entrants).
            - **Cost data:** IPEDS net price, aggregated to a total program cost (annual net price × program length) in the epanalysis pipeline.
            - **Baselines:** High school graduate earnings from U.S. Census ACS 5-year estimates—statewide ($24,939) and county-specific values.
            - **Processing:** `src/data/build_roi_metrics.py` merges these metrics, appends IPEDS `UnitID`, and stores them in `data/processed/roi_metrics.parquet`.
            """
        )

        st.warning(
            "📍 **California only** – No institutions outside California are included. "
            "Premiums reflect historical earnings and may not capture recent labor market shifts."
        )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Earnings Premium chart."""
        self.render_section_header("Earnings Premium", chart_name)

        # Load ROI data
        roi_data = self.data_manager.load_roi_metrics()

        if roi_data.empty:
            st.error("ROI data not available. Run `python src/data/build_roi_metrics.py` to generate.")
            return

        # California-only reminder
        st.info("📍 **California Institutions Only** - This analysis covers California community and technical colleges.")

        # Render appropriate chart by delegating to shared methods
        if chart_name == ROI_EARNINGS_PREMIUM_LABEL:
            self._render_earnings_premium_table(roi_data)
        elif chart_name == ROI_EARNINGS_PREMIUM_RANKINGS_LABEL:
            self._render_earnings_premium_rankings(roi_data)
        else:
            st.error(f"Unknown chart: {chart_name}")

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
        - **Coverage**: California Associate's degree-granting institutions
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
        - **Coverage**: California Associate's degree-granting institutions
        """)

    def get_available_charts(self) -> List[str]:
        """Get available charts for Earnings Premium section."""
        return [
            ROI_EARNINGS_PREMIUM_LABEL,
            ROI_EARNINGS_PREMIUM_RANKINGS_LABEL,
        ]
