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


class ROISection(BaseSection):
    """Handles the ROI section for California institutions."""

    def render_overview(self) -> None:
        """Render the ROI overview page."""
        self.render_section_header("ROI", "Overview")

        # Hero section
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
            <h1 style='margin: 0; color: white;'>💰 Measuring Return on Investment in Higher Education</h1>
            <p style='font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;'>
                Understanding earnings outcomes and accountability through outcomes-based frameworks
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Key insight callout
        st.info("""
        **🎯 Key Insight**: Higher education policy is shifting from access-only metrics
        toward value and accountability—not just whether students can enroll, but whether
        their investment pays off.
        """)

        # What is this section
        st.markdown("## What is ROI Analysis?")
        st.markdown("""
        A core premise of higher education policy is that pursuing a college degree or credential
        should lead to higher earnings and greater social mobility. Yet evidence shows that not all
        programs deliver on that promise. Some leave students with debt but little or no economic
        gain—sometimes even worse off than if they had entered the workforce directly after high school.

        A new federal provision under the **One Big Beautiful Bill Act (OBBBA)** introduces a major
        step toward addressing this problem. The law establishes an outcomes-based accountability
        framework that evaluates whether programs provide a positive economic return to their students.
        At its center is the **Earnings Premium Test**, which asks a simple but powerful question:

        **Are students, on average, better off financially after completing this program than if they
        had not attended at all?**
        """)

        # The Earnings Premium Test
        st.markdown("### The Earnings Premium Test")
        st.markdown("""
        Under this framework, each program's graduates are compared to a relevant benchmark:

        - **Undergraduate programs** → median earnings of graduates are compared to median earnings of high school graduates
        - **Graduate and professional programs** → median earnings are compared to median earnings of bachelor's degree holders

        If a program fails this test for **two out of three consecutive years**, it loses eligibility to offer federal student loans—a powerful incentive for institutions to ensure that programs genuinely improve their students' economic prospects.

        This approach aligns with broader efforts—such as the **Postsecondary Value Commission's Threshold 0**—to define a minimum acceptable return on investment for higher education. Together, these efforts reflect a shift from access-only metrics toward value and accountability: not just whether students can enroll, but whether their investment pays off.
        """)

        # Visualizing ROI
        st.markdown("## Visualizing ROI")
        st.markdown("""
        A simple way to understand Return on Investment (ROI) in higher education is to trace a student's path over time—linking what they pay to what they earn.

        1. **Entry Point**: A student enrolls in a college program and begins paying tuition and fees. These represent the cost of investment—the amount of money (and time) the student must commit to pursue the credential.

        2. **Completion**: After several years, the student graduates and enters the workforce.

        3. **Post-Graduation**: A few years after completion, we compare their median annual earnings to those of a comparable group:
           - For undergraduate programs, high school graduates.
           - For graduate or professional programs, bachelor's degree holders.

        The difference in earnings represents the **earnings premium**, while the cost of attendance represents the **investment** required to achieve it.

        Together, these two elements—earnings and cost—determine the program's economic value:

        - A high earnings premium and low cost suggest **strong ROI**.
        - A low earnings premium and high cost indicate **weak ROI** or potential harm.
        """)

        # A Practical Example
        st.markdown("### A Practical Example")
        st.markdown(r"""
        Consider Maya, a high school graduate deciding whether to enroll in a four-year college program.

        - **Entry Point**: Maya chooses a state university with an average annual cost of \$10,000 in tuition and fees. Over four years, her total investment is about \$40,000, not including living expenses.
        - **Completion**: Maya graduates with a degree in accounting and begins her career at a modest starting salary.
        - **Some Years After Graduation (e.g., Five)**: By this point, Maya's median annual earnings have risen to \$70,000. Her friend Jordan, who entered the workforce directly after high school, now earns \$45,000.

        The earnings premium for Maya's degree—measured some number of years (e.g., five) after graduation—is **\$25,000 per year**. Over time, her higher earnings have allowed her to recover the cost of her education and continue building wealth at a faster rate.

        Now consider another student, Leo, who attends a private college fine arts program with total tuition and fees of \$60,000. Some number of years (e.g., five) after graduation, Leo earns \$42,000, only slightly above Jordan's \$45,000. His earnings premium is **negative**, meaning that even years after completing his degree, he has not recouped the cost of his education.

        This example illustrates how the Earnings Premium Test evaluates return over time. It doesn't measure immediate outcomes but rather asks whether, some number of years (e.g., five) after graduation, students are financially better off than if they had never enrolled—and whether the return justifies both the public and personal investment.
        """)

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
        st.markdown("## Data Notes")
        st.markdown("""
        - **Coverage:** California community and technical colleges only (327 institutions with mapped IPEDS UnitIDs).
        - **Source repository:** [Higher Ed ROI Research Lab (epanalysis)](https://github.com/malpasocodes/epanalysis); raw files live under `data/raw/epanalysis/`.
        - **Earnings:** College Scorecard median earnings **10 years after entry** (`md_earn_wne_p10`).
        - **Costs:** IPEDS annual net price aggregated to a total program cost before import.
        - **Baselines:** U.S. Census ACS 5-year high school earnings, provided at both statewide and county levels.
        - **Processing pipeline:** `src/data/build_roi_metrics.py` merges the epanalysis metrics with IPEDS `UnitID`, normalizes dtypes, adds ROI-in-months flags, and saves `data/processed/roi_metrics.parquet`.
        - **Negative premiums:** Institutions with non-positive earnings premiums are flagged with `ROI = 999` and excluded from charts by default.
        """)

        # Disclaimer
        st.warning("""
        **⚠️ Important Limitations**:
        - ROI analysis is limited to **California institutions only** (327 community, technical, and career colleges)
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
