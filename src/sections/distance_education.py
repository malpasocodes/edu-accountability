"""Distance Education section implementation."""

from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st
import altair as alt

from src.charts.distance_top_enrollment_chart import render_distance_top_enrollment_chart
from src.charts.distance_enrollment_trend_chart import render_distance_enrollment_trend_chart
from src.charts.distance_de_trend_chart import render_distance_de_trend_chart
from src.ui.renderers import render_altair_chart
from .base import BaseSection


class DistanceEducationSection(BaseSection):
    """Handles the Distance Education section."""

    def render_overview(self) -> None:
        """Render the Distance Education overview."""
        self.render_section_header("Distance Education", "Overview")

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    💻 Distance Education Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Track online and hybrid enrollment trends to understand how institutions deliver digital learning.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Key insight callout
        st.info("**💡 Key Insight:** Distance education data reveals how institutions are adapting to online learning, showing enrollment patterns from the COVID-19 era through 2024 and which schools lead in online program delivery.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is Distance Education Analysis?")
        st.markdown(
            """
            This section tracks **distance education enrollment** at colleges and universities across the United States.
            The data covers **2020-2024** and categorizes students into three groups:

            - **Exclusively Distance Education**: Students taking all courses online
            - **Some Distance Education**: Students in hybrid programs mixing online and in-person
            - **No Distance Education**: Students in traditional in-person programs only

            Understanding these patterns helps illuminate how higher education delivery has evolved, particularly
            during and after the COVID-19 pandemic, and which institutions are leading in online education.
            """
        )

        st.divider()

        # Available analyses section
        st.markdown("### Three Ways to Explore Distance Education Data")
        st.markdown(
            """
            Use the **sidebar charts** to examine distance education patterns from different angles. Each analysis
            is available for both 4-year and 2-year institutions:
            """
        )

        st.markdown("")  # Spacing

        # Three analysis types in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; background-color: #fffaf5; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #ff7f0e; margin-bottom: 0.5rem;'>📊 Top 25 Total Enrollment (Distance Education Breakdown)</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>See which institutions have the highest total enrollment with distance education breakdown.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Stacked bars show exclusive, some, and in-person enrollment.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f8faff; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>📈 Total Enrollment Trend (Top 10 Institutions)</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Track overall enrollment changes from 2020-2024 for top 10 institutions by 2024 enrollment.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Shows year-over-year enrollment patterns.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem; height: 220px; display: flex; flex-direction: column;'>
                    <h4 style='color: #2ca02c; margin-bottom: 0.5rem;'>📉 Exclusive Distance Education Trend (Top 10 Institutions)</h4>
                    <div style='flex-grow: 1; display: flex; flex-direction: column; justify-content: center;'>
                        <p style='color: #000000; margin-bottom: 0.5rem;'>Track exclusive distance education enrollment over time for top 10 institutions by 2024 exclusive DE enrollment.</p>
                        <p style='color: #000000; font-style: italic; margin: 0;'>Shows how online-only enrollment evolved 2020-2024.</p>
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
            **Start with Top 25 Total Enrollment** to see which institutions have the largest student bodies and how those students break down by distance education participation.
            Then explore the **Total Enrollment Trend** to see how overall student populations changed during the pandemic period for the top 10 largest institutions.
            Finally, use the **Exclusive Distance Education Trend** to track the specific growth of exclusively online programs for the top 10 institutions by DE enrollment.

            **Each chart includes tabs** at the top for 4-year and 2-year institutions, allowing you to compare
            patterns across different institutional types.
            """
        )

        st.divider()

        # What to look for section
        st.markdown("### What the Data Shows")
        st.markdown(
            """
            Distance education data reveals important patterns about online learning adoption:

            - **High distance education enrollment** indicates institutional commitment to online delivery
            - **COVID-19 impact** is visible in 2020-2021 shifts toward online learning
            - **Post-pandemic patterns** show whether online enrollment sustained or returned to pre-pandemic levels
            - **Institutional differences** emerge between traditional colleges and online-focused institutions
            """
        )

        st.divider()

        # Data disclaimer
        st.markdown("### Data Source & Notes")
        st.info(
            "**Data Source:** IPEDS Distance Education surveys, 2020-2024. "
            "Enrollment data includes breakdowns by distance education participation level (exclusive, some, none). "
            "Data reflects fall enrollment snapshots for each year."
        )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Distance Education chart."""
        self.render_section_header("Distance Education", chart_name)

        # Handle chart routing (support both old and new labels for backward compatibility)
        if chart_name in ["Top 25 Total Enrollment (Distance Education Breakdown)", "Top 25 Distance Education Enrollment"]:
            self._render_distance_top_enrollment_with_tabs(chart_name)
        elif chart_name in ["Total Enrollment Trend (Top 10 Institutions)", "Total Enrollment Trend"]:
            self._render_enrollment_trend_with_tabs(chart_name)
        elif chart_name in ["Exclusive Distance Education Trend (Top 10 Institutions)", "Distance Education Trend"]:
            self._render_de_trend_with_tabs(chart_name)
        elif chart_name == "Institution Distance Search":
            self._render_institution_search()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_institution_search(self) -> None:
        """Provide a searchable distance education snapshot for a single institution."""
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
            total_2024 = int(float(total_2024))
            exclusive_2024 = int(float(exclusive_2024))
            some_2024 = int(float(some_2024))
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

            render_altair_chart((lines + points), width="stretch")

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
                use_container_width=True,
                column_config={
                    "Total": st.column_config.NumberColumn("Total", format="%,d", width="small"),
                    "Exclusive Distance": st.column_config.NumberColumn("Exclusive Distance", format="%,d", width="small"),
                    "On Campus / Hybrid": st.column_config.NumberColumn("On Campus / Hybrid", format="%,d", width="small"),
                },
            )
        else:
            st.info("Historical distance education data is not available for this institution.")

    def _render_distance_top_enrollment_with_tabs(self, title: str) -> None:
        """Render top enrollment chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_distance_top_enrollment("four_year", f"{title} (4-year)")

        with tab2:
            self._render_distance_top_enrollment("two_year", f"{title} (2-year)")

    def _render_distance_top_enrollment(self, sector: str, title: str) -> None:
        """Render distance education top enrollment chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_top_enrollment_chart(
                distance_data,
                metadata,
                top_n=25,
                title=title,
                year=2024  # Use most recent year
            )
        except Exception as e:
            st.error(f"Error rendering chart: {e}")

    def _render_enrollment_trend_with_tabs(self, title: str) -> None:
        """Render enrollment trend chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_enrollment_trend("four_year", f"{title} (4-year)")

        with tab2:
            self._render_enrollment_trend("two_year", f"{title} (2-year)")

    def _render_enrollment_trend(self, sector: str, title: str) -> None:
        """Render enrollment trend chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_enrollment_trend_chart(
                distance_data,
                metadata,
                title=title,
                top_n=10,
                anchor_year=2024
            )
        except Exception as e:
            st.error(f"Error rendering enrollment trend chart: {e}")

    def _render_de_trend_with_tabs(self, title: str) -> None:
        """Render DE trend chart with 4-year/2-year tabs."""
        tab1, tab2 = st.tabs(["4-year", "2-year"])

        with tab1:
            self._render_de_trend("four_year", f"{title} (4-year)")

        with tab2:
            self._render_de_trend("two_year", f"{title} (2-year)")

    def _render_de_trend(self, sector: str, title: str) -> None:
        """Render DE trend chart for a specific sector."""
        # Get distance education data
        distance_data = self.data_manager.get_distance_data()
        if distance_data is None or distance_data.empty:
            st.warning("Distance education data not available.")
            return

        # Get metadata for the sector
        metadata = self.data_manager.get_metadata_for_sector(sector)
        if metadata is None or metadata.empty:
            st.warning(f"Metadata for {sector} institutions not available.")
            return

        try:
            render_distance_de_trend_chart(
                distance_data,
                metadata,
                title=title,
                top_n=10,
                anchor_year=2024
            )
        except Exception as e:
            st.error(f"Error rendering DE trend chart: {e}")

    def get_available_charts(self) -> List[str]:
        """Get available charts for distance education section."""
        from src.config.constants import DISTANCE_OVERVIEW_LABEL, DISTANCE_CHARTS
        return [
            DISTANCE_OVERVIEW_LABEL,
            *DISTANCE_CHARTS
        ]
