"""Earnings Premium Analysis section implementation."""

from __future__ import annotations

from typing import List
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config.constants import (
    EARNINGS_PREMIUM_SECTION,
    EARNINGS_PREMIUM_OVERVIEW_LABEL,
    EP_OVERVIEW_RISK_MAP_LABEL,
    EP_INSTITUTION_LOOKUP_LABEL,
    EP_METHODOLOGY_LABEL,
)
from src.core.ep_data_loader import (
    load_ep_data,
    load_state_thresholds,
    get_risk_summary,
    search_institutions,
    get_institution_by_unitid,
    get_peer_institutions,
)
from .base import BaseSection


class EarningsPremiumAnalysisSection(BaseSection):
    """Handles the Earnings Premium Analysis section."""

    def render_overview(self) -> None:
        """Render the Earnings Premium Analysis overview."""
        self.render_section_header(EARNINGS_PREMIUM_SECTION, EARNINGS_PREMIUM_OVERVIEW_LABEL)

        # Hero section
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    📈 Earnings Premium Analysis Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Assess institutional readiness for July 1, 2026 Earnings Premium requirements
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # What is Earnings Premium
        st.markdown("### What is the Earnings Premium Test?")
        st.markdown(
            """
            Starting **July 1, 2026**, all undergraduate and graduate degree programs must demonstrate that
            graduates earn **MORE than the median earnings of high school graduates (aged 25-34) in their state**.

            Programs that fail this test for **2 out of 3 consecutive years** lose Title IV federal aid eligibility.
            """
        )

        st.info(
            "**💡 Key Insight:** This analysis provides institution-level risk screening to help colleges "
            "prepare for upcoming EP requirements. Actual testing will occur at the program level using IRS/SSA data."
        )

        st.markdown("")  # Spacing

        # Load summary statistics
        summary = get_risk_summary()

        # Summary statistics
        st.markdown("### National Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Institutions",
                f"{summary['total_institutions']:,}",
                help="Institutions with earnings data available"
            )

        with col2:
            at_risk_pct = (summary['at_risk_count'] / summary['total_institutions']) * 100
            st.metric(
                "At Risk",
                f"{summary['at_risk_count']:,}",
                f"{at_risk_pct:.1f}%",
                delta_color="inverse",
                help="High Risk + Critical Risk institutions"
            )

        with col3:
            critical_pct = (summary['critical_count'] / summary['total_institutions']) * 100
            st.metric(
                "Critical Risk",
                f"{summary['critical_count']:,}",
                f"{critical_pct:.1f}%",
                delta_color="inverse",
                help="Earnings below state threshold"
            )

        with col4:
            st.metric(
                "Avg Margin",
                f"{summary['avg_margin']:.1f}%",
                help="Average earnings margin above state thresholds"
            )

        st.markdown("")  # Spacing

        # Risk distribution
        st.markdown("### Risk Distribution")

        risk_df = pd.DataFrame(
            list(summary['risk_distribution'].items()),
            columns=['Risk Level', 'Count']
        ).sort_values('Count', ascending=False)

        # Color mapping
        risk_colors = {
            'Low Risk': '#2ca02c',
            'Moderate Risk': '#1f77b4',
            'High Risk': '#ff7f0e',
            'Critical Risk': '#d62728',
            'No Data': '#7f7f7f'
        }

        risk_df['Color'] = risk_df['Risk Level'].map(risk_colors)

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.bar(
                risk_df,
                x='Risk Level',
                y='Count',
                color='Risk Level',
                color_discrete_map=risk_colors,
                title="Institutions by Risk Level"
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Risk Categories")
            for _, row in risk_df.iterrows():
                pct = (row['Count'] / summary['total_institutions']) * 100
                st.markdown(
                    f"<div style='padding: 0.5rem; margin-bottom: 0.5rem; background-color: {row['Color']}15; "
                    f"border-left: 4px solid {row['Color']};'>"
                    f"<strong>{row['Risk Level']}</strong><br>"
                    f"{row['Count']:,} institutions ({pct:.1f}%)"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.divider()

        # What to explore
        st.markdown("### What You Can Explore")
        st.markdown(
            """
            - **Overview & Risk Map**: Interactive scatter plot showing all institutions' earnings vs state thresholds
            - **Institution Lookup**: Search for specific institutions and view detailed risk assessments with peer comparisons
            - **Methodology & Limitations**: Understanding the data, calculations, and critical limitations
            """
        )

        st.markdown("")  # Spacing

        # Important limitations
        st.warning(
            "**⚠️ Important Limitation:** This analysis uses institution-level median earnings (aggregated across all programs) "
            "compared to state thresholds. Actual EP testing will occur at the individual program level using IRS/SSA data "
            "not publicly available. This tool provides directional risk assessment for planning purposes only."
        )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Earnings Premium chart."""
        self.render_section_header(EARNINGS_PREMIUM_SECTION, chart_name)

        if chart_name == EP_OVERVIEW_RISK_MAP_LABEL:
            self._render_overview_risk_map()
        elif chart_name == EP_INSTITUTION_LOOKUP_LABEL:
            self._render_institution_lookup()
        elif chart_name == EP_METHODOLOGY_LABEL:
            self._render_methodology()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_overview_risk_map(self) -> None:
        """Render the Overview & Risk Map page."""
        st.markdown("## Overview & Risk Map")
        st.markdown(
            """
            This interactive scatter plot shows how all U.S. institutions compare to their state's
            Earnings Premium threshold. Each dot represents an institution, color-coded by risk level.
            """
        )

        st.markdown("")  # Spacing

        # Load data
        df = load_ep_data()
        df_plot = df[df['risk_level'] != 'No Data'].copy()

        # Filters
        st.markdown("### Filters")
        col1, col2, col3 = st.columns(3)

        with col1:
            risk_filter = st.multiselect(
                "Risk Level",
                options=['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk'],
                default=['Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk'],
                key="ep_risk_filter"
            )

        with col2:
            sector_options = df_plot['sector_name'].dropna().unique().tolist()
            sector_filter = st.multiselect(
                "Sector",
                options=sector_options,
                default=sector_options,
                key="ep_sector_filter"
            )

        with col3:
            state_options = sorted(df_plot['STABBR'].dropna().unique().tolist())
            state_filter = st.multiselect(
                "State",
                options=state_options,
                default=state_options,
                key="ep_state_filter"
            )

        # Apply filters
        if risk_filter:
            df_plot = df_plot[df_plot['risk_level'].isin(risk_filter)]
        if sector_filter:
            df_plot = df_plot[df_plot['sector_name'].isin(sector_filter)]
        if state_filter:
            df_plot = df_plot[df_plot['STABBR'].isin(state_filter)]

        st.markdown(f"**Showing {len(df_plot):,} institutions**")

        st.markdown("")  # Spacing

        # Create scatter plot
        risk_colors = {
            'Low Risk': '#2ca02c',
            'Moderate Risk': '#1f77b4',
            'High Risk': '#ff7f0e',
            'Critical Risk': '#d62728'
        }

        fig = px.scatter(
            df_plot,
            x='Threshold',
            y='median_earnings',
            color='risk_level',
            color_discrete_map=risk_colors,
            hover_data={
                'institution': True,
                'STABBR': True,
                'sector_name': True,
                'Threshold': ':$,.0f',
                'median_earnings': ':$,.0f',
                'earnings_margin_pct': ':.1f%',
                'risk_level': True
            },
            title="Institutional Earnings vs State Thresholds",
            labels={
                'Threshold': 'State EP Threshold ($)',
                'median_earnings': 'Institutional Median Earnings ($)',
                'risk_level': 'Risk Level'
            },
            height=600
        )

        # Add reference line (y = x)
        max_val = max(df_plot['Threshold'].max(), df_plot['median_earnings'].max())
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                line=dict(dash='dash', color='gray', width=2),
                name='Earnings = Threshold',
                showlegend=True
            )
        )

        fig.update_layout(
            xaxis_title="State EP Threshold ($)",
            yaxis_title="Institutional Median Earnings ($)",
            legend_title="Risk Level"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "_Data Sources: College Scorecard (median earnings 10 years after entry), "
            "Federal Register (state EP thresholds), IPEDS (institutional characteristics)._"
        )

        st.markdown("")  # Spacing

        # Download data
        st.markdown("### Download Data")

        csv = df_plot.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data (CSV)",
            data=csv,
            file_name="ep_analysis_filtered.csv",
            mime="text/csv",
            key="ep_download_csv"
        )

    def _render_institution_lookup(self) -> None:
        """Render the Institution Lookup page."""
        st.markdown("## Institution Lookup")
        st.markdown(
            """
            Search for a specific institution to view its Earnings Premium risk assessment
            and compare it to peer institutions in the same state and sector.
            """
        )

        st.markdown("")  # Spacing

        # Search interface
        df = load_ep_data()

        # Create institution list for selectbox
        institutions = df[['UnitID', 'institution', 'STABBR']].copy()
        institutions = institutions.sort_values('institution')
        institutions['display'] = institutions['institution'] + ' (' + institutions['STABBR'] + ')'

        selected_display = st.selectbox(
            "Search for an institution:",
            options=institutions['display'].tolist(),
            key="ep_institution_search"
        )

        if selected_display:
            # Get selected institution
            selected_idx = institutions[institutions['display'] == selected_display].index[0]
            selected_unitid = institutions.loc[selected_idx, 'UnitID']

            institution = get_institution_by_unitid(selected_unitid)

            if institution is not None:
                self._render_institution_card(institution)

                st.markdown("")  # Spacing

                # Peer comparison
                st.markdown("### Peer Comparison")
                st.markdown(
                    f"Institutions in **{institution['STABBR']}** with similar sector "
                    f"(**{institution['sector_name']}**) and enrollment:"
                )

                peers = get_peer_institutions(institution, n_peers=5)

                if not peers.empty:
                    self._render_peer_comparison(institution, peers)
                else:
                    st.info("No peer institutions found with the selected criteria.")
            else:
                st.error("Institution not found.")

    def _render_institution_card(self, institution: pd.Series) -> None:
        """Render an institution risk assessment card."""

        # Risk color
        risk_colors = {
            'Low Risk': '#2ca02c',
            'Moderate Risk': '#1f77b4',
            'High Risk': '#ff7f0e',
            'Critical Risk': '#d62728',
            'No Data': '#7f7f7f'
        }

        risk_color = risk_colors.get(institution['risk_level'], '#7f7f7f')

        # Card header
        st.markdown(
            f"""
            <div style='padding: 1rem; background: linear-gradient(135deg, {risk_color}20 0%, {risk_color}10 100%);
                border-left: 4px solid {risk_color}; border-radius: 5px; margin-bottom: 1rem;'>
                <h3 style='margin: 0; color: {risk_color};'>{institution['institution']}</h3>
                <p style='margin: 0.5rem 0 0 0; color: #495057;'>{institution['STABBR']} • {institution['sector_name']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Risk Level",
                institution['risk_level'],
                help="EP risk category based on earnings margin"
            )

        with col2:
            if pd.notna(institution['median_earnings']):
                st.metric(
                    "Median Earnings",
                    f"${institution['median_earnings']:,.0f}",
                    help="Institutional median earnings (10 years after entry)"
                )
            else:
                st.metric("Median Earnings", "No Data")

        with col3:
            if pd.notna(institution['Threshold']):
                st.metric(
                    "State Threshold",
                    f"${institution['Threshold']:,.0f}",
                    help=f"EP threshold for {institution['STABBR']}"
                )
            else:
                st.metric("State Threshold", "No Data")

        with col4:
            if pd.notna(institution['earnings_margin_pct']):
                margin_val = institution['earnings_margin_pct']
                delta_color = "normal" if margin_val > 0 else "inverse"
                st.metric(
                    "Earnings Margin",
                    f"{margin_val:.1f}%",
                    delta_color=delta_color,
                    help="Percentage above (+) or below (-) state threshold"
                )
            else:
                st.metric("Earnings Margin", "No Data")

        st.markdown("")  # Spacing

        # Additional details
        with st.expander("Additional Details"):
            col1, col2 = st.columns(2)

            with col1:
                if pd.notna(institution['enrollment']):
                    st.markdown(f"**Enrollment:** {institution['enrollment']:,.0f}")
                if pd.notna(institution['graduation_rate']):
                    st.markdown(f"**Graduation Rate:** {institution['graduation_rate']:.1f}%")

            with col2:
                if pd.notna(institution['cost']):
                    st.markdown(f"**Cost:** ${institution['cost']:,.0f}")
                st.markdown(f"**UnitID:** {institution['UnitID']}")

        # Limitations reminder
        if institution['risk_level'] != 'No Data':
            if institution['risk_level'] in ['High Risk', 'Critical Risk']:
                st.warning(
                    "⚠️ **Important:** This risk assessment uses institution-level data. "
                    "Actual EP testing occurs at the program level. Individual programs may perform "
                    "better or worse than the institutional median."
                )

    def _render_peer_comparison(self, institution: pd.Series, peers: pd.DataFrame) -> None:
        """Render peer comparison table."""

        # Prepare comparison data
        comparison_data = []

        # Add selected institution first
        comparison_data.append({
            'Institution': f"**{institution['institution']}** (Selected)",
            'Risk Level': institution['risk_level'],
            'Median Earnings': f"${institution['median_earnings']:,.0f}" if pd.notna(institution['median_earnings']) else "No Data",
            'Earnings Margin': f"{institution['earnings_margin_pct']:.1f}%" if pd.notna(institution['earnings_margin_pct']) else "No Data",
            'Enrollment': f"{institution['enrollment']:,.0f}" if pd.notna(institution['enrollment']) else "No Data"
        })

        # Add peers
        for _, peer in peers.iterrows():
            comparison_data.append({
                'Institution': peer['institution'],
                'Risk Level': peer['risk_level'],
                'Median Earnings': f"${peer['median_earnings']:,.0f}" if pd.notna(peer['median_earnings']) else "No Data",
                'Earnings Margin': f"{peer['earnings_margin_pct']:.1f}%" if pd.notna(peer['earnings_margin_pct']) else "No Data",
                'Enrollment': f"{peer['enrollment']:,.0f}" if pd.notna(peer['enrollment']) else "No Data"
            })

        comparison_df = pd.DataFrame(comparison_data)

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    def _render_methodology(self) -> None:
        """Render the Methodology & Limitations page."""
        st.markdown("## Methodology & Limitations")

        # Data sources
        st.markdown("### Data Sources")
        st.markdown(
            """
            This analysis combines data from three authoritative sources:
            """
        )

        sources_data = [
            {
                'Source': 'Federal Register',
                'Data': 'State EP Thresholds (2024)',
                'Description': 'Median earnings of HS graduates aged 25-34 by state',
                'Update': 'Annual (December 31)'
            },
            {
                'Source': 'College Scorecard',
                'Data': 'Institutional Earnings',
                'Description': 'Median earnings 10 years after entry (MD_EARN_WNE_P10)',
                'Update': 'Annual (cohort-based)'
            },
            {
                'Source': 'IPEDS',
                'Data': 'Institutional Characteristics',
                'Description': 'Sector, enrollment, graduation rates, costs',
                'Update': 'Annual (fall collection)'
            }
        ]

        sources_df = pd.DataFrame(sources_data)
        st.dataframe(sources_df, use_container_width=True, hide_index=True)

        st.markdown("")  # Spacing

        # Calculation methodology
        st.markdown("### Risk Calculation Methodology")
        st.markdown(
            """
            **Step 1: Earnings Margin Calculation**
            ```
            Earnings Margin = (Institutional Median Earnings - State Threshold) / State Threshold
            ```

            **Step 2: Risk Categorization**
            - **Low Risk**: Margin > 50% (earnings 150%+ of threshold)
            - **Moderate Risk**: Margin 20-50% (earnings 120-150% of threshold)
            - **High Risk**: Margin 0-20% (earnings 100-120% of threshold)
            - **Critical Risk**: Margin < 0% (earnings below threshold)
            - **No Data**: Missing earnings or threshold data
            """
        )

        st.markdown("")  # Spacing

        # Example calculation
        with st.expander("Example Calculation"):
            st.markdown(
                """
                **Example: UCLA**
                - State: California
                - State Threshold: $32,476
                - Institutional Median Earnings: $65,011
                - Earnings Margin: ($65,011 - $32,476) / $32,476 = 100.2%
                - Risk Level: **Low Risk** (margin > 50%)
                """
            )

        st.markdown("")  # Spacing

        # Critical limitations
        st.markdown("### Critical Limitations")

        st.error(
            """
            **⚠️ IMPORTANT:** This analysis has significant limitations that must be understood:

            1. **Institution-Level vs Program-Level**: This analysis uses institution-level median earnings
               (aggregated across all programs). Actual EP testing will occur at the individual program level.
               Programs within an institution can vary dramatically.

            2. **Data Not Used in Actual Testing**: The Department of Education will use confidential IRS/SSA
               earnings data for actual EP testing, not College Scorecard data. Results may differ.

            3. **Timing Differences**: College Scorecard uses 10-year post-entry earnings. EP regulations
               use earnings 2 years after program completion. Different cohorts, different timelines.

            4. **Coverage Gaps**: Not all institutions or programs have College Scorecard earnings data.
               Missing data does not mean EP exemption.

            5. **Planning Tool Only**: This is a directional risk assessment for strategic planning.
               Do not use as definitive compliance determination.
            """
        )

        st.markdown("")  # Spacing

        # Recommendations
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Best Practices:**
            - ✅ Use for early risk screening and strategic planning
            - ✅ Identify peer institutions for benchmarking
            - ✅ Understand state-level variations in thresholds
            - ✅ Track national trends and risk distributions
            - ❌ Do not use for definitive compliance determination
            - ❌ Do not assume institution-level results apply to all programs
            - ❌ Do not substitute for program-level analysis and planning
            """
        )

        st.markdown("")  # Spacing

        # FAQs
        st.markdown("### Frequently Asked Questions")

        with st.expander("Why use institution-level data instead of program-level?"):
            st.markdown(
                """
                Program-level earnings data from College Scorecard is available for some programs,
                but coverage is incomplete and may not match the exact definitions used in EP regulations.
                Institution-level data provides broader coverage for initial screening, with the understanding
                that program-level analysis is needed for actual compliance.
                """
            )

        with st.expander("What if my institution shows 'No Data'?"):
            st.markdown(
                """
                'No Data' means College Scorecard does not have median earnings data for your institution.
                This could be due to insufficient sample sizes, privacy suppression, or reporting gaps.
                Lack of data in this tool does NOT exempt your institution from EP requirements.
                """
            )

        with st.expander("How often is this data updated?"):
            st.markdown(
                """
                - State thresholds: Updated annually by the Department of Education (typically December 31)
                - College Scorecard data: Updated annually (typically fall release)
                - IPEDS data: Updated annually (fall collection period)

                This dashboard will be updated as new data becomes available.
                """
            )

        with st.expander("My institution is 'Critical Risk' - what should I do?"):
            st.markdown(
                """
                'Critical Risk' indicates that institutional median earnings are below your state's threshold.
                This suggests potential EP compliance challenges, but remember:

                1. Actual testing is at the program level - some programs may pass even if the institution
                   shows critical risk
                2. You have until July 1, 2026 to improve outcomes or adjust program offerings
                3. Consult with your compliance office and financial aid administrators
                4. Consider program-level analysis using available data and internal records
                """
            )

    def get_available_charts(self) -> List[str]:
        """Get available charts for Earnings Premium section."""
        return [
            EP_OVERVIEW_RISK_MAP_LABEL,
            EP_INSTITUTION_LOOKUP_LABEL,
            EP_METHODOLOGY_LABEL,
        ]
