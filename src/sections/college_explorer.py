"""College Explorer section implementation."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

from .base import BaseSection
from src.ui.renderers import render_altair_chart
from src.config.constants import (
    COLLEGE_EXPLORER_OVERVIEW_LABEL,
    COLLEGE_SUMMARY_LABEL,
    COLLEGE_LOANS_PELL_LABEL,
    COLLEGE_GRAD_RATES_LABEL,
    COLLEGE_DISTANCE_ED_LABEL,
    COLLEGE_EXPLORER_CHARTS,
)


class CollegeExplorerSection(BaseSection):
    """Handles the college explorer section for individual institution data."""

    def __init__(self, data_manager):
        """Initialize the section with institutions data."""
        super().__init__(data_manager)
        self.institutions_df = data_manager.institutions_df if hasattr(data_manager, 'institutions_df') else pd.DataFrame()
        self.distance_df = data_manager.get_distance_data() if hasattr(data_manager, 'get_distance_data') else None
        self.pellgradrates_df = data_manager.pellgradrates_df if hasattr(data_manager, 'pellgradrates_df') else None

    def render_overview(self) -> None:
        """Render the college explorer overview page."""
        self.render_section_header("College Explorer", "Overview")

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    🔍 College Explorer Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Dive into institution-level profiles that blend enrollment, aid, and outcomes data.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Key insight callout
        st.info("**💡 Key Insight:** The College Explorer provides detailed analysis of individual institutions, allowing you to examine specific colleges' enrollment patterns, federal aid trends, and graduation outcomes over time.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is College Explorer?")
        st.markdown(
            """
            The College Explorer allows you to **dive deep into individual institutions** with comprehensive data
            on specific colleges and universities. Instead of comparing across many institutions, you can focus on
            a single college to understand its unique characteristics, performance metrics, and trends over time.

            This tool integrates data from **6,050+ institutions** across the United States, providing detailed
            institutional profiles with enrollment metrics, federal aid patterns, and graduation outcomes.
            """
        )

        st.divider()

        # Available analyses section
        st.markdown("### Four Ways to Explore Individual Colleges")
        st.markdown(
            """
            Use the **sidebar tabs** to examine different aspects of each institution. Each analysis provides
            unique insights into institutional performance:
            """
        )

        st.markdown("")  # Spacing

        # Four analysis types in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f8faff; margin-bottom: 1rem; height: 200px; display: flex; flex-direction: column;'>
                    <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>📋 Summary</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>View comprehensive institutional profile and key metrics.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Includes enrollment, graduation rates, and institutional details.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem; height: 200px; display: flex; flex-direction: column;'>
                    <h4 style='color: #2ca02c; margin-bottom: 0.5rem;'>💰 Federal Loans & Pell Grants</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Track federal aid trends from 2008-2022.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Combined visualization of loans and grants over time.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; background-color: #fffaf5; margin-bottom: 1rem; height: 200px; display: flex; flex-direction: column;'>
                    <h4 style='color: #ff7f0e; margin-bottom: 0.5rem;'>🎓 Graduation Rates</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Compare overall vs Pell student graduation trends.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Shows equity gaps in completion outcomes (2016-2023).</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #9467bd; border-radius: 10px; background-color: #faf9ff; margin-bottom: 1rem; height: 200px; display: flex; flex-direction: column;'>
                    <h4 style='color: #9467bd; margin-bottom: 0.5rem;'>💻 Distance Education</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Analyze online and hybrid enrollment patterns.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Track distance education trends over time (2020-2024).</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # How to use section
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Start with the Summary tab** to select an institution from the searchable dropdown (6,050+ colleges available).
            Once selected, you'll see institutional details, enrollment metrics, and graduation rates with context.

            **Then explore Federal Loans & Pell Grants** to understand the institution's federal aid patterns and how
            they've changed from 2008-2022.

            **Finally, review Graduation Rates** to see how overall graduation outcomes compare to Pell student outcomes,
            revealing potential equity gaps in completion.
            """
        )

        st.divider()

        # Data notes
        st.markdown("### Data Notes")
        st.markdown(
            """
            - **Graduation rates** in the Summary and Graduation Rates tabs come from IPEDS **Outcome Measures** reporting (columns `GR20XX`/`PGR20XX`), which track **all entering students** over an eight-year window. The most recent value shown is the 2023 outcome for cohorts that started in 2015.
            - **Enrollment metrics** pull from the IPEDS **Distance Education** collection (2020-2024) so the “Total,” “Exclusive Distance Ed,” and “Some Distance Ed” counts reflect the latest fall snapshot available.
            """
        )

        st.divider()

        # What to look for section
        st.markdown("### What the Data Shows")
        st.markdown(
            """
            College Explorer reveals institution-specific patterns:

            - **Institutional context**: Sector, control type, location, and special designations
            - **Enrollment trends**: Total enrollment and distance education participation patterns
            - **Federal aid evolution**: How reliance on loans and grants has shifted over 15 years
            - **Equity in outcomes**: Graduation rate gaps between overall and Pell student populations
            - **Performance benchmarks**: Compare institutional metrics to sector medians with z-scores
            """
        )

        st.divider()

        # Getting started
        st.markdown("### Get Started")
        st.markdown(
            """
            Click on **Summary** in the sidebar to begin exploring individual college data. The searchable dropdown
            allows you to find institutions by name, city, or state—then view comprehensive institutional analysis
            across all available tabs.
            """
        )

    def render_chart(self, chart_name: str) -> None:
        """
        Render a specific chart within the college explorer section.

        Args:
            chart_name: Name of the chart to render
        """
        if chart_name == COLLEGE_SUMMARY_LABEL:
            self._render_college_summary()
        elif chart_name == COLLEGE_LOANS_PELL_LABEL:
            self._render_loans_pell_trends()
        elif chart_name == COLLEGE_GRAD_RATES_LABEL:
            self._render_graduation_rates()
        elif chart_name == COLLEGE_DISTANCE_ED_LABEL:
            self._render_distance_education()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_college_summary(self) -> None:
        """Render the college summary page."""
        self.render_section_header("College Explorer", "Summary")

        # Check if institutions data is available
        if self.institutions_df.empty:
            st.error(
                "Institution data is not available. Please ensure the institutions.csv file is present in the data directory."
            )
            return

        # Prepare institution options for selectbox
        institutions_list = self._prepare_institution_list()

        # College selection
        st.markdown("## Select a College")

        # Create selectbox for college selection
        selected_option = st.selectbox(
            "Search for a college by name:",
            options=[""] + institutions_list,
            index=0,
            key="selected_college",
            help="Start typing to search for a college"
        )

        # Display selected college information
        if selected_option and selected_option != "":
            self._display_college_summary(selected_option)
        else:
            # Show instructions when no college is selected
            st.info(
                """
                **Getting Started**

                Use the dropdown above to search for and select a college. You can:
                - Type part of the college name to filter the list
                - Select from over 6,000 institutions
                - View basic institutional information

                Once selected, you'll see the college's summary information.
                """
            )

            # Preview of available data
            with st.expander("Data Available"):
                st.markdown(
                    """
                    Current data includes:
                    - Institution name and location
                    - State and ZIP code
                    - Sector classification
                    - Control type (Public/Private)
                    - Federal identifiers (UnitID, OPEID)

                    **Coming Soon:**
                    - Enrollment statistics
                    - Graduation rates
                    - Cost and financial aid data
                    - Student outcomes
                    """
                )

    def _prepare_institution_list(self) -> List[str]:
        """Prepare formatted list of institutions for display."""
        if self.institutions_df.empty:
            return []

        # Create display format: "Institution Name - City, State"
        institutions_list = []
        for _, row in self.institutions_df.iterrows():
            display_name = f"{row['INSTITUTION']} - {row['CITY']}, {row['STATE']}"
            institutions_list.append(display_name)

        return sorted(institutions_list)

    def _display_college_summary(self, selected_option: str) -> None:
        """Display summary information for the selected college."""
        # Parse the selected option to get institution name
        institution_name = selected_option.split(" - ")[0]

        # Find the institution in the dataframe
        institution_data = self.institutions_df[
            self.institutions_df['INSTITUTION'] == institution_name
        ]

        if institution_data.empty:
            st.error(f"Could not find data for {institution_name}")
            return

        # Get the first matching row
        inst = institution_data.iloc[0]

        # Display institution header
        st.markdown(f"### {inst['INSTITUTION']}")
        st.markdown(f"📍 {inst['CITY']}, {inst['STATE']} {inst['ZIP']}")

        # Map sector codes to descriptions
        sector_map = {
            0: "Administrative Unit",
            1: "Public, 4-year or above",
            2: "Private not-for-profit, 4-year or above",
            3: "Private for-profit, 4-year or above",
            4: "Public, 2-year",
            5: "Private not-for-profit, 2-year",
            6: "Private for-profit, 2-year",
            7: "Public, less-than 2-year",
            8: "Private not-for-profit, less-than 2-year",
            9: "Private for-profit, less-than 2-year"
        }
        sector = sector_map.get(inst.get('SECTOR', -1), "Unknown")

        # Display sector as a metric
        st.metric("Sector", sector)

        # Add enrollment data if available
        if self.distance_df is not None and not self.distance_df.empty:
            # Find enrollment data for this institution
            enrollment_data = self.distance_df[self.distance_df['UnitID'] == inst['UnitID']]

            if not enrollment_data.empty:
                enroll_row = enrollment_data.iloc[0]

                # Display enrollment section
                st.markdown("---")
                st.markdown("#### Enrollment")

                # Get the most recent year's data (2024)
                total_enrollment = enroll_row.get('TOTAL_ENROLL_2024', None)
                exclusive_de = enroll_row.get('DE_ENROLL_2024', None)
                some_de = enroll_row.get('SDE_ENROLL_TOTAL', None)  # Note: 2024 uses SDE_ENROLL_TOTAL

                # Create columns for enrollment metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    if pd.notna(total_enrollment):
                        st.metric("Total Enrollment", f"{int(total_enrollment):,}")
                    else:
                        st.metric("Total Enrollment", "N/A")

                with col2:
                    if pd.notna(exclusive_de):
                        st.metric("Exclusive Distance Education", f"{int(exclusive_de):,}")
                    else:
                        st.metric("Exclusive Distance Education", "N/A")

                with col3:
                    if pd.notna(some_de):
                        st.metric("Some Distance Education", f"{int(some_de):,}")
                    else:
                        st.metric("Some Distance Education", "N/A")

        # Add graduation rates section if data is available
        if self.pellgradrates_df is not None and not self.pellgradrates_df.empty:
            # Find graduation data for this institution
            grad_data = self.pellgradrates_df[self.pellgradrates_df['UnitID'] == inst['UnitID']]

            if not grad_data.empty:
                grad_row = grad_data.iloc[0]

                # Display graduation rates section
                st.markdown("---")
                st.markdown("#### Graduation Rates")
                st.caption(
                    "“Overall Graduation Rate” reflects the share of **all entering students** (full-time, part-time, Pell, and non-Pell) who "
                    "completed a credential within eight years, using the IPEDS Outcome Measures series. The value shown for 2023 corresponds "
                    "to students who first entered in 2015."
                )

                # Get the most recent year's data (2023)
                overall_grad_rate = grad_row.get('GR2023', None)
                pell_grad_rate = grad_row.get('PGR2023', None)

                # Calculate sector-specific statistics
                sector_code = inst.get('SECTOR', -1)
                is_four_year = sector_code in [1, 2, 3]  # 4-year sectors
                is_two_year = sector_code in [4, 5, 6]   # 2-year sectors

                # Calculate medians and z-scores if we can determine sector
                if is_four_year or is_two_year:
                    # Merge institutions with graduation rates to get sector info
                    merged_df = pd.merge(
                        self.pellgradrates_df[['UnitID', 'GR2023', 'PGR2023']],
                        self.institutions_df[['UnitID', 'SECTOR']],
                        on='UnitID',
                        how='inner'
                    )

                    if is_four_year:
                        sector_df = merged_df[merged_df['SECTOR'].isin([1, 2, 3])]
                        sector_label = "4-year"
                    else:
                        sector_df = merged_df[merged_df['SECTOR'].isin([4, 5, 6])]
                        sector_label = "2-year"

                    # Calculate medians
                    overall_median = sector_df['GR2023'].median()
                    pell_median = sector_df['PGR2023'].median()

                    # Calculate z-scores
                    overall_mean = sector_df['GR2023'].mean()
                    overall_std = sector_df['GR2023'].std()
                    pell_mean = sector_df['PGR2023'].mean()
                    pell_std = sector_df['PGR2023'].std()

                    overall_z = None
                    pell_z = None

                    if pd.notna(overall_grad_rate) and overall_std > 0:
                        overall_z = (overall_grad_rate - overall_mean) / overall_std

                    if pd.notna(pell_grad_rate) and pell_std > 0:
                        pell_z = (pell_grad_rate - pell_mean) / pell_std

                    # Display graduation rates
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Overall Graduation Rate**")
                        if pd.notna(overall_grad_rate):
                            st.metric("This Institution", f"{overall_grad_rate:.1f}%")
                            if pd.notna(overall_median):
                                st.metric(f"{sector_label} Median", f"{overall_median:.1f}%")
                            if overall_z is not None:
                                st.metric("Z-Score", f"{overall_z:.2f}")
                        else:
                            st.metric("This Institution", "N/A")

                    with col2:
                        st.markdown("**Pell Student Graduation Rate**")
                        if pd.notna(pell_grad_rate):
                            st.metric("This Institution", f"{pell_grad_rate:.1f}%")
                            if pd.notna(pell_median):
                                st.metric(f"{sector_label} Median", f"{pell_median:.1f}%")
                            if pell_z is not None:
                                st.metric("Z-Score", f"{pell_z:.2f}")
                        else:
                            st.metric("This Institution", "N/A")
                else:
                    # If sector is unknown, just show the rates without comparisons
                    col1, col2 = st.columns(2)

                    with col1:
                        if pd.notna(overall_grad_rate):
                            st.metric("Overall Graduation Rate", f"{overall_grad_rate:.1f}%")
                        else:
                            st.metric("Overall Graduation Rate", "N/A")

                    with col2:
                        if pd.notna(pell_grad_rate):
                            st.metric("Pell Student Graduation Rate", f"{pell_grad_rate:.1f}%")
                        else:
                            st.metric("Pell Student Graduation Rate", "N/A")

    def _render_loans_pell_trends(self) -> None:
        """Render the Federal Loans and Pell Grants trends page."""
        self.render_section_header("College Explorer", "Federal Loans and Pell Grants")

        # Check if required data is available
        if self.institutions_df.empty:
            st.error(
                "Institution data is not available. Please ensure the institutions.csv file is present in the data directory."
            )
            return

        if self.data_manager.pell_df is None or self.data_manager.pell_df.empty:
            st.error("Pell grant data is not available.")
            return

        if self.data_manager.loan_df is None or self.data_manager.loan_df.empty:
            st.error("Federal loan data is not available.")
            return

        # Prepare institution options for selectbox
        institutions_list = self._prepare_institution_list()

        # College selection
        st.markdown("## Select a College")

        # Create selectbox for college selection
        selected_option = st.selectbox(
            "Search for a college by name:",
            options=[""] + institutions_list,
            index=0,
            key="selected_college_loans_pell",
            help="Start typing to search for a college"
        )

        # Display selected college trend chart
        if selected_option and selected_option != "":
            self._display_combined_trend_chart(selected_option)
        else:
            # Show instructions when no college is selected
            st.info(
                """
                **Getting Started**

                Use the dropdown above to search for and select a college. You can:
                - Type part of the college name to filter the list
                - Select from over 6,000 institutions
                - View combined Pell and Loan trends over time

                Once selected, you'll see a chart with three trend lines:
                - **Pell Grants**: Annual Pell grant dollars received
                - **Federal Loans**: Annual federal loan dollars received
                - **Total Aid**: Combined Pell + Loan dollars
                """
            )

            # Preview of chart features
            with st.expander("Chart Features"):
                st.markdown(
                    """
                    The combined trend chart will show:
                    - **Time period**: 2008-2022 (where data is available)
                    - **Three trend lines**: Pell Grants, Federal Loans, and Total
                    - **Interactive tooltips**: Hover for exact values and year-over-year changes
                    - **Professional styling**: Consistent with existing dashboard charts
                    - **Responsive design**: Scales to fit your screen
                    """
                )

    def _display_combined_trend_chart(self, selected_option: str) -> None:
        """Display the combined Pell and Loan trend chart for the selected college."""
        # Parse the selected option to get institution name
        institution_name = selected_option.split(" - ")[0]

        # Find the institution in the dataframe
        institution_data = self.institutions_df[
            self.institutions_df['INSTITUTION'] == institution_name
        ]

        if institution_data.empty:
            st.error(f"Could not find data for {institution_name}")
            return

        # Get the UnitID
        unit_id = institution_data.iloc[0]['UnitID']

        # Display institution header
        st.markdown(f"### {institution_name}")
        st.markdown(f"**Financial Aid Trends (2008-2022)**")

        # Prepare the combined trend data
        trend_data = self._prepare_combined_trend_data(unit_id, institution_name)

        if trend_data.empty:
            st.warning(f"No financial aid trend data available for {institution_name}")
            return

        # Create the combined trend chart
        chart = self._create_combined_trend_chart(trend_data, institution_name)

        # Display the chart
        render_altair_chart(chart)

        # Display summary statistics
        self._display_trend_summary(trend_data)

    def _prepare_combined_trend_data(self, unit_id: int, institution_name: str) -> pd.DataFrame:
        """Prepare combined Pell and Loan trend data for a specific institution."""

        # Get Pell data for this institution
        pell_data = self.data_manager.pell_df[self.data_manager.pell_df['UnitID'] == unit_id]
        loan_data = self.data_manager.loan_df[self.data_manager.loan_df['UnitID'] == unit_id]

        if pell_data.empty and loan_data.empty:
            return pd.DataFrame()

        # Prepare year columns (YR2008 through YR2022)
        year_columns = [f'YR{year}' for year in range(2008, 2023)]
        available_year_columns = [col for col in year_columns if col in self.data_manager.pell_df.columns]

        trend_records = []

        for year_col in available_year_columns:
            year = int(year_col[2:])  # Extract year from 'YR2022' -> 2022

            # Get Pell value
            pell_value = 0
            if not pell_data.empty and year_col in pell_data.columns:
                pell_val = pell_data.iloc[0][year_col]
                pell_value = pell_val if pd.notna(pell_val) else 0

            # Get Loan value
            loan_value = 0
            if not loan_data.empty and year_col in loan_data.columns:
                loan_val = loan_data.iloc[0][year_col]
                loan_value = loan_val if pd.notna(loan_val) else 0

            # Only include if at least one value is > 0
            if pell_value > 0 or loan_value > 0:
                # Convert to billions for consistency with existing charts
                pell_billions = pell_value / 1_000_000_000
                loan_billions = loan_value / 1_000_000_000
                total_billions = pell_billions + loan_billions

                # Add three records for this year (one for each line)
                trend_records.extend([
                    {
                        'Year': year,
                        'Aid_Type': 'Pell Grants',
                        'Amount_Billions': pell_billions,
                        'Raw_Amount': pell_value,
                        'Institution': institution_name
                    },
                    {
                        'Year': year,
                        'Aid_Type': 'Federal Loans',
                        'Amount_Billions': loan_billions,
                        'Raw_Amount': loan_value,
                        'Institution': institution_name
                    },
                    {
                        'Year': year,
                        'Aid_Type': 'Total Aid',
                        'Amount_Billions': total_billions,
                        'Raw_Amount': pell_value + loan_value,
                        'Institution': institution_name
                    }
                ])

        return pd.DataFrame(trend_records)

    def _create_combined_trend_chart(self, df: pd.DataFrame, institution_name: str) -> alt.Chart:
        """Create the combined trend chart with three lines."""

        # Define colors for the three lines
        color_scale = alt.Scale(
            domain=['Pell Grants', 'Federal Loans', 'Total Aid'],
            range=['#28a745', '#1f77b4', '#ff7f0e']  # Green, Blue, Orange
        )

        # Create the line chart
        lines = alt.Chart(df).mark_line(
            strokeWidth=3,
            point=alt.OverlayMarkDef(size=100, filled=True)
        ).encode(
            x=alt.X('Year:Q', title='Year', axis=alt.Axis(format='d')),
            y=alt.Y('Amount_Billions:Q', title='Amount (billions of dollars)'),
            color=alt.Color(
                'Aid_Type:N',
                title='Aid Type',
                scale=color_scale
            ),
            tooltip=[
                alt.Tooltip('Institution:N', title='Institution'),
                alt.Tooltip('Year:Q', title='Year', format='.0f'),
                alt.Tooltip('Aid_Type:N', title='Aid Type'),
                alt.Tooltip('Amount_Billions:Q', title='Amount (billions)', format='.3f'),
                alt.Tooltip('Raw_Amount:Q', title='Amount ($)', format=',.0f')
            ]
        ).properties(
            height=520,
            title=f"Financial Aid Trends - {institution_name}"
        )

        return lines

    def _display_trend_summary(self, df: pd.DataFrame) -> None:
        """Display summary statistics for the trend data."""
        if df.empty:
            return

        st.markdown("#### Summary Statistics")

        # Get the most recent year with data
        recent_year = df['Year'].max()
        recent_data = df[df['Year'] == recent_year]

        # Display recent year values
        st.markdown(f"##### Most Recent Year ({recent_year})")
        col1, col2, col3 = st.columns(3)

        with col1:
            pell_recent = recent_data[recent_data['Aid_Type'] == 'Pell Grants']['Raw_Amount'].iloc[0] if not recent_data[recent_data['Aid_Type'] == 'Pell Grants'].empty else 0
            st.metric("Pell Grants", f"${pell_recent:,.0f}")

        with col2:
            loan_recent = recent_data[recent_data['Aid_Type'] == 'Federal Loans']['Raw_Amount'].iloc[0] if not recent_data[recent_data['Aid_Type'] == 'Federal Loans'].empty else 0
            st.metric("Federal Loans", f"${loan_recent:,.0f}")

        with col3:
            total_recent = recent_data[recent_data['Aid_Type'] == 'Total Aid']['Raw_Amount'].iloc[0] if not recent_data[recent_data['Aid_Type'] == 'Total Aid'].empty else 0
            st.metric("Total Aid", f"${total_recent:,.0f}")

        # Calculate and display cumulative totals
        st.markdown("##### Cumulative Total (2008-2022)")
        col1, col2, col3 = st.columns(3)

        # Calculate cumulative sums for each aid type
        pell_cumulative = df[df['Aid_Type'] == 'Pell Grants']['Raw_Amount'].sum()
        loan_cumulative = df[df['Aid_Type'] == 'Federal Loans']['Raw_Amount'].sum()
        total_cumulative = df[df['Aid_Type'] == 'Total Aid']['Raw_Amount'].sum()

        with col1:
            st.metric("Pell Grants", f"${pell_cumulative:,.0f}")

        with col2:
            st.metric("Federal Loans", f"${loan_cumulative:,.0f}")

        with col3:
            st.metric("Total Aid", f"${total_cumulative:,.0f}")

        # Calculate year-over-year changes if we have multiple years
        years_available = sorted(df['Year'].unique())
        if len(years_available) >= 2:
            prev_year = years_available[-2]
            prev_data = df[df['Year'] == prev_year]

            st.markdown(f"#### Year-over-Year Change ({prev_year} to {recent_year})")

            col1, col2, col3 = st.columns(3)

            for i, (aid_type, col) in enumerate(zip(['Pell Grants', 'Federal Loans', 'Total Aid'], [col1, col2, col3])):
                recent_val = recent_data[recent_data['Aid_Type'] == aid_type]['Raw_Amount'].iloc[0] if not recent_data[recent_data['Aid_Type'] == aid_type].empty else 0
                prev_val = prev_data[prev_data['Aid_Type'] == aid_type]['Raw_Amount'].iloc[0] if not prev_data[prev_data['Aid_Type'] == aid_type].empty else 0

                if prev_val > 0:
                    change_pct = ((recent_val - prev_val) / prev_val) * 100
                    change_amount = recent_val - prev_val

                    with col:
                        delta_color = "normal" if change_amount >= 0 else "inverse"
                        st.metric(
                            aid_type,
                            f"{change_pct:+.1f}%",
                            delta=f"${change_amount:+,.0f}",
                            delta_color=delta_color
                        )

    def _render_graduation_rates(self) -> None:
        """Render the Graduation Rates page."""
        self.render_section_header("College Explorer", "Graduation Rates")

        # Check if required data is available
        if self.institutions_df.empty:
            st.error(
                "Institution data is not available. Please ensure the institutions.csv file is present in the data directory."
            )
            return

        if self.data_manager.pellgradrates_df is None or self.data_manager.pellgradrates_df.empty:
            st.error("Graduation rates data is not available.")
            return

        # Prepare institution options for selectbox
        institutions_list = self._prepare_institution_list()

        # College selection
        st.markdown("## Select a College")

        # Create selectbox for college selection
        selected_option = st.selectbox(
            "Search for a college by name:",
            options=[""] + institutions_list,
            index=0,
            key="selected_college_grad_rates",
            help="Start typing to search for a college"
        )

        # Display selected college trend chart
        if selected_option and selected_option != "":
            self._display_graduation_trend_chart(selected_option)
        else:
            # Show instructions when no college is selected
            st.info(
                """
                **Getting Started**

                Use the dropdown above to search for and select a college. You can:
                - Type part of the college name to filter the list
                - Select from over 6,000 institutions
                - View graduation rate trends over time

                Once selected, you'll see a chart with:
                - **Overall Graduation Rate**: Blue line showing general student graduation rates
                - **Pell Student Graduation Rate**: Green line showing Pell recipient graduation rates
                - **Reference Lines**: Dashed lines at 25%, 50%, and 75% for context
                """
            )

            # Preview of chart features
            with st.expander("Understanding Graduation Rates"):
                st.markdown(
                    """
                    **Graduation Rate Metrics**:
                    - **Overall Rate (GR)**: Percentage of all students who graduate
                    - **Pell Rate (PGR)**: Percentage of Pell grant recipients who graduate
                    - **Time Period**: 2016-2023 (where data is available)
                    - **Cohort**: 6-year graduation rate for 4-year institutions, 3-year for 2-year

                    **Why This Matters**:
                    - Graduation rates indicate institutional effectiveness
                    - Pell vs Overall gap shows equity in student outcomes
                    - Trends reveal improvement or decline over time
                    """
                )

    def _display_graduation_trend_chart(self, selected_option: str) -> None:
        """Display the graduation rate trend chart for the selected college."""
        # Parse the selected option to get institution name
        institution_name = selected_option.split(" - ")[0]

        # Find the institution in the dataframe
        institution_data = self.institutions_df[
            self.institutions_df['INSTITUTION'] == institution_name
        ]

        if institution_data.empty:
            st.error(f"Could not find data for {institution_name}")
            return

        # Get the UnitID
        unit_id = institution_data.iloc[0]['UnitID']

        # Display institution header
        st.markdown(f"### {institution_name}")
        st.markdown(f"**Graduation Rate Trends (2016-2023)**")

        # Prepare the graduation trend data
        trend_data = self._prepare_graduation_trend_data(unit_id, institution_name)

        if trend_data.empty:
            st.warning(f"No graduation rate data available for {institution_name}")
            return

        # Create the graduation trend chart
        chart = self._create_graduation_trend_chart(trend_data, institution_name)

        # Display the chart
        render_altair_chart(chart)

        # Display summary statistics
        self._display_grad_rate_summary(trend_data)

    def _prepare_graduation_trend_data(self, unit_id: int, institution_name: str) -> pd.DataFrame:
        """Prepare graduation trend data for a specific institution."""

        # Get graduation rates data for this institution
        grad_data = self.data_manager.pellgradrates_df[
            self.data_manager.pellgradrates_df['UnitID'] == unit_id
        ]

        if grad_data.empty:
            return pd.DataFrame()

        trend_records = []

        # Process years from 2016 to 2023
        for year in range(2016, 2024):
            pgr_col = f'PGR{year}'
            gr_col = f'GR{year}'

            # Check if columns exist
            if pgr_col in grad_data.columns and gr_col in grad_data.columns:
                # Get values
                pgr_value = grad_data.iloc[0][pgr_col] if not grad_data[pgr_col].isna().iloc[0] else None
                gr_value = grad_data.iloc[0][gr_col] if not grad_data[gr_col].isna().iloc[0] else None

                # Add Overall graduation rate record
                if gr_value is not None:
                    trend_records.append({
                        'Year': year,
                        'Rate_Type': 'Overall',
                        'Rate': gr_value,
                        'Institution': institution_name
                    })

                # Add Pell graduation rate record
                if pgr_value is not None:
                    trend_records.append({
                        'Year': year,
                        'Rate_Type': 'Pell Students',
                        'Rate': pgr_value,
                        'Institution': institution_name
                    })

        return pd.DataFrame(trend_records)

    def _create_graduation_trend_chart(self, df: pd.DataFrame, institution_name: str) -> alt.Chart:
        """Create the graduation trend chart with two lines and reference lines."""

        # Create reference lines at 25%, 50%, 75%
        reference_data = pd.DataFrame({'rate': [25, 50, 75]})
        reference_lines = alt.Chart(reference_data).mark_rule(
            color='gray',
            strokeDash=[6, 4],
            size=1
        ).encode(
            y=alt.Y('rate:Q')
        )

        # Define colors for the two lines
        color_scale = alt.Scale(
            domain=['Overall', 'Pell Students'],
            range=['#1f77b4', '#28a745']  # Blue for Overall, Green for Pell
        )

        # Create the main line chart
        lines = alt.Chart(df).mark_line(
            strokeWidth=3,
            point=alt.OverlayMarkDef(size=100, filled=True)
        ).encode(
            x=alt.X('Year:Q', title='Year', axis=alt.Axis(format='d')),
            y=alt.Y('Rate:Q',
                    title='Graduation Rate (%)',
                    scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                'Rate_Type:N',
                title='Student Type',
                scale=color_scale
            ),
            tooltip=[
                alt.Tooltip('Institution:N', title='Institution'),
                alt.Tooltip('Year:Q', title='Year', format='.0f'),
                alt.Tooltip('Rate_Type:N', title='Student Type'),
                alt.Tooltip('Rate:Q', title='Graduation Rate (%)', format='.1f')
            ]
        )

        # Combine the lines with reference lines
        chart = (lines + reference_lines).properties(
            height=520,
            title=f"Graduation Rate Trends - {institution_name}"
        )

        return chart

    def _display_grad_rate_summary(self, df: pd.DataFrame) -> None:
        """Display summary statistics for graduation rates."""
        if df.empty:
            return

        st.markdown("#### Summary Statistics")

        # Get the most recent year with data
        recent_year = df['Year'].max()
        recent_data = df[df['Year'] == recent_year]

        # Display recent year values
        st.markdown(f"##### Most Recent Year ({recent_year})")
        col1, col2, col3 = st.columns(3)

        # Overall graduation rate
        overall_recent = recent_data[recent_data['Rate_Type'] == 'Overall']
        if not overall_recent.empty:
            overall_rate = overall_recent['Rate'].iloc[0]
            with col1:
                st.metric("Overall Graduation Rate", f"{overall_rate:.1f}%")
        else:
            with col1:
                st.metric("Overall Graduation Rate", "N/A")

        # Pell graduation rate
        pell_recent = recent_data[recent_data['Rate_Type'] == 'Pell Students']
        if not pell_recent.empty:
            pell_rate = pell_recent['Rate'].iloc[0]
            with col2:
                st.metric("Pell Student Graduation Rate", f"{pell_rate:.1f}%")
        else:
            with col2:
                st.metric("Pell Student Graduation Rate", "N/A")

        # Gap between rates
        if not overall_recent.empty and not pell_recent.empty:
            gap = overall_recent['Rate'].iloc[0] - pell_recent['Rate'].iloc[0]
            with col3:
                color = "normal" if gap < 5 else "inverse"  # Smaller gap is better
                st.metric("Equity Gap", f"{gap:.1f}%",
                         help="Difference between overall and Pell graduation rates",
                         delta_color=color)
        else:
            with col3:
                st.metric("Equity Gap", "N/A")

        # Calculate averages and trends
        st.markdown("##### Historical Analysis")
        col1, col2, col3 = st.columns(3)

        # Average rates
        overall_avg = df[df['Rate_Type'] == 'Overall']['Rate'].mean()
        pell_avg = df[df['Rate_Type'] == 'Pell Students']['Rate'].mean()

        with col1:
            if not pd.isna(overall_avg):
                st.metric("Average Overall Rate", f"{overall_avg:.1f}%",
                         help="Average across all available years")
            else:
                st.metric("Average Overall Rate", "N/A")

        with col2:
            if not pd.isna(pell_avg):
                st.metric("Average Pell Rate", f"{pell_avg:.1f}%",
                         help="Average across all available years")
            else:
                st.metric("Average Pell Rate", "N/A")

        # Trend direction
        with col3:
            # Get first and last year data
            years_available = sorted(df['Year'].unique())
            if len(years_available) >= 2:
                first_year = years_available[0]
                last_year = years_available[-1]

                overall_first = df[(df['Year'] == first_year) & (df['Rate_Type'] == 'Overall')]['Rate']
                overall_last = df[(df['Year'] == last_year) & (df['Rate_Type'] == 'Overall')]['Rate']

                if not overall_first.empty and not overall_last.empty:
                    trend = overall_last.iloc[0] - overall_first.iloc[0]
                    trend_label = "📈 Improving" if trend > 0 else "📉 Declining" if trend < 0 else "➡️ Stable"
                    st.metric("Overall Trend", trend_label,
                             delta=f"{trend:+.1f}% since {first_year}",
                             help=f"Change from {first_year} to {last_year}")
                else:
                    st.metric("Overall Trend", "N/A")
            else:
                st.metric("Overall Trend", "Insufficient Data")

    def _render_distance_education(self) -> None:
        """Provide a searchable distance education snapshot for a single institution."""
        self.render_section_header("College Explorer", "Distance Education")

        distance_data = self.data_manager.get_distance_data()
        institutions = getattr(self.data_manager, "institutions_df", None)

        if distance_data is None or distance_data.empty or institutions is None or institutions.empty:
            st.warning("Distance education institution lookup is unavailable because the required datasets are missing.")
            return

        merged = distance_data.merge(
            institutions[["UnitID", "INSTITUTION", "STATE", "SECTOR"]],
            on="UnitID",
            how="left",
            )

        def _resolve_column(prefix: str) -> str:
            candidates = [
                f"{prefix}_y",
                f"{prefix}_meta",
                f"{prefix}_x",
                prefix,
            ]
            for candidate in candidates:
                if candidate in merged.columns:
                    return candidate
            return prefix

        name_col = _resolve_column("INSTITUTION")
        state_col = _resolve_column("STATE")
        merged["__inst_name"] = merged[name_col].fillna("")
        merged["__inst_state"] = merged[state_col].fillna("") if state_col in merged.columns else ""

        options = (
            merged[["__inst_name", "__inst_state"]]
            .dropna()
            .drop_duplicates()
            .sort_values(["__inst_name", "__inst_state"])
        )
        display_options = [
            f"{row['__inst_name']} ({row['__inst_state']})"
            for _, row in options.iterrows()
            if row["__inst_name"]
        ]

        st.markdown("### Search Distance Education by Institution")
        selected = st.selectbox(
            "Start typing a college name to view its distance education mix (2024).",
            options=[""] + display_options,
            index=0,
        )

        if not selected:
            st.info("Select an institution to view the latest exclusive vs. hybrid enrollment breakdown.")
            return

        institution_name = selected.split(" (")[0]
        selected_rows = merged[merged["__inst_name"] == institution_name]
        if selected_rows.empty:
            st.warning("Unable to locate distance education data for the selected institution.")
            return

        row = selected_rows.iloc[0]
        total_2024 = row.get("TOTAL_ENROLL_2024")
        exclusive_2024 = row.get("DE_ENROLL_2024")
        some_2024 = row.get("SDE_ENROLL_TOTAL")

        try:
            total_2024 = int(float(total_2024)) if pd.notna(total_2024) else None
            exclusive_2024 = int(float(exclusive_2024)) if pd.notna(exclusive_2024) else None
            some_2024 = int(float(some_2024)) if pd.notna(some_2024) and some_2024 != '' else 0

            if total_2024 is None or exclusive_2024 is None:
                st.warning("Distance education figures for 2024 are unavailable for this institution.")
                return
        except (ValueError, TypeError):
            st.warning("Distance education figures for 2024 are unavailable for this institution.")
            return

        oncampus_or_hybrid = max(total_2024 - exclusive_2024, 0)
        exclusive_share = exclusive_2024 / total_2024 if total_2024 else 0
        oncampus_share = oncampus_or_hybrid / total_2024 if total_2024 else 0

        st.markdown(f"#### {institution_name}")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Total Enrollment (2024)", f"{total_2024:,}")
        with metrics_col2:
            st.metric(
                "Exclusive Distance Ed",
                f"{exclusive_2024:,}",
                delta=f"{exclusive_share:.1%}",
            )
        with metrics_col3:
            st.metric(
                "On Campus / Hybrid",
                f"{oncampus_or_hybrid:,}",
                delta=f"{oncampus_share:.1%}",
            )

        years = [2020, 2021, 2022, 2023, 2024]
        total_series = []
        exclusive_series = []
        oncampus_series = []

        for year in years:
            total_col = f"TOTAL_ENROLL_{year}"
            exclusive_col = f"DE_ENROLL_{year}"

            try:
                total_val = int(float(row.get(total_col, 0)))
                exclusive_val = int(float(row.get(exclusive_col, 0)))
            except (TypeError, ValueError):
                total_val = None
                exclusive_val = None

            if total_val is None:
                total_series.append(None)
                exclusive_series.append(None)
                oncampus_series.append(None)
            else:
                total_series.append(total_val)
                exclusive_series.append(exclusive_val if exclusive_val is not None else 0)
                oncampus_series.append(
                    max(total_val - (exclusive_val or 0), 0)
                )

        plot_data = {
            "Year": years,
            "Total Enrollment": total_series,
            "Exclusive Distance": exclusive_series,
            "On Campus / Hybrid": oncampus_series,
        }
        chart_df = pd.DataFrame(plot_data).dropna()
        if not chart_df.empty:
            long_df = (
                chart_df.melt(id_vars="Year", var_name="Metric", value_name="Headcount")
                .sort_values(["Metric", "Year"])
            )
            long_df["Year"] = long_df["Year"].astype(int)
            long_df["Headcount"] = long_df["Headcount"].astype(int)
            long_df["PrevHeadcount"] = long_df.groupby("Metric")["Headcount"].shift(1)
            long_df["YoYChange"] = long_df["Headcount"] - long_df["PrevHeadcount"]
            long_df["YoYChangePercent"] = (
                (long_df["YoYChange"] / long_df["PrevHeadcount"]) * 100
            ).round(1)

            long_df["ChangeDirection"] = pd.cut(
                long_df["YoYChange"],
                bins=[-float("inf"), -0.001, 0.001, float("inf")],
                labels=["Decrease", "Same", "Increase"],
                include_lowest=True,
            ).astype(str)

            first_year_mask = long_df["PrevHeadcount"].isna()
            long_df.loc[first_year_mask, "ChangeDirection"] = "Same"
            long_df.loc[first_year_mask, "YoYChangePercent"] = 0.0

            metric_color_scale = alt.Scale(
                domain=["Total Enrollment", "Exclusive Distance", "On Campus / Hybrid"],
                range=["#1f77b4", "#ff7f0e", "#2ca02c"],
            )

            change_color_scale = alt.Scale(
                domain=["Increase", "Same", "Decrease"],
                range=["#28a745", "#f6c344", "#d62728"],
            )

            lines = (
                alt.Chart(long_df)
                .mark_line(point=False, strokeDash=[4, 4])
                .encode(
                    x=alt.X("Year:Q", title="Year", axis=alt.Axis(format="d")),
                    y=alt.Y("Headcount:Q", title="Headcount"),
                    color=alt.Color("Metric:N", title="", scale=metric_color_scale),
                    tooltip=[
                        alt.Tooltip("Metric:N", title="Series"),
                        alt.Tooltip("Year:Q", title="Year", format=".0f"),
                        alt.Tooltip("Headcount:Q", title="Headcount", format=",.0f"),
                        alt.Tooltip(
                            "YoYChangePercent:Q",
                            title="Year-over-year change (%)",
                            format=".1f",
                        ),
                    ],
                )
                .properties(height=360)
            )

            points = (
                alt.Chart(long_df)
                .mark_circle(size=85)
                .encode(
                    x=alt.X("Year:Q", axis=alt.Axis(format="d")),
                    y=alt.Y("Headcount:Q"),
                    color=alt.Color(
                        "ChangeDirection:N",
                        title="Year-over-Year Change",
                        scale=change_color_scale,
                        legend=None,
                    ),
                    tooltip=[
                        alt.Tooltip("Metric:N", title="Series"),
                        alt.Tooltip("Year:Q", title="Year", format=".0f"),
                        alt.Tooltip("Headcount:Q", title="Headcount", format=",.0f"),
                        alt.Tooltip(
                            "YoYChangePercent:Q",
                            title="Year-over-year change (%)",
                            format=".1f",
                        ),
                        alt.Tooltip("ChangeDirection:N", title="Change direction"),
                    ],
                )
            )

            render_altair_chart((lines + points))

            # Add spacing between charts
            st.markdown("")

            # Stacked bar chart showing enrollment composition
            st.subheader("Enrollment Composition Over Time")

            # Filter to show only the two components (exclude Total Enrollment)
            stacked_df = long_df[long_df["Metric"].isin(["Exclusive Distance", "On Campus / Hybrid"])].copy()

            # Create color scale for just the two components
            component_color_scale = alt.Scale(
                domain=["Exclusive Distance", "On Campus / Hybrid"],
                range=["#ff7f0e", "#2ca02c"],  # Orange for Exclusive Distance, Green for On Campus/Hybrid
            )

            # Create stacked bar chart
            stacked_chart = (
                alt.Chart(stacked_df)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "Year:O",
                        title="Year",
                        axis=alt.Axis(
                            labelAngle=0,
                            labelFontSize=14,
                            titleFontSize=16,
                            titleFontWeight="bold"
                        )
                    ),
                    y=alt.Y(
                        "Headcount:Q",
                        title="Total Enrollment",
                        stack="zero",
                        axis=alt.Axis(
                            format="~s",
                            labelFontSize=14,
                            titleFontSize=16,
                            titleFontWeight="bold"
                        )
                    ),
                    color=alt.Color(
                        "Metric:N",
                        title="Enrollment Type",
                        scale=component_color_scale,
                        legend=alt.Legend(
                            orient="right",
                            titleFontSize=12,
                            labelFontSize=11,
                            labelLimit=200
                        )
                    ),
                    order=alt.Order("Headcount:Q", sort="descending"),
                    tooltip=[
                        alt.Tooltip("Metric:N", title="Type"),
                        alt.Tooltip("Year:O", title="Year"),
                        alt.Tooltip("Headcount:Q", title="Enrollment", format=","),
                    ],
                )
                .properties(height=400)
            )

            st.caption(
                "Total enrollment breakdown by type (2020-2024). Each bar is divided into "
                "Exclusive Distance Education (orange) and On Campus/Hybrid (green) enrollment."
            )
            render_altair_chart(stacked_chart)

            table = (
                chart_df.astype(int)
                .sort_values("Year")
                .rename(
                    columns={
                        "Total Enrollment": "Total",
                        "Exclusive Distance": "Exclusive Distance",
                        "On Campus / Hybrid": "On Campus / Hybrid",
                    }
                )
                .set_index("Year")
            )

            st.dataframe(
                table,
                width="stretch",
                column_config={
                    "Total": st.column_config.NumberColumn("Total", format="%,d", width="small"),
                    "Exclusive Distance": st.column_config.NumberColumn("Exclusive Distance", format="%,d", width="small"),
                    "On Campus / Hybrid": st.column_config.NumberColumn("On Campus / Hybrid", format="%,d", width="small"),
                },
            )
        else:
            st.info("Historical distance education data is not available for this institution.")

    def get_available_charts(self) -> List[str]:
        """
        Get list of available charts for the college explorer section.

        Returns:
            List of chart names
        """
        return COLLEGE_EXPLORER_CHARTS
