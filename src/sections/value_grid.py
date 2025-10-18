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
)
from src.core.data_loader import DataLoader
from .base import BaseSection


class ValueGridSection(BaseSection):
    """Handles the College Value Grid section."""
    
    def render_overview(self) -> None:
        """Render the Value Grid overview."""
        self.render_section_header(VALUE_GRID_SECTION, VALUE_GRID_OVERVIEW_LABEL)

        # Main title
        st.title("College Value Grid: Understanding Cost vs. Graduation")

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
            <div style='position: relative; width: 100%; max-width: 420px;'>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); grid-template-rows: repeat(2, 1fr); width: 100%; aspect-ratio: 1 / 1; border: 2px solid #ced4da; border-radius: 12px; overflow: hidden; background: linear-gradient(135deg, rgba(248,249,250,0.9) 0%, rgba(233,236,239,0.9) 100%); box-shadow: 0 8px 20px rgba(0,0,0,0.05);'>

            <div style='position: relative; border-right: 1px solid #adb5bd; border-bottom: 1px solid #adb5bd; background-color: rgba(44,160,44,0.06); display: flex; align-items: flex-start; justify-content: flex-start; padding: 0.75rem;'>
            <span style='color: #2ca02c; font-size: 1.8rem; font-weight: 600;'>I</span>
            </div>

            <div style='position: relative; border-left: 1px solid #adb5bd; border-bottom: 1px solid #adb5bd; background-color: rgba(31,119,180,0.06); display: flex; align-items: flex-start; justify-content: flex-end; padding: 0.75rem;'>
            <span style='color: #1f77b4; font-size: 1.8rem; font-weight: 600;'>II</span>
            </div>

            <div style='position: relative; border-right: 1px solid #adb5bd; border-top: 1px solid #adb5bd; background-color: rgba(255,127,14,0.06); display: flex; align-items: flex-end; justify-content: flex-start; padding: 0.75rem;'>
            <span style='color: #ff7f0e; font-size: 1.8rem; font-weight: 600;'>III</span>
            </div>

            <div style='position: relative; border-left: 1px solid #adb5bd; border-top: 1px solid #adb5bd; background-color: rgba(214,39,40,0.06); display: flex; align-items: flex-end; justify-content: flex-end; padding: 0.75rem;'>
            <span style='color: #d62728; font-size: 1.8rem; font-weight: 600;'>IV</span>
            </div>

            </div>

            <div style='position: absolute; top: 16%; left: 24%; width: 12px; height: 12px; background: #6c757d; border-radius: 50%;'></div>
            <div style='position: absolute; top: 32%; left: 38%; width: 10px; height: 10px; background: #6c757d; border-radius: 50%; opacity: 0.9;'></div>
            <div style='position: absolute; top: 44%; left: 60%; width: 13px; height: 13px; background: #6c757d; border-radius: 50%; opacity: 0.8;'></div>
            <div style='position: absolute; top: 58%; left: 28%; width: 9px; height: 9px; background: #6c757d; border-radius: 50%; opacity: 0.75;'></div>
            <div style='position: absolute; top: 68%; left: 48%; width: 11px; height: 11px; background: #6c757d; border-radius: 50%; opacity: 0.85;'></div>
            <div style='position: absolute; top: 22%; right: 20%; width: 12px; height: 12px; background: #6c757d; border-radius: 50%;'></div>
            <div style='position: absolute; top: 36%; right: 30%; width: 9px; height: 9px; background: #6c757d; border-radius: 50%; opacity: 0.8;'></div>
            <div style='position: absolute; top: 52%; right: 18%; width: 10px; height: 10px; background: #6c757d; border-radius: 50%; opacity: 0.7;'></div>
            <div style='position: absolute; top: 64%; right: 32%; width: 12px; height: 12px; background: #6c757d; border-radius: 50%; opacity: 0.75;'></div>
            <div style='position: absolute; top: 78%; right: 22%; width: 8px; height: 8px; background: #6c757d; border-radius: 50%; opacity: 0.85;'></div>
            <div style='position: absolute; bottom: 24%; left: 22%; width: 11px; height: 11px; background: #6c757d; border-radius: 50%;'></div>
            <div style='position: absolute; bottom: 36%; left: 40%; width: 9px; height: 9px; background: #6c757d; border-radius: 50%; opacity: 0.9;'></div>
            <div style='position: absolute; bottom: 20%; left: 55%; width: 10px; height: 10px; background: #6c757d; border-radius: 50%; opacity: 0.8;'></div>
            <div style='position: absolute; bottom: 28%; right: 24%; width: 12px; height: 12px; background: #6c757d; border-radius: 50%; opacity: 0.85;'></div>
            <div style='position: absolute; bottom: 14%; right: 38%; width: 9px; height: 9px; background: #6c757d; border-radius: 50%; opacity: 0.78;'></div>

            <div style='position: absolute; bottom: -2.6rem; left: 50%; transform: translateX(-50%); color: #495057; font-size: 1.15rem; font-weight: 600;'>Higher Cost <span style='font-size: 1.8rem; line-height: 1;'>→</span></div>
            <div style='position: absolute; top: 50%; left: -7.6rem; transform: translateY(-50%) rotate(-90deg); color: #495057; font-size: 1.15rem; font-weight: 600; white-space: nowrap;'>Higher Graduation Rate <span style='font-size: 1.8rem; line-height: 1;'>→</span></div>

            </div>
            </div>
            """
        )
        st.markdown(quadrant_html, unsafe_allow_html=True)

        st.divider()

        # Reading the chart section
        st.markdown("### Reading the Chart: Four Quadrants")
        st.markdown(
            """
            The chart is divided into **four quadrants** using the median cost and graduation rate across all institutions.
            This creates a clear framework for comparing institutional performance:
            """
        )

        st.markdown("")  # Spacing

        # Quadrant grid layout (2x2)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #2ca02c; border-radius: 10px; background-color: #f8fff8; margin-bottom: 1rem;'>
                    <h4 style='color: #2ca02c; margin-bottom: 0.5rem;'>✓ Quadrant I</h4>
                    <h5 style='color: #000000; margin-bottom: 1rem;'>High Graduation, Low Cost</h5>
                    <p style='color: #000000; margin-bottom: 0.5rem;'>Institutions delivering strong outcomes at an affordable price.</p>
                    <p style='color: #000000; font-style: italic; margin: 0;'>This is the "best value" quadrant.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #1f77b4; border-radius: 10px; background-color: #f8faff; margin-bottom: 1rem;'>
                    <h4 style='color: #1f77b4; margin-bottom: 0.5rem;'>⚠ Quadrant II</h4>
                    <h5 style='color: #000000; margin-bottom: 1rem;'>High Graduation, High Cost</h5>
                    <p style='color: #000000; margin-bottom: 0.5rem;'>Institutions with high graduation rates, but at a higher tuition cost.</p>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Strong outcomes, premium pricing.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        col3, col4 = st.columns(2)

        with col3:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #ff7f0e; border-radius: 10px; background-color: #fffaf5; margin-bottom: 1rem;'>
                    <h4 style='color: #ff7f0e; margin-bottom: 0.5rem;'>⚠ Quadrant III</h4>
                    <h5 style='color: #000000; margin-bottom: 1rem;'>Low Graduation, Low Cost</h5>
                    <p style='color: #000000; margin-bottom: 0.5rem;'>Lower-cost institutions where graduation rates fall below the median.</p>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Affordability with outcome challenges.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                """
                <div style='padding: 1.5rem; border: 2px solid #d62728; border-radius: 10px; background-color: #fff5f5; margin-bottom: 1rem;'>
                    <h4 style='color: #d62728; margin-bottom: 0.5rem;'>✗ Quadrant IV</h4>
                    <h5 style='color: #000000; margin-bottom: 1rem;'>Low Graduation, High Cost</h5>
                    <p style='color: #000000; margin-bottom: 0.5rem;'>Institutions charging above-median tuition with below-median graduation rates.</p>
                    <p style='color: #000000; font-style: italic; margin: 0;'>Posing the greatest concern for affordability and student outcomes.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()

        # How to use section
        st.markdown("### How to Use This Tool")
        st.markdown(
            """
            **Below the chart**, you'll find a sortable table listing all institutions included in the analysis,
            showing sector (public, private not-for-profit, private for-profit), tuition cost, graduation rate,
            and enrollment.

            **Tabs at the top** allow you to view the list of institutions quadrant by quadrant, making it easy
            to explore institutions in each category.
            """
        )

        st.divider()

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
        
        self._render_value_grid_chart(config.label, dataset, config.min_enrollment)
    
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
