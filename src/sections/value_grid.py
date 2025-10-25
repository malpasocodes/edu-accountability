"""Value Grid section implementation."""

from __future__ import annotations

from typing import List
from textwrap import dedent

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter
from src.config.constants import (
    VALUE_GRID_CONFIG_MAP,
    VALUE_GRID_OVERVIEW_LABEL,
    VALUE_GRID_SECTION,
    ENROLLMENT_FILTER_OPTIONS,
    DEFAULT_ENROLLMENT_FILTER,
)
from src.core.data_loader import DataLoader
from src.state.session_manager import SessionManager
from .base import BaseSection


class ValueGridSection(BaseSection):
    """Handles the College Value Grid section."""
    
    def render_overview(self) -> None:
        """Render the Value Grid overview."""
        self.render_section_header(VALUE_GRID_SECTION, VALUE_GRID_OVERVIEW_LABEL)

        # Overview hero styling aligned with landing page
        st.markdown(
            """
            <div style='text-align: center; padding: 1.5rem 0; background: linear-gradient(135deg, #dee2e6 0%, #ced4da 100%); border-radius: 10px; margin-bottom: 1.5rem;'>
                <h2 style='color: #1f77b4; font-size: 2.2rem; margin-bottom: 0.25rem; font-weight: 700;'>
                    📊 College Value Grid Overview
                </h2>
                <p style='color: #000000; font-size: 1.05rem; margin: 0; font-weight: 400;'>
                    Explore tuition costs and graduation outcomes to identify institutions delivering strong value.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Key insight callout
        st.info("**💡 Key Insight:** This tool reveals which institutions deliver strong graduation outcomes at affordable prices—and which charge more but graduate fewer students.")

        st.markdown("")  # Spacing

        # What is this section
        st.markdown("### What is the College Value Grid?")
        st.markdown(
            """
            The College Value Grid provides a clear way to compare institutions by two simple but powerful measures:
            **graduation rate** and **in-state tuition cost**. Each dot on the chart represents a college or university
            with at least 1,000 undergraduate students.
            """
        )

        quadrant_html = dedent(
            """
            <div style='display: flex; justify-content: center; margin: 2rem 0 2.5rem;'>
            <div style='position: relative; width: 100%; max-width: 460px;'>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr); width: 460px; height: 460px; border: 2px solid #ced4da; border-radius: 12px; overflow: hidden; background: linear-gradient(135deg, rgba(248,249,250,0.9) 0%, rgba(233,236,239,0.9) 100%); box-shadow: 0 8px 20px rgba(0,0,0,0.05);'>

            <div style='position: relative; border-right: 1px solid #adb5bd; border-bottom: 1px solid #adb5bd; background-color: rgba(44,160,44,0.06); display: flex; align-items: center; justify-content: center; padding: 0.75rem; text-align: center;'>
            <div>
            <span style='color: #2ca02c; font-size: 1.8rem; font-weight: 600; display: block;'>I</span>
            <span style='color: #2ca02c; font-size: 1rem; font-weight: 600;'>High Graduation, Low Cost</span>
            </div>
            </div>

            <div style='position: relative; border-left: 1px solid #adb5bd; border-bottom: 1px solid #adb5bd; background-color: rgba(31,119,180,0.06); display: flex; align-items: center; justify-content: center; padding: 0.75rem; text-align: center;'>
            <div>
            <span style='color: #1f77b4; font-size: 1.8rem; font-weight: 600; display: block;'>II</span>
            <span style='color: #1f77b4; font-size: 1rem; font-weight: 600;'>High Graduation, High Cost</span>
            </div>
            </div>

            <div style='position: relative; border-right: 1px solid #adb5bd; border-top: 1px solid #adb5bd; background-color: rgba(255,127,14,0.06); display: flex; align-items: center; justify-content: center; padding: 0.75rem; text-align: center;'>
            <div>
            <span style='color: #ff7f0e; font-size: 1.8rem; font-weight: 600; display: block;'>III</span>
            <span style='color: #ff7f0e; font-size: 1rem; font-weight: 600;'>Low Graduation, Low Cost</span>
            </div>
            </div>

            <div style='position: relative; border-left: 1px solid #adb5bd; border-top: 1px solid #adb5bd; background-color: rgba(214,39,40,0.06); display: flex; align-items: center; justify-content: center; padding: 0.75rem; text-align: center;'>
            <div>
            <span style='color: #d62728; font-size: 1.8rem; font-weight: 600; display: block;'>IV</span>
            <span style='color: #d62728; font-size: 1rem; font-weight: 600;'>Low Graduation, High Cost</span>
            </div>
            </div>

            </div>

            <div style='position: absolute; top: 18%; left: -15.5rem; width: 200px; text-align: right; color: #868e96; font-size: 0.95rem; font-weight: 600; line-height: 1.45;'>
                Institutions delivering strong outcomes at an affordable price.
                <span style='display: block; font-style: italic; color: #495057;'>This is the best value quadrant.</span>
            </div>

            <div style='position: absolute; top: 18%; right: -15.5rem; width: 200px; text-align: left; color: #868e96; font-size: 0.95rem; font-weight: 600; line-height: 1.45;'>
                Institutions with high graduation rates, but at a higher tuition cost.
                <span style='display: block; font-style: italic; color: #495057;'>Strong outcomes, premium pricing.</span>
            </div>

            <div style='position: absolute; bottom: 16%; left: -15.5rem; width: 200px; text-align: right; color: #868e96; font-size: 0.95rem; font-weight: 600; line-height: 1.45;'>
                Lower-cost institutions where graduation rates fall below the median.
                <span style='display: block; font-style: italic; color: #495057;'>Affordability with outcome challenges.</span>
            </div>

            <div style='position: absolute; bottom: 16%; right: -15.5rem; width: 200px; text-align: left; color: #868e96; font-size: 0.95rem; font-weight: 600; line-height: 1.45;'>
                Institutions charging above-median tuition with below-median graduation rates.
                <span style='display: block; font-style: italic; color: #495057;'>Posing the greatest concern for affordability and student outcomes.</span>
            </div>


            <div style='position: absolute; bottom: -2.6rem; left: 50%; transform: translateX(-50%); color: #495057; font-size: 1.15rem; font-weight: 600;'>Higher Cost <span style='font-size: 1.8rem; line-height: 1;'>→</span></div>
            <div style='position: absolute; top: 50%; left: -7.6rem; transform: translateY(-50%) rotate(-90deg); color: #495057; font-size: 1.15rem; font-weight: 600; white-space: nowrap;'>Higher Graduation Rate <span style='font-size: 1.8rem; line-height: 1;'>→</span></div>

            </div>
            </div>
            """
        )
        st.markdown(quadrant_html, unsafe_allow_html=True)

        # Data notes
        st.markdown("### Data Notes")
        st.markdown(
            """
            - **Cost** reflects published in-state tuition and required fees reported to IPEDS for the **2023-24 academic year** (IC2023_AY survey).
            - **Graduation rate** comes from the IPEDS **Graduation Rates (GR) survey** for the cohort that entered in **2015** and completed within 150% of normal time (three years for 2-year colleges, six years for 4-year institutions).
            """
        )

        st.divider()

        # What to look for section
        st.markdown("### What the Data Shows")
        st.markdown(
            """
            This tool is designed to make patterns across higher education transparent. For example:

            - **Many public universities** fall into Quadrant I, offering strong value
            - **Quadrant IV** highlights higher-risk institutions where students pay more but graduate less often
            - Patterns emerge by sector, control type, and institutional mission
            """
        )

    def _render_enrollment_filter(self) -> None:
        """Render the enrollment filter UI control."""
        st.markdown("### Filter by Enrollment")

        # Create radio button options with formatted labels
        option_labels = []
        for threshold in ENROLLMENT_FILTER_OPTIONS:
            if threshold == 1:
                option_labels.append("All (>0)")
            else:
                option_labels.append(f">{threshold:,}")

        # Map labels to values
        label_to_value = dict(zip(option_labels, ENROLLMENT_FILTER_OPTIONS))

        # Get current filter value from session state
        current_value = SessionManager.get("value_grid_enrollment_filter", DEFAULT_ENROLLMENT_FILTER)

        # Find the current label
        current_label = None
        for label, value in label_to_value.items():
            if value == current_value:
                current_label = label
                break
        if current_label is None:
            current_label = option_labels[2]  # Default to ">1,000"

        # Render radio buttons
        selected_label = st.radio(
            "Minimum undergraduate enrollment:",
            options=option_labels,
            index=option_labels.index(current_label),
            horizontal=True,
            key="enrollment_filter_radio"
        )

        # Update session state with the selected value
        selected_value = label_to_value[selected_label]
        SessionManager.set("value_grid_enrollment_filter", selected_value)

        st.markdown("")  # Add spacing

    def render_chart(self, chart_name: str) -> None:
        """Render a specific Value Grid chart."""
        self.render_section_header(VALUE_GRID_SECTION, chart_name)

        config = VALUE_GRID_CONFIG_MAP.get(chart_name)
        if config is None:
            st.error("Select a value grid view from the sidebar to load a chart.")
            return

        dataset = self.data_manager.get_value_grid_dataset(config.label)
        if dataset is None:
            st.error("Unable to locate dataset for the selected chart.")
            return

        # Add enrollment filter UI control
        self._render_enrollment_filter()

        # Get the selected enrollment filter from session state
        selected_filter = SessionManager.get("value_grid_enrollment_filter", DEFAULT_ENROLLMENT_FILTER)

        self._render_value_grid_chart(config.label, dataset, selected_filter)
    
    def _render_value_grid_chart(
        self, 
        label: str, 
        dataset: pd.DataFrame, 
        min_enrollment: int
    ) -> None:
        """Internal method to render the value grid chart."""
        columns_needed = {"institution", "sector", "cost", "graduation_rate"}
        missing = [column for column in columns_needed if column not in dataset.columns]
        if missing:
            st.error(
                "Cannot render cost vs graduation chart. Missing columns: " + ", ".join(missing)
            )
            return
        
        prepared = DataLoader.prepare_value_grid_dataset(label, dataset)
        
        if min_enrollment > 0 and "enrollment" in prepared.columns:
            filtered = prepared[prepared["enrollment"] >= min_enrollment]
        else:
            filtered = prepared
        
        filtered = filtered.dropna(subset=["cost", "graduation_rate"])
        if filtered.empty:
            st.warning("No institutions meet the current baseline criteria.")
            return
        
        cost_median = float(prepared["cost"].dropna().median())
        grad_median = float(prepared["graduation_rate"].dropna().median())
        
        render_cost_vs_grad_scatter(
            filtered,
            min_enrollment=min_enrollment,
            global_cost_median=cost_median,
            global_grad_median=grad_median,
            group_label=label,
        )
    
    def get_available_charts(self) -> List[str]:
        """Get available charts for Value Grid section."""
        return list(VALUE_GRID_CONFIG_MAP.keys())
