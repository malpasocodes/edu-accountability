"""Canonical IPEDS datasets explorer."""

from __future__ import annotations

from pathlib import Path
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from src.config.constants import (
    CANONICAL_IPEDS_SECTION,
    CANONICAL_DATASET_GRAD,
    CANONICAL_DATASET_PELL,
    CANONICAL_DATASET_LOANS,
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
        self._datasets = {
            CANONICAL_DATASET_GRAD: {
                "long": self._load_parquet(DataSources.CANONICAL_GRAD_LONG),
                "value_col": "grad_rate_150",
                "y_title": "Graduation Rate (150%)",
                "summary": self._load_parquet(DataSources.CANONICAL_GRAD_SUMMARY),
            },
            CANONICAL_DATASET_PELL: {
                "long": self._load_parquet(DataSources.CANONICAL_PELL_LONG),
                "value_col": "percent_pell",
                "y_title": "Percent Pell",
                "summary": self._load_parquet(DataSources.CANONICAL_PELL_SUMMARY),
            },
            CANONICAL_DATASET_LOANS: {
                "long": self._load_parquet(DataSources.CANONICAL_LOANS_LONG),
                "value_col": "percent_loans",
                "y_title": "Percent Federal Loans",
                "summary": self._load_parquet(DataSources.CANONICAL_LOANS_SUMMARY),
            },
        }

    def _load_parquet(self, source) -> pd.DataFrame:
        try:
            if hasattr(source, "path"):
                return self.loader.load_parquet(str(source.path), source.description)
            return self.loader.load_parquet(str(source), "Canonical IPEDS dataset")
        except DataLoadError as exc:
            st.warning(str(exc))
            return pd.DataFrame()

    def render_overview(self) -> None:
        self._render_overview_content(CANONICAL_DATASET_GRAD)

    def render_chart(self, chart_name: str) -> None:  # pragma: no cover
        if chart_name in self._datasets:
            self._render_overview_content(chart_name)
        else:
            st.error(f"Unknown chart: {chart_name}")

    def get_available_charts(self) -> List[str]:
        return list(self._datasets.keys())

    def _render_overview_content(self, dataset: str) -> None:
        self.render_section_header(CANONICAL_IPEDS_SECTION, dataset)
        dataset_info = self._datasets[dataset]
        df = dataset_info["long"]

        if df.empty:
            st.error("Canonical long-format data is unavailable.")
            return

        options = sorted(df["instnm"].dropna().unique())
        selected = st.selectbox(
            f"{dataset} Explorer",
            ["Select an institution"] + options,
            index=0,
        )

        if selected == "Select an institution":
            st.info(f"Pick an institution to view {dataset_info['y_title']} over time.")
            return

        inst_df = df[df["instnm"] == selected].sort_values("year")
        if inst_df.empty:
            st.warning("No canonical records found for the selected institution.")
            return

        value_col = dataset_info["value_col"]
        y_title = dataset_info["y_title"]
        chart = (
            alt.Chart(inst_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Cohort Year"),
                y=alt.Y(f"{value_col}:Q", title=y_title, scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip(f"{value_col}:Q", title=y_title, format=".1f"),
                    alt.Tooltip("source_flag:N", title="Source"),
                    alt.Tooltip("is_revised:N", title="Revised"),
                ],
            )
            .properties(height=400, title=f"{dataset} — {selected}")
        )
        st.altair_chart(chart.interactive(), use_container_width=True)
