"""Graduation Rates (Alpha) section powered by canonical data."""

from __future__ import annotations

from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from src.config.constants import (
    GRAD_ALPHA_SECTION,
    GRAD_ALPHA_OVERVIEW_LABEL,
)
from src.config.data_sources import DataSources
from src.core.data_loader import DataLoader
from src.core.exceptions import DataLoadError
from .base import BaseSection


class GraduationAlphaSection(BaseSection):
    """Displays canonical IPEDS graduation pipeline outputs."""

    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.loader: DataLoader = data_manager.loader
        self._latest_df = self._load_parquet(DataSources.CANONICAL_GRAD_LATEST)
        self._summary_df = self._load_parquet(DataSources.CANONICAL_GRAD_SUMMARY)

    def _load_parquet(self, source) -> pd.DataFrame:
        try:
            return self.loader.load_parquet(str(source.path), source.description)
        except DataLoadError as exc:
            st.warning(str(exc))
            return pd.DataFrame()

    def render_overview(self) -> None:
        self._render_overview_content()

    def render_chart(self, chart_name: str) -> None:  # pragma: no cover - single-chart section
        if chart_name == GRAD_ALPHA_OVERVIEW_LABEL:
            self._render_overview_content()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def get_available_charts(self) -> List[str]:
        return [GRAD_ALPHA_OVERVIEW_LABEL]

    def _render_overview_content(self) -> None:
        self.render_section_header(GRAD_ALPHA_SECTION, "Canonical Overview")

        if self._latest_df.empty:
            st.error("Canonical graduation dataset is unavailable.")
            return

        st.markdown(
            "This alpha view surfaces the new canonical IPEDS graduation pipeline, "
            "featuring 150% completion rates with explicit DRV/DFR provenance."
        )

        state_options = ["All states"] + sorted(
            filter(None, self._latest_df["state"].dropna().unique())
        )
        sector_options = ["All sectors"] + sorted(
            filter(None, self._latest_df["sector"].dropna().unique())
        )

        col_filters = st.columns(2)
        with col_filters[0]:
            state_filter = st.selectbox("State", state_options)
        with col_filters[1]:
            sector_filter = st.selectbox("Sector", sector_options)

        filtered = self._latest_df.copy()
        if state_filter != "All states":
            filtered = filtered[filtered["state"] == state_filter]
        if sector_filter != "All sectors":
            filtered = filtered[filtered["sector"] == sector_filter]

        if filtered.empty:
            st.warning("No institutions match the selected filters.")
        else:
            col_metrics = st.columns(3)
            with col_metrics[0]:
                st.metric("Institutions", f"{filtered['unitid'].nunique():,}")
            with col_metrics[1]:
                median_rate = filtered["grad_rate_150"].median()
                st.metric("Median Grad Rate", f"{median_rate:.1f}%" if pd.notna(median_rate) else "N/A")
            with col_metrics[2]:
                latest_year = filtered["year"].max()
                st.metric("Latest Cohort Year", int(latest_year) if pd.notna(latest_year) else "N/A")

            st.markdown("### Top Institutions by 150% Graduation Rate")
            preview = (
                filtered.sort_values("grad_rate_150", ascending=False)
                .head(25)
                .loc[:, ["instnm", "state", "sector", "year", "grad_rate_150", "source_flag", "is_revised"]]
                .rename(
                    columns={
                        "instnm": "Institution",
                        "state": "State",
                        "sector": "Sector",
                        "year": "Cohort Year",
                        "grad_rate_150": "Grad Rate (150%)",
                        "source_flag": "Source",
                        "is_revised": "Revised",
                    }
                )
            )
            st.dataframe(preview, hide_index=True, use_container_width=True)

        self._render_trend_chart(sector_filter)

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
