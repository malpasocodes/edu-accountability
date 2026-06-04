"""Faculty section implementation (instructional staffing / adjunct reliance)."""

from __future__ import annotations

from typing import List

import streamlit as st

from src.charts.faculty_composition_chart import render_faculty_adjunct_chart
from src.config.constants import (
    ENROLLMENT_FILTER_OPTIONS,
    FACULTY_ADJUNCT_RELIANCE_LABEL,
    FACULTY_CHARTS,
    FACULTY_OVERVIEW_LABEL,
)
from src.state.session_manager import SessionManager
from .base import BaseSection

FACULTY_ENROLLMENT_FILTER_KEY = "faculty_enrollment_filter"
DEFAULT_FACULTY_ENROLLMENT_FILTER = 1


class FacultySection(BaseSection):
    """Handles the Faculty section covering instructional staffing."""

    def render_overview(self) -> None:
        """Render the Faculty overview page."""
        self.render_section_header("Faculty", "Overview")

        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    👩‍🏫 Faculty Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Examine how institutions staff instruction with full-time versus part-time (adjunct) faculty.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "**💡 Key Insight:** Heavy reliance on part-time instructors can signal "
            "cost pressures and affect instructional continuity. Reliance varies "
            "sharply by sector — many for-profit and online institutions staff "
            "instruction almost entirely with part-time faculty."
        )

        st.markdown("### What This Measures")
        st.markdown("""
            This section reports **instructional staff** at each institution, split into
            **full-time** and **part-time** headcounts, and the **part-time share** of all
            instructional staff.

            IPEDS does **not** publish an "adjunct" category. The widely used proxy for
            adjunct/contingent teaching is **part-time instructional staff**, which is what
            this section reports. The proxy slightly over-counts (some part-timers teach a
            single course) and under-counts (full-time non-tenure-track lecturers are also
            contingent), so read it as a directional indicator of adjunct reliance rather
            than an exact count.
            """)

        st.markdown("### How to Read the Ranking")
        st.markdown("""
            The **Adjunct (Part-time) Faculty Reliance** chart ranks institutions by the
            part-time share of instructional staff, separated into 4-year and 2-year tabs.
            To keep the ranking meaningful, only institutions with at least 50 instructional
            staff are included — otherwise very small departments dominate the top with
            100% part-time figures.
            """)

        st.divider()
        st.markdown("### Data Source & Notes")
        st.info(
            "**Data Source:** IPEDS Human Resources survey, Employees by Assigned "
            "Position (EAP), 2023. Counts reflect the institution-wide total of "
            "instructional staff across all faculty/tenure statuses."
        )

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Faculty chart."""
        self.render_section_header("Faculty", chart_name)

        if chart_name == FACULTY_ADJUNCT_RELIANCE_LABEL:
            self._render_adjunct_reliance_with_tabs(chart_name)
        else:
            st.error(f"Unknown chart: {chart_name}")

    def _render_enrollment_filter(self) -> int:
        """Render the enrollment filter UI control and return the selected value."""
        st.markdown("### Filter by Enrollment")

        option_labels = []
        for threshold in ENROLLMENT_FILTER_OPTIONS:
            if threshold == 1:
                option_labels.append("All (>0)")
            else:
                option_labels.append(f">{threshold:,}")

        label_to_value = dict(zip(option_labels, ENROLLMENT_FILTER_OPTIONS))

        current_value = SessionManager.get(
            FACULTY_ENROLLMENT_FILTER_KEY, DEFAULT_FACULTY_ENROLLMENT_FILTER
        )
        current_label = next(
            (
                label
                for label, value in label_to_value.items()
                if value == current_value
            ),
            option_labels[0],
        )

        selected_label = st.radio(
            "Minimum undergraduate enrollment:",
            options=option_labels,
            index=option_labels.index(current_label),
            horizontal=True,
            key="faculty_enrollment_filter_radio",
        )

        selected_value = label_to_value[selected_label]
        SessionManager.set(FACULTY_ENROLLMENT_FILTER_KEY, selected_value)
        st.markdown("")  # Spacing
        return selected_value

    def _render_adjunct_reliance_with_tabs(self, title: str) -> None:
        """Render the adjunct reliance ranking with 4-year/2-year tabs."""
        faculty_df = self.data_manager.get_faculty_data()
        if faculty_df is None or faculty_df.empty:
            st.warning(
                "Faculty staffing data is not available. Run "
                "`python -m src.data.build_faculty_metrics` to generate it."
            )
            return

        min_enrollment = self._render_enrollment_filter()

        tab_four, tab_two = st.tabs(["4-year", "2-year"])
        with tab_four:
            render_faculty_adjunct_chart(
                faculty_df,
                sector="four_year",
                title=f"{title} (4-year)",
                min_enrollment=min_enrollment,
            )
        with tab_two:
            render_faculty_adjunct_chart(
                faculty_df,
                sector="two_year",
                title=f"{title} (2-year)",
                min_enrollment=min_enrollment,
            )

    def get_available_charts(self) -> List[str]:
        """Get available charts for the Faculty section."""
        return [FACULTY_OVERVIEW_LABEL, *FACULTY_CHARTS]
