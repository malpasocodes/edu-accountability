"""College Explorer section implementation."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd
import streamlit as st
import altair as alt

from .base import BaseSection
from src.ui.renderers import render_altair_chart
from src.config.constants import (
    COLLEGE_EXPLORER_OVERVIEW_LABEL,
    COLLEGE_SUMMARY_LABEL,
    COLLEGE_LOANS_PELL_LABEL,
    COLLEGE_GRAD_RATES_LABEL,
    COLLEGE_EXPLORER_CHARTS,
)


class CollegeExplorerSection(BaseSection):
    """Handles the college explorer section for individual institution data."""

    def __init__(self, data_manager):
        """Initialize the section with institutions data."""
        super().__init__(data_manager)
        self.institutions_df = data_manager.institutions_df if hasattr(data_manager, 'institutions_df') else pd.DataFrame()

    def render_overview(self) -> None:
        """Render the college explorer overview page."""
        self.render_section_header("College Explorer", "Overview")

        # Introduction
        st.markdown(
            """
            ## Explore Individual College Data

            The College Explorer allows you to dive deep into detailed information about individual
            institutions. This tool provides comprehensive data on specific colleges and universities,
            enabling you to examine their unique characteristics, performance metrics, and outcomes.
            """
        )

        # Feature Preview
        st.info(
            """
            **🚧 Coming Soon**

            This section is under development and will provide:
            - Detailed institutional profiles with key metrics
            - Historical trends for individual colleges
            - Peer comparisons within similar institution types
            - Student outcome data by demographic groups
            - Financial aid and affordability analysis
            """
        )

        # How it will work
        st.subheader("How the College Explorer Works")
        st.markdown(
            """
            1. **Search or Select**: Find colleges by name, location, or characteristics
            2. **View Summary**: Access comprehensive institutional data at a glance
            3. **Deep Dive**: Explore detailed metrics across multiple dimensions
            4. **Compare**: Benchmark against peer institutions
            5. **Export**: Download data for further analysis
            """
        )

        # Data Sources
        st.subheader("Data Sources")
        st.markdown(
            """
            The College Explorer integrates multiple authoritative data sources:
            - **IPEDS**: Institutional characteristics, enrollment, and completion data
            - **Federal Student Aid**: Loan and grant disbursement information
            - **College Scorecard**: Earnings and debt metrics
            - **Census Data**: Regional demographic context
            """
        )

        # Call to Action
        st.markdown("---")
        st.markdown(
            """
            ### Get Started

            Click on **Summary** in the navigation to begin exploring individual college data.
            The summary page will allow you to select a specific institution and view its
            comprehensive profile.
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

        # Create columns for basic information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Unit ID", inst['UnitID'])

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
            st.info(f"**Sector:** {sector}")

        with col2:
            st.metric("OPEID", inst.get('OPEID', 'N/A'))

            # Map control codes
            control_map = {
                1: "Public",
                2: "Private not-for-profit",
                3: "Private for-profit"
            }
            control = control_map.get(inst.get('CONTROL', -1), "Unknown")
            st.info(f"**Control:** {control}")

        with col3:
            # Check special designations
            designations = []
            if inst.get('HISTORICALLY_BLACK') == 1:
                designations.append("HBCU")
            if inst.get('TRIBAL') == 1:
                designations.append("Tribal College")

            if designations:
                st.info(f"**Designations:** {', '.join(designations)}")
            else:
                st.info("**Designations:** None")

            # Category if available
            if 'CATEGORY' in inst and pd.notna(inst['CATEGORY']):
                st.metric("Category", inst['CATEGORY'])

        # Placeholder for additional data
        st.markdown("---")
        st.markdown("#### Additional Information")
        st.info(
            """
            🚧 **More Data Coming Soon**

            Future updates will include:
            - Total enrollment and demographics
            - Graduation and retention rates
            - Average net price by income level
            - Federal loan and Pell Grant statistics
            - Distance education enrollment
            - Historical trends and peer comparisons
            """
        )

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
        render_altair_chart(chart, width="stretch")

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
        render_altair_chart(chart, width="stretch")

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

    def get_available_charts(self) -> List[str]:
        """
        Get list of available charts for the college explorer section.

        Returns:
            List of chart names
        """
        return COLLEGE_EXPLORER_CHARTS