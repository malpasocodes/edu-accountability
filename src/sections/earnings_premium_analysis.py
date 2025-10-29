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
    EP_NATIONAL_OVERVIEW_LABEL,
    EP_OVERVIEW_RISK_MAP_LABEL,
    EP_INSTITUTION_LOOKUP_LABEL,
    EP_STATE_ANALYSIS_LABEL,
    EP_SECTOR_COMPARISON_LABEL,
    EP_RISK_QUADRANTS_LABEL,
    EP_PROGRAM_DISTRIBUTION_LABEL,
    EP_METHODOLOGY_LABEL,
)
from src.core.ep_data_loader import (
    load_ep_data,
    load_state_thresholds,
    get_risk_summary,
    get_national_summary,
    get_state_summary,
    get_sector_summary,
    get_all_states,
    get_all_sectors,
    search_institutions,
    get_institution_by_unitid,
    get_peer_institutions,
    filter_by_state,
    filter_by_sector,
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

        # Important Limitation at top
        from src.ui.disclaimer import load_disclaimer_content

        st.markdown('<h4 style="color: red;">⚠️ Important Limitation</h4>', unsafe_allow_html=True)
        st.markdown(
            """
            The analyses and visualizations below rely on **institution-level median earnings** rather than **program-level data**.
            Federal gainful employment and accountability tests (such as EP or D/E) are based on **program-specific earnings** drawn from **IRS and SSA administrative records**, which are **not publicly accessible**.

            As a result, these results are **approximate and non-authoritative**. They **must not be interpreted as official compliance assessments, rankings, or findings**.
            They are provided **for research and policy discussion purposes only**, and their use implies acceptance of the <span style="color: red;">Full Disclaimer & Terms of Use</span>.
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

        st.markdown("")  # Spacing

        # What is Earnings Premium
        st.markdown("### What is the Earnings Premium Test?")
        st.markdown(
            """
            On July 4, 2025, President Trump signed the "One Big Beautiful Bill" as part of budget reconciliation,
            fundamentally transforming accountability requirements for American higher education. The law amended
            the Higher Education Act of 1965 to create a new "earnings premium" (EP) metric that will assess the
            effectiveness of all degree programs at all universities receiving Title IV federal student aid funds.
            """
        )

        st.markdown("#### Test 1: The Earnings Premium Test")
        st.markdown("**Question:** Do your graduates earn more than people who didn't pursue your type of credential?")

        st.markdown(
            """
            **For undergraduate programs:** Graduates' median earnings must exceed the median earnings of high school
            graduates (aged 25-34) in the state where the institution is located. These state thresholds range from
            $27,362 in Mississippi to $37,850 in New Hampshire, with a national threshold of $31,269.

            **For graduate programs:** Graduates' median earnings must exceed the lowest of three benchmarks:
            1. Bachelor's degree holders in the state
            2. Workers in the same field statewide
            3. Workers in the same field nationally

            **Measurement:** The Department of Education will measure earnings 2, 3, and 4 years after program completion
            using IRS and Social Security Administration data. Programs must pass in at least 2 out of 3 years.

            **Effective Date:** July 1, 2026
            """
        )

        st.info(
            "**💡 Key Insight:** This analysis provides institution-level risk screening to help colleges "
            "prepare for upcoming EP requirements. Actual testing will occur at the program level using IRS/SSA data."
        )

        st.markdown("")  # Spacing

        # Risk category definitions
        st.markdown("### Risk Category Definitions")
        st.markdown("Institutions are classified based on how their median graduate earnings compare to their state's EP threshold:")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div style='padding: 1rem; border: 2px solid #2ca02c; border-radius: 8px; margin-bottom: 1rem; background-color: #2ca02c15;'>
                    <h4 style='margin-top: 0; color: #2ca02c;'>✓ Very Low Risk</h4>
                    <p style='margin: 0.25rem 0;'><strong>Margin:</strong> > 50%</p>
                    <p style='margin: 0.25rem 0;'><strong>Earnings:</strong> 150%+ of state threshold</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div style='padding: 1rem; border: 2px solid #ff7f0e; border-radius: 8px; margin-bottom: 1rem; background-color: #ff7f0e15;'>
                    <h4 style='margin-top: 0; color: #ff7f0e;'>⚠ Moderate Risk</h4>
                    <p style='margin: 0.25rem 0;'><strong>Margin:</strong> 0-20%</p>
                    <p style='margin: 0.25rem 0;'><strong>Earnings:</strong> 100-120% of threshold</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1rem; border: 2px solid #1f77b4; border-radius: 8px; margin-bottom: 1rem; background-color: #1f77b415;'>
                    <h4 style='margin-top: 0; color: #1f77b4;'>○ Low Risk</h4>
                    <p style='margin: 0.25rem 0;'><strong>Margin:</strong> 20-50%</p>
                    <p style='margin: 0.25rem 0;'><strong>Earnings:</strong> 120-150% of threshold</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div style='padding: 1rem; border: 2px solid #d62728; border-radius: 8px; margin-bottom: 1rem; background-color: #d6272815;'>
                    <h4 style='margin-top: 0; color: #d62728;'>✕ High Risk</h4>
                    <p style='margin: 0.25rem 0;'><strong>Margin:</strong> < 0%</p>
                    <p style='margin: 0.25rem 0;'><strong>Earnings:</strong> Below state threshold</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # What to explore
        st.markdown("### What You Can Explore")
        st.markdown(
            """
            - **Risk Distribution**: National summary metrics and risk distribution across all institutions
            - **Risk Map**: Interactive scatter plot showing all institutions' earnings vs state thresholds
            - **Risk Quadrants**: Scatter plots by risk category with sector colors
            - **Sector Comparison**: Compare risk across institutional types
            - **State Analysis**: Deep dive into EP risk by state
            - **Program Distribution**: Scale of program-level EP assessment requirements
            - **Institution Lookup**: Search institutions and view detailed risk assessments
            - **Methodology & Limitations**: Data sources, calculations, and critical limitations
            """
        )

        st.markdown("")  # Spacing

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Earnings Premium chart."""
        self.render_section_header(EARNINGS_PREMIUM_SECTION, chart_name)

        if chart_name == EP_NATIONAL_OVERVIEW_LABEL:
            self._render_national_overview()
        elif chart_name == EP_OVERVIEW_RISK_MAP_LABEL:
            self._render_overview_risk_map()
        elif chart_name == EP_INSTITUTION_LOOKUP_LABEL:
            self._render_institution_lookup()
        elif chart_name == EP_STATE_ANALYSIS_LABEL:
            self._render_state_analysis()
        elif chart_name == EP_SECTOR_COMPARISON_LABEL:
            self._render_sector_comparison()
        elif chart_name == EP_RISK_QUADRANTS_LABEL:
            self._render_risk_quadrants()
        elif chart_name == EP_PROGRAM_DISTRIBUTION_LABEL:
            self._render_program_distribution()
        elif chart_name == EP_METHODOLOGY_LABEL:
            self._render_methodology()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_national_overview(self) -> None:
        """Render the Risk Distribution page with summary metrics and institution lists."""
        st.markdown("## 📊 Risk Distribution")
        st.markdown(
            """
            This page provides a comprehensive snapshot of Earnings Premium risk across all U.S. institutions
            with available data. Review key metrics and the distribution of institutions by risk level.
            """
        )

        st.markdown("")  # Spacing

        # Load summary statistics
        summary = get_risk_summary()

        # Summary metrics
        st.markdown("### Key Metrics")

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
                help="Moderate Risk + High Risk institutions"
            )

        with col3:
            high_risk_pct = (summary['high_risk_count'] / summary['total_institutions']) * 100
            st.metric(
                "High Risk",
                f"{summary['high_risk_count']:,}",
                f"{high_risk_pct:.1f}%",
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
        st.markdown("### Institution Count by Risk Level")

        risk_df = pd.DataFrame(
            list(summary['risk_distribution'].items()),
            columns=['Risk Level', 'Count']
        ).sort_values('Count', ascending=False)

        # Color mapping
        risk_colors = {
            'Very Low Risk': '#2ca02c',
            'Low Risk': '#1f77b4',
            'Moderate Risk': '#ff7f0e',
            'High Risk': '#d62728',
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
                color_discrete_map=risk_colors
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

        st.markdown("")  # Spacing

        # Institutions by Risk Category (Tabs)
        st.markdown("### Institutions by Risk Category")
        st.markdown("Click a tab to view all institutions in each risk level.")

        # Load full dataset
        df = load_ep_data()

        # Create tabs for each risk level
        risk_levels = ['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk', 'No Data']
        tabs = st.tabs(risk_levels)

        for tab, risk_level in zip(tabs, risk_levels):
            with tab:
                # Filter by risk level
                risk_df = df[df['risk_level'] == risk_level].copy()

                if not risk_df.empty:
                    # Show count
                    st.markdown(f"**{len(risk_df):,} institutions in {risk_level}**")

                    st.markdown("")  # Spacing

                    # Prepare display dataframe
                    display_cols = ['institution', 'STABBR', 'median_earnings', 'Threshold', 'earnings_margin_pct', 'sector_name', 'enrollment']
                    display_df = risk_df[display_cols].copy()

                    # Sort by earnings margin (best first for Very Low/Low, worst first for Moderate/High)
                    if risk_level in ['Very Low Risk', 'Low Risk']:
                        display_df = display_df.sort_values('earnings_margin_pct', ascending=False)
                    else:
                        display_df = display_df.sort_values('earnings_margin_pct', ascending=True)

                    # Rename columns
                    display_df.columns = ['Institution', 'State', 'Median Earnings', 'State Threshold', 'Margin (%)', 'Sector', 'Enrollment']

                    # Format columns
                    display_df['Median Earnings'] = display_df['Median Earnings'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) else "No Data"
                    )
                    display_df['State Threshold'] = display_df['State Threshold'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) else "No Data"
                    )
                    display_df['Margin (%)'] = display_df['Margin (%)'].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "No Data"
                    )
                    display_df['Enrollment'] = display_df['Enrollment'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "No Data"
                    )

                    # Display table
                    st.dataframe(display_df, width="stretch", hide_index=True, height=500)

                    # Download button
                    csv = risk_df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {risk_level} Data (CSV)",
                        data=csv,
                        file_name=f"ep_national_{risk_level.replace(' ', '_').lower()}.csv",
                        mime="text/csv",
                        key=f"national_overview_{risk_level.replace(' ', '_').lower()}_download"
                    )
                else:
                    st.info(f"No institutions found in {risk_level}.")

        st.divider()

        # Navigation guidance
        st.markdown("### Dive Deeper")
        st.markdown(
            """
            - **Overview & Risk Map**: Interactive scatter plot showing all institutions' earnings vs state thresholds
            - **Institution Lookup**: Search for specific institutions and view detailed risk assessments
            - **State Analysis**: Explore EP risk patterns by state
            - **Sector Comparison**: Compare risk across institutional types
            - **Risk Quadrants**: Visualize institutions by risk category with sector breakdowns
            """
        )

    def _render_overview_risk_map(self) -> None:
        """Render the Risk Map page."""
        st.markdown("## Risk Map")
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
                options=['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk'],
                default=['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk'],
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
            'Very Low Risk': '#2ca02c',
            'Low Risk': '#1f77b4',
            'Moderate Risk': '#ff7f0e',
            'High Risk': '#d62728'
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
        institutions['display'] = institutions['institution'] + ' (' + institutions['STABBR'].astype(str) + ')'

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
            'Very Low Risk': '#2ca02c',
            'Low Risk': '#1f77b4',
            'Moderate Risk': '#ff7f0e',
            'High Risk': '#d62728',
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

        st.dataframe(comparison_df, width="stretch", hide_index=True)

    def _render_state_analysis(self) -> None:
        """Render the State Analysis page."""
        st.markdown("## State Analysis")
        st.markdown(
            """
            Explore EP risk landscape by state to understand how institutions in each
            state compare to their state-specific threshold.
            """
        )

        st.markdown("")  # Spacing

        # State selector
        states = ['National Overview'] + get_all_states()
        selected_state = st.selectbox(
            "Select a state to analyze:",
            options=states,
            key="ep_state_selector"
        )

        if selected_state == 'National Overview':
            # Show national summary
            national = get_national_summary()
            st.markdown("### National Overview")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("National Threshold", f"${national['national_threshold']:,.0f}")
            with col2:
                st.metric("Total Institutions", f"{national['total_institutions']:,}")
            with col3:
                st.metric("At Risk", f"{national['at_risk_pct']:.1f}%")
            with col4:
                st.metric("Avg Margin", f"{national['avg_margin']:.1f}%")

            st.markdown("")  # Spacing

            # National risk distribution
            st.markdown("### National Risk Distribution")
            risk_df = pd.DataFrame(
                list(national['risk_distribution'].items()),
                columns=['Risk Level', 'Count']
            ).sort_values('Count', ascending=False)

            risk_colors = {
                'Very Low Risk': '#2ca02c',
                'Low Risk': '#1f77b4',
                'Moderate Risk': '#ff7f0e',
                'High Risk': '#d62728',
                'No Data': '#7f7f7f'
            }

            fig = px.bar(
                risk_df,
                x='Risk Level',
                y='Count',
                color='Risk Level',
                color_discrete_map=risk_colors,
                title="National Risk Distribution"
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        else:
            # Show state-specific analysis
            state_summary = get_state_summary(selected_state)

            if state_summary is None:
                st.warning(f"No data available for {selected_state}")
                return

            # State summary card
            st.markdown(f"### {selected_state} Earnings Premium Analysis")

            # Rank state threshold
            thresholds = load_state_thresholds()
            sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)
            state_rank = next(i for i, (st_abbr, _) in enumerate(sorted_thresholds, 1) if st_abbr == selected_state)

            st.markdown(
                f"""
                <div style='padding: 1.5rem; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    border-radius: 10px; margin-bottom: 1.5rem;'>
                    <h4 style='margin-top: 0;'>State EP Threshold: ${state_summary['state_threshold']:,.0f}</h4>
                    <p style='margin: 0;'>Ranked <strong>#{state_rank}</strong> highest nationally (out of 52)</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Institutions in State", f"{state_summary['total_institutions']:,}")

            with col2:
                if state_summary['median_earnings']:
                    st.metric("Median Earnings", f"${state_summary['median_earnings']:,.0f}")
                else:
                    st.metric("Median Earnings", "No Data")

            with col3:
                if state_summary['avg_margin'] is not None:
                    st.metric("Average Margin", f"{state_summary['avg_margin']:.1f}%")
                else:
                    st.metric("Average Margin", "No Data")

            st.markdown("")  # Spacing

            # Risk distribution for state
            st.markdown("#### Risk Distribution")
            risk_dist = state_summary['risk_distribution']

            for risk_level in ['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk']:
                count = risk_dist.get(risk_level, 0)
                pct = (count / state_summary['total_institutions'] * 100) if state_summary['total_institutions'] > 0 else 0
                st.markdown(f"• **{risk_level}**: {count:,} ({pct:.1f}%)")

            st.markdown("")  # Spacing

            # State institutions table
            st.markdown("### Institutions in State")

            state_df = filter_by_state([selected_state])
            state_df_display = state_df[state_df['risk_level'] != 'No Data'].copy()

            if not state_df_display.empty:
                # Filters
                col1, col2 = st.columns(2)

                with col1:
                    sector_options = state_df_display['sector_name'].dropna().unique().tolist()
                    sector_filter = st.multiselect(
                        "Filter by Sector",
                        options=sector_options,
                        default=sector_options,
                        key="state_sector_filter"
                    )

                with col2:
                    risk_filter = st.multiselect(
                        "Filter by Risk Level",
                        options=['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk'],
                        default=['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk'],
                        key="state_risk_filter"
                    )

                # Apply filters
                if sector_filter:
                    state_df_display = state_df_display[state_df_display['sector_name'].isin(sector_filter)]
                if risk_filter:
                    state_df_display = state_df_display[state_df_display['risk_level'].isin(risk_filter)]

                st.markdown(f"**Showing {len(state_df_display):,} institutions**")

                # Display table
                display_cols = ['institution', 'sector_name', 'median_earnings', 'earnings_margin_pct', 'risk_level', 'enrollment']
                display_df = state_df_display[display_cols].copy()
                display_df.columns = ['Institution', 'Sector', 'Median Earnings', 'Margin (%)', 'Risk Level', 'Enrollment']

                # Format columns
                display_df['Median Earnings'] = display_df['Median Earnings'].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) else "No Data"
                )
                display_df['Margin (%)'] = display_df['Margin (%)'].apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "No Data"
                )
                display_df['Enrollment'] = display_df['Enrollment'].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else "No Data"
                )

                st.dataframe(display_df, width="stretch", hide_index=True)

                # Download button
                csv = state_df_display.to_csv(index=False)
                st.download_button(
                    label=f"Download {selected_state} Data (CSV)",
                    data=csv,
                    file_name=f"ep_analysis_{selected_state}.csv",
                    mime="text/csv",
                    key="state_download_csv"
                )
            else:
                st.info("No institutions with risk assessments found for the selected filters.")

            st.markdown("")  # Spacing

            # State comparison
            st.markdown("### Comparison to National Average")

            national = get_national_summary()

            comparison_data = {
                'Metric': ['EP Threshold', '% At Risk', 'Median Earnings'],
                'State': [
                    f"${state_summary['state_threshold']:,.0f}",
                    f"{len(state_df_display[state_df_display['risk_level'].isin(['High Risk', 'Critical Risk'])]) / len(state_df_display) * 100:.1f}%" if not state_df_display.empty else "No Data",
                    f"${state_summary['median_earnings']:,.0f}" if state_summary['median_earnings'] else "No Data"
                ],
                'National': [
                    f"${national['national_threshold']:,.0f}",
                    f"{national['at_risk_pct']:.1f}%",
                    f"${national['median_earnings']:,.0f}"
                ]
            }

            st.table(pd.DataFrame(comparison_data))

    def _render_sector_comparison(self) -> None:
        """Render the Sector Comparison page."""
        st.markdown("## Sector Comparison")
        st.markdown(
            """
            Compare EP risk across different types of institutions to understand
            which sectors face the greatest compliance challenges.
            """
        )

        st.markdown("")  # Spacing

        # Sector overview cards
        st.markdown("### Sector Overview")

        sectors = get_all_sectors()

        # Create grid layout
        cols_per_row = 3
        rows = [sectors[i:i+cols_per_row] for i in range(0, len(sectors), cols_per_row)]

        for row in rows:
            cols = st.columns(len(row))
            for col, sector in zip(cols, row):
                summary = get_sector_summary(sector)
                if summary:
                    with col:
                        # Determine color based on at_risk_pct
                        if summary['at_risk_pct'] is not None:
                            if summary['at_risk_pct'] > 50:
                                color = '#d62728'  # Red
                            elif summary['at_risk_pct'] > 30:
                                color = '#ff7f0e'  # Orange
                            else:
                                color = '#2ca02c'  # Green
                        else:
                            color = '#7f7f7f'  # Gray

                        st.markdown(
                            f"""
                            <div style='padding: 1rem; border: 2px solid {color}; border-radius: 8px; margin-bottom: 1rem;'>
                                <h4 style='margin-top: 0; color: {color};'>{sector}</h4>
                                <p style='margin: 0.25rem 0;'><strong>Institutions:</strong> {summary['total_institutions']:,}</p>
                                <p style='margin: 0.25rem 0;'><strong>At Risk:</strong> {summary['at_risk_pct']:.1f}%</p>
                                <p style='margin: 0.25rem 0;'><strong>Avg Margin:</strong> {summary['avg_margin']:.1f}%</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        st.markdown("")  # Spacing

        # Sector risk distribution chart
        st.markdown("### Risk Distribution by Sector")

        # Prepare data for grouped bar chart
        risk_data = []
        for sector in sectors:
            summary = get_sector_summary(sector)
            if summary and 'risk_distribution' in summary:
                for risk_level, count in summary['risk_distribution'].items():
                    if risk_level != 'No Data':
                        pct = (count / summary['total_institutions'] * 100) if summary['total_institutions'] > 0 else 0
                        risk_data.append({
                            'Sector': sector,
                            'Risk Level': risk_level,
                            'Percentage': pct,
                            'Count': count
                        })

        if risk_data:
            risk_df = pd.DataFrame(risk_data)

            risk_colors = {
                'Very Low Risk': '#2ca02c',
                'Low Risk': '#1f77b4',
                'Moderate Risk': '#ff7f0e',
                'High Risk': '#d62728'
            }

            fig = px.bar(
                risk_df,
                x='Sector',
                y='Percentage',
                color='Risk Level',
                color_discrete_map=risk_colors,
                title="Risk Level Distribution by Sector",
                barmode='group',
                hover_data={'Count': True}
            )
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("")  # Spacing

        # All Institutions by Sector (Tabs)
        st.markdown("### All Institutions by Sector")
        st.markdown("Click a tab to view all institutions in that sector.")

        # Create tabs for each sector
        tab_labels = sectors
        tabs = st.tabs(tab_labels)

        for tab, sector in zip(tabs, sectors):
            with tab:
                sector_df = filter_by_sector([sector])
                sector_df_valid = sector_df[sector_df['risk_level'] != 'No Data'].copy()

                if not sector_df_valid.empty:
                    # Show count
                    st.markdown(f"**{len(sector_df_valid):,} institutions in {sector}**")

                    st.markdown("")  # Spacing

                    # Risk level filter
                    risk_options = ['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk']
                    selected_risks = st.multiselect(
                        "Filter by risk level:",
                        options=risk_options,
                        default=risk_options,
                        key=f"sector_{sector.replace(' ', '_').replace('-', '_')}_risk_filter"
                    )

                    # Apply filter
                    if selected_risks:
                        sector_df_filtered = sector_df_valid[sector_df_valid['risk_level'].isin(selected_risks)]
                    else:
                        sector_df_filtered = sector_df_valid

                    st.markdown(f"*Showing {len(sector_df_filtered):,} institutions*")

                    st.markdown("")  # Spacing

                    # Prepare display dataframe
                    display_cols = ['institution', 'STABBR', 'median_earnings', 'Threshold', 'earnings_margin_pct', 'risk_level', 'enrollment']
                    display_df = sector_df_filtered[display_cols].copy()

                    # Sort by earnings margin (best first)
                    display_df = display_df.sort_values('earnings_margin_pct', ascending=False)

                    # Rename columns
                    display_df.columns = ['Institution', 'State', 'Median Earnings', 'State Threshold', 'Margin (%)', 'Risk Level', 'Enrollment']

                    # Format columns
                    display_df['Median Earnings'] = display_df['Median Earnings'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) else "No Data"
                    )
                    display_df['State Threshold'] = display_df['State Threshold'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) else "No Data"
                    )
                    display_df['Margin (%)'] = display_df['Margin (%)'].apply(
                        lambda x: f"{x:.1f}%" if pd.notna(x) else "No Data"
                    )
                    display_df['Enrollment'] = display_df['Enrollment'].apply(
                        lambda x: f"{x:,.0f}" if pd.notna(x) else "No Data"
                    )

                    # Display table
                    st.dataframe(display_df, width="stretch", hide_index=True, height=500)

                    # Download button
                    csv = sector_df_filtered.to_csv(index=False)
                    st.download_button(
                        label=f"Download {sector} Data (CSV)",
                        data=csv,
                        file_name=f"ep_sector_{sector.replace(' ', '_').replace('-', '_')}.csv",
                        mime="text/csv",
                        key=f"sector_{sector.replace(' ', '_').replace('-', '_')}_download"
                    )
                else:
                    st.info(f"No institutions with risk assessments found in {sector}.")

    def _render_risk_quadrants(self) -> None:
        """Render the Risk Quadrants page with tabs for each risk category."""
        st.markdown("## Risk Quadrants")
        st.markdown(
            """
            Visualize how institutions in each risk category compare their earnings to state thresholds.
            Each scatter plot shows institutions color-coded by sector type.
            """
        )

        st.markdown("")  # Spacing

        # Load data
        df = load_ep_data()
        df_valid = df[df['risk_level'] != 'No Data'].copy()

        # Create tabs for each risk level
        risk_levels = ['Very Low Risk', 'Low Risk', 'Moderate Risk', 'High Risk']
        tabs = st.tabs(risk_levels)

        # Sector color mapping (consistent with dashboard patterns)
        sector_colors = {
            'Public 4-year': '#2ca02c',
            'Public 2-year': '#98df8a',
            'Private nonprofit 4-year': '#9467bd',
            'Private nonprofit 2-year': '#c5b0d5',
            'For-profit 4-year': '#ff7f0e',
            'For-profit 2-year': '#ffbb78'
        }

        for tab, risk_level in zip(tabs, risk_levels):
            with tab:
                # Filter data for this risk level
                risk_df = df_valid[df_valid['risk_level'] == risk_level].copy()

                st.markdown(f"**{len(risk_df):,} institutions in {risk_level} category**")
                st.markdown("")  # Spacing

                if not risk_df.empty:
                    # Create scatter plot
                    fig = px.scatter(
                        risk_df,
                        x='Threshold',
                        y='median_earnings',
                        color='sector_name',
                        color_discrete_map=sector_colors,
                        hover_data={
                            'institution': True,
                            'STABBR': True,
                            'sector_name': True,
                            'Threshold': ':$,.0f',
                            'median_earnings': ':$,.0f',
                            'earnings_margin_pct': ':.1f%'
                        },
                        title=f"{risk_level} Institutions: Earnings vs State Threshold",
                        labels={
                            'Threshold': 'State EP Threshold ($)',
                            'median_earnings': 'Institutional Median Earnings ($)',
                            'sector_name': 'Sector'
                        },
                        height=600
                    )

                    # Add reference line (y = x)
                    max_val = max(risk_df['Threshold'].max(), risk_df['median_earnings'].max())
                    min_val = min(risk_df['Threshold'].min(), risk_df['median_earnings'].min())

                    fig.add_trace(
                        go.Scatter(
                            x=[min_val, max_val],
                            y=[min_val, max_val],
                            mode='lines',
                            line=dict(dash='dash', color='gray', width=2),
                            name='Earnings = Threshold',
                            showlegend=True
                        )
                    )

                    fig.update_layout(
                        xaxis_title="State EP Threshold ($)",
                        yaxis_title="Institutional Median Earnings ($)",
                        legend_title="Sector"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Summary stats for this risk level
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "Median Earnings",
                            f"${risk_df['median_earnings'].median():,.0f}"
                        )
                    with col2:
                        st.metric(
                            "Median Threshold",
                            f"${risk_df['Threshold'].median():,.0f}"
                        )
                    with col3:
                        st.metric(
                            "Avg Margin",
                            f"{risk_df['earnings_margin_pct'].mean():.1f}%"
                        )

                    st.caption(
                        f"_Showing all {len(risk_df):,} institutions classified as {risk_level}. "
                        f"Points above the diagonal line exceed their state threshold._"
                    )
                else:
                    st.info(f"No institutions found in {risk_level} category.")

    def _render_program_distribution(self) -> None:
        """Render the Program Distribution analysis page."""
        st.markdown("## 📚 Program Distribution")

        st.markdown("""
        The Earnings Premium requirement assesses **each degree program individually**—not
        institutions as a whole. A "program" is defined as a specific field of study
        (6-digit CIP code) at a specific degree level at a specific institution.

        For example, UCLA's "Bachelor of Arts in Psychology" is one program, separate from
        its "Master of Arts in Psychology" and its "Bachelor of Arts in English." Each
        must demonstrate that graduates earn more than comparable non-completers.

        This page explores the scale of the data collection and monitoring effort required
        to implement Earnings Premium requirements nationwide.
        """)

        # Load data
        df = load_ep_data()

        # Filter to institutions with program count data
        df_with_programs = df[df['total_programs'] > 0].copy()

        if len(df_with_programs) == 0:
            st.error("No program count data available. Please run: python src/data/build_program_counts.py")
            return

        # Summary metrics
        st.markdown("### Key Metrics")

        num_institutions = len(df_with_programs)
        total_programs = df_with_programs['total_programs'].sum()
        assessable_programs = df_with_programs['assessable_programs'].sum()
        max_programs_inst = df_with_programs.loc[df_with_programs['total_programs'].idxmax()]
        data_points_3yr = total_programs * 3  # 3 years of tracking per program

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Number of Institutions",
                f"{num_institutions:,}",
                help="Institutions with program-level completions data"
            )

        with col2:
            st.metric(
                "Total Programs Subject to EP",
                f"{total_programs:,.0f}",
                help="Each program (field + level + institution) must be assessed separately"
            )

        with col3:
            st.metric(
                "Large Enough for Assessment",
                f"{assessable_programs:,.0f}",
                f"{assessable_programs/total_programs*100:.0f}%",
                help="Programs with sufficient completers (30+) for reliable median calculation"
            )

        with col4:
            inst_name = max_programs_inst['institution']
            if len(inst_name) > 25:
                inst_name = inst_name[:25] + "..."
            st.metric(
                "Largest Portfolio",
                inst_name,
                f"{max_programs_inst['total_programs']:.0f} programs",
                help="Institution with the most degree programs"
            )

        with col5:
            st.metric(
                "Data Points to Track",
                f"{data_points_3yr:,.0f}",
                "3 years × programs",
                help="ED must track earnings for 3 consecutive years per program"
            )

        st.markdown("---")

        # Program distribution histogram
        st.markdown("### How Many Programs Must Be Assessed?")

        st.markdown("""
        This histogram shows how program counts are distributed across institutions.
        Most institutions have 25-75 programs, but large research universities may
        have 150-267 programs, each requiring separate EP assessment.
        """)

        # Create bins
        bins = [0, 25, 50, 75, 100, 150, 200, df_with_programs['total_programs'].max() + 1]
        labels = ['0-25', '25-50', '50-75', '75-100', '100-150', '150-200', '200+']

        df_with_programs['program_bin'] = pd.cut(df_with_programs['total_programs'], bins=bins, labels=labels, right=False)

        # Count institutions per bin
        bin_counts = df_with_programs['program_bin'].value_counts().sort_index()

        # Create histogram
        fig = go.Figure(data=[
            go.Bar(
                x=bin_counts.index.astype(str),
                y=bin_counts.values,
                text=bin_counts.values,
                textposition='auto',
                marker_color='steelblue',
                hovertemplate='<b>%{x} programs</b><br>%{y} institutions<extra></extra>'
            )
        ])

        fig.update_layout(
            xaxis_title="Number of Programs per Institution",
            yaxis_title="Number of Institutions",
            height=400,
            showlegend=False,
            hovermode='x'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary statistics below chart
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Median Programs", f"{df_with_programs['total_programs'].median():.0f}")

        with col2:
            st.metric("Mean Programs", f"{df_with_programs['total_programs'].mean():.0f}")

        with col3:
            st.metric("Institutions with 100+", f"{len(df_with_programs[df_with_programs['total_programs'] >= 100]):,}")

        with col4:
            st.metric("Institutions with 200+", f"{len(df_with_programs[df_with_programs['total_programs'] >= 200]):,}")

        st.markdown("---")

        # Sector breakdown
        st.markdown("### Program Distribution by Sector")

        st.markdown("""
        Different institutional sectors have vastly different program portfolios.
        Public research universities typically have the largest portfolios, while
        for-profit institutions tend to be more focused with fewer programs.
        """)

        # Aggregate by sector
        sector_stats = df_with_programs.groupby('sector_name').agg({
            'institution': 'count',
            'total_programs': ['sum', 'mean', 'median']
        }).round(0)

        sector_stats.columns = ['Institutions', 'Total Programs', 'Avg Programs', 'Median Programs']
        sector_stats = sector_stats.sort_values('Total Programs', ascending=False)

        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=sector_stats.index,
                x=sector_stats['Total Programs'],
                orientation='h',
                text=sector_stats['Total Programs'].astype(int),
                textposition='auto',
                marker_color='steelblue',
                hovertemplate='<b>%{y}</b><br>' +
                             'Total Programs: %{x:,.0f}<br>' +
                             'Institutions: %{customdata[0]:,.0f}<br>' +
                             'Avg per Institution: %{customdata[1]:.0f}<br>' +
                             'Median per Institution: %{customdata[2]:.0f}<extra></extra>',
                customdata=sector_stats[['Institutions', 'Avg Programs', 'Median Programs']].values
            )
        ])

        fig.update_layout(
            xaxis_title="Total Programs in Sector",
            yaxis_title="",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Table below chart
        st.markdown("**Detailed Sector Statistics:**")
        st.dataframe(
            sector_stats.style.format({
                'Institutions': '{:,.0f}',
                'Total Programs': '{:,.0f}',
                'Avg Programs': '{:.0f}',
                'Median Programs': '{:.0f}'
            }),
            width="stretch"
        )

        st.markdown("---")

        # Top institutions table
        st.markdown("### Top 25 Institutions by Program Count")

        st.markdown("""
        These institutions face the largest compliance burden, with each program
        requiring separate earnings tracking, monitoring, and potential enforcement actions.
        """)

        # Select top 25
        top_25 = df_with_programs.nlargest(25, 'total_programs')[
            ['institution', 'STABBR', 'sector_name', 'total_programs',
             'assessable_programs', 'total_completions']
        ].copy()

        # Calculate data points
        top_25['data_points_3yr'] = top_25['total_programs'] * 3

        # Reset index for display (1-based)
        top_25 = top_25.reset_index(drop=True)
        top_25.index = top_25.index + 1

        # Rename columns for display
        top_25.columns = [
            'Institution',
            'State',
            'Sector',
            'Total Programs',
            'Assessable Programs',
            'Total Completions',
            'Data Points (3 years)'
        ]

        # Display table
        st.dataframe(
            top_25.style.format({
                'Total Programs': '{:.0f}',
                'Assessable Programs': '{:.0f}',
                'Total Completions': '{:,.0f}',
                'Data Points (3 years)': '{:,.0f}'
            }),
            width="stretch",
            height=600
        )

        # Summary
        total_top_25_programs = top_25['Total Programs'].sum()
        total_top_25_datapoints = top_25['Data Points (3 years)'].sum()

        st.caption(f"""
        These 25 institutions alone account for **{total_top_25_programs:,.0f} programs** requiring
        individual assessment, representing **{total_top_25_datapoints:,.0f} data points**
        to track over the 3-year compliance window.
        """)

        st.markdown("---")

        # The data challenge explainer
        st.markdown("### The Data Collection Challenge")

        total_institutions = len(df_with_programs)

        st.markdown(f"""
        #### To Implement Earnings Premium Requirements, the Department of Education Must:

        📊 **Track {total_programs:,.0f} individual programs** across {total_institutions:,} institutions

        📅 **Monitor earnings for 3 consecutive years per program** (years 2, 3, and 4 after completion)

        👥 **Match millions of graduates to IRS/SSA wage records** annually

        🎯 **Calculate program-specific medians** (minimum 30 graduates per cohort for reliable data)

        📧 **Notify institutions within 30 days** when programs fail either metric

        📋 **Process appeals and recalculations** for contested determinations

        🔄 **Repeat this process annually, indefinitely**

        ---

        #### Scale Comparison: Institutional vs. Program-Level Data

        | System | Data Points | Granularity | Update Frequency |
        |--------|-------------|-------------|------------------|
        | **College Scorecard** | ~6,000 institutions | Aggregate across all programs | Annual |
        | **Earnings Premium** | ~{total_programs:,.0f} programs | Individual program-level | Annual (3-year rolling) |
        | **Multiplier** | **{total_programs/6000:.0f}× more data points** | Program-specific tracking | Continuous compliance monitoring |

        ---

        #### The Data Infrastructure Gap

        This dashboard provides **institutional-level** risk estimates precisely because
        program-level earnings data is currently:

        - **Not publicly available** - IRS and Social Security Administration wage records are confidential
        - **Computationally intensive** to generate and maintain at scale ({data_points_3yr:,.0f}+ data points)
        - **Subject to privacy suppression** for small programs with fewer than 30 graduates
        - **Not yet systematically collected** in the format required by EP regulations

        The Department of Education will need to build this comprehensive data infrastructure—
        capable of tracking and monitoring hundreds of thousands of programs—while simultaneously
        using it to enforce accountability measures affecting billions in federal student aid.
        """)

        # Comparative context box
        st.info(f"""
        💡 **Context for Scale**: The entire IPEDS data collection system currently gathers
        approximately 100-200 institutional data elements per institution annually. The Earnings
        Premium requirement effectively creates **{total_programs:,.0f} new "institutional units"**
        (programs) requiring ongoing earnings monitoring, compliance tracking, and potential
        enforcement actions—each with multiple years of data to maintain.
        """)

        # Timeline consideration
        st.warning("""
        ⏱️ **Timeline Consideration**: The law requires implementation by **July 1, 2026**,
        with the first assessments evaluating graduates who completed as early as 2022. This
        means ED must build the data infrastructure, establish calculation methodologies,
        create the compliance monitoring system, and begin enforcement—all within the timeframe
        since the law was signed (July 1, 2024).
        """)

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
        st.dataframe(sources_df, width="stretch", hide_index=True)

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
            EP_NATIONAL_OVERVIEW_LABEL,
            EP_OVERVIEW_RISK_MAP_LABEL,
            EP_INSTITUTION_LOOKUP_LABEL,
            EP_STATE_ANALYSIS_LABEL,
            EP_SECTOR_COMPARISON_LABEL,
            EP_RISK_QUADRANTS_LABEL,
            EP_PROGRAM_DISTRIBUTION_LABEL,
            EP_METHODOLOGY_LABEL,
        ]
