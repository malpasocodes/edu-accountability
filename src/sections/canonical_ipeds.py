"""Canonical IPEDS datasets explorer."""

from __future__ import annotations

from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from src.config.constants import (
    CANONICAL_IPEDS_SECTION,
    CANONICAL_DATASET_GRAD,
)
from src.config.data_sources import DataSources
from src.core.data_loader import DataLoader
from src.core.exceptions import DataLoadError
from .base import BaseSection


class CanonicalIPEDSSection(BaseSection):
    """Displays canonical IPEDS datasets (graduation, Pell, etc.)."""

    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.loader: DataLoader = data_manager.loader
        self._latest_df = self._load_parquet(DataSources.CANONICAL_GRAD_LATEST)
        self._summary_df = self._load_parquet(DataSources.CANONICAL_GRAD_SUMMARY)
        self._long_df = self._load_parquet(DataSources.CANONICAL_GRAD_LONG)

    def _load_parquet(self, source) -> pd.DataFrame:
        try:
            return self.loader.load_parquet(str(source.path), source.description)
        except DataLoadError as exc:
            st.warning(str(exc))
            return pd.DataFrame()

    def render_overview(self) -> None:
        self._render_overview_content()

    def render_chart(self, chart_name: str) -> None:  # pragma: no cover
        if chart_name == CANONICAL_DATASET_GRAD:
            self._render_overview_content()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def get_available_charts(self) -> List[str]:
        return [CANONICAL_DATASET_GRAD]

    def _render_overview_content(self) -> None:
        self.render_section_header(CANONICAL_IPEDS_SECTION, CANONICAL_DATASET_GRAD)

        if self._long_df.empty:
            st.error("Canonical long-format data is unavailable.")
            return

        options = sorted(self._long_df["instnm"].dropna().unique())
        selected = st.selectbox(
            "Explorer",
            ["Select an institution"] + options,
            index=0,
        )

        if selected == "Select an institution":
            st.info("Pick an institution to view canonical 150% graduation rates over time.")
            return

        inst_df = self._long_df[self._long_df["instnm"] == selected].sort_values("year")
        if inst_df.empty:
            st.warning("No canonical records found for the selected institution.")
            return

        chart = (
            alt.Chart(inst_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Cohort Year"),
                y=alt.Y("grad_rate_150:Q", title="Graduation Rate (150%)", scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip("grad_rate_150:Q", title="Rate", format=".1f"),
                    alt.Tooltip("source_flag:N", title="Source"),
                    alt.Tooltip("is_revised:N", title="Revised"),
                ],
            )
            .properties(height=400, title=f"Canonical Trend — {selected}")
        )
        st.altair_chart(chart.interactive(), use_container_width=True)

    def _render_trend_chart(self, sector_filter: str) -> None:
        if self._summary_df.empty:
            return

        st.markdown("### Yearly Trend")

        summary_df = self._summary_df.copy()
        if sector_filter != "All sectors" and sector_filter in summary_df["sector"].values:
            trend_df = summary_df[summary_df["sector"] == sector_filter].copy()
            legend_title = sector_filter
        else:
            trend_df = (
                summary_df.groupby("year", as_index=False)
                .agg(
                    institution_count=("institution_count", "sum"),
                    avg_grad_rate=("avg_grad_rate", "mean"),
                    median_grad_rate=("median_grad_rate", "mean"),
                )
            )
            trend_df["sector"] = "All sectors"
            legend_title = "All sectors"

        melted = trend_df.melt(
            id_vars=["year", "sector", "institution_count"],
            value_vars=["avg_grad_rate", "median_grad_rate"],
            var_name="Metric",
            value_name="Rate",
        )
        metric_map = {
            "avg_grad_rate": "Average",
            "median_grad_rate": "Median",
        }
        melted["Metric"] = melted["Metric"].map(metric_map)

        chart = (
            alt.Chart(melted)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Cohort Year"),
                y=alt.Y("Rate:Q", title="Graduation Rate (150%)", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("Metric:N", title="Metric"),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip("Metric:N"),
                    alt.Tooltip("Rate:Q", title="Rate", format=".1f"),
                    alt.Tooltip("institution_count:Q", title="# Institutions"),
                ],
            )
            .properties(height=400)
        )

        st.altair_chart(chart.interactive(), use_container_width=True)
        st.caption(f"Sector: {legend_title}. Data: canonical IPEDS pipeline summary.")

    def _render_four_year_comparison(self) -> None:
        if self._summary_df.empty:
            return

        four_year_sectors = [
            "Public, 4-year or above",
            "Private nonprofit, 4-year or above",
            "Private for-profit, 4-year or above",
        ]

        subset = self._summary_df[
            self._summary_df["sector"].isin(four_year_sectors)
        ].copy()

        if subset.empty:
            return

        st.markdown("### Four-year Sector Trajectories")
        st.caption(
            "Median 150% graduation rates by cohort year, comparing the three 4-year sectors."
        )

        chart_df = subset.rename(columns={"median_grad_rate": "Median Rate"})

        chart = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Cohort Year"),
                y=alt.Y("Median Rate:Q", title="Median Graduation Rate (150%)", scale=alt.Scale(domain=[0, 100])),
                color=alt.Color("sector:N", title="Sector"),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip("sector:N", title="Sector"),
                    alt.Tooltip("Median Rate:Q", title="Median Rate", format=".1f"),
                    alt.Tooltip("institution_count:Q", title="# Institutions"),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart.interactive(), use_container_width=True)
