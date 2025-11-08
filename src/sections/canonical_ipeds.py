"""Canonical IPEDS datasets explorer."""

from __future__ import annotations

from pathlib import Path
from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from src.config.constants import (
    CANONICAL_IPEDS_SECTION,
    CANONICAL_IPEDS_OVERVIEW_LABEL,
    CANONICAL_DATASET_GRAD,
    CANONICAL_DATASET_PELL,
    CANONICAL_DATASET_LOANS,
    CANONICAL_DATASET_RETENTION,
    CANONICAL_DATASET_RETENTION_RATE,
    CANONICAL_DATASET_GRAD_Z,
)
from src.analytics.grad_zscores import (
    HEADCOUNT_THRESHOLDS,
    compute_peer_distribution,
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
            CANONICAL_DATASET_GRAD: self._build_dataset_config(
                long_source=DataSources.CANONICAL_GRAD_LONG,
                summary_source=DataSources.CANONICAL_GRAD_SUMMARY,
                value_col="grad_rate_150",
                y_title="Graduation Rate (150%)",
                y_domain=[0, 100],
                value_format=".1f",
            ),
            CANONICAL_DATASET_PELL: self._build_dataset_config(
                long_source=DataSources.CANONICAL_PELL_LONG,
                summary_source=DataSources.CANONICAL_PELL_SUMMARY,
                value_col="percent_pell",
                y_title="Percent Pell",
                y_domain=[0, 100],
                value_format=".1f",
            ),
            CANONICAL_DATASET_LOANS: self._build_dataset_config(
                long_source=DataSources.CANONICAL_LOANS_LONG,
                summary_source=DataSources.CANONICAL_LOANS_SUMMARY,
                value_col="percent_loans",
                y_title="Percent Federal Loans",
                y_domain=[0, 100],
                value_format=".1f",
            ),
            CANONICAL_DATASET_RETENTION: self._build_dataset_config(
                long_source=DataSources.CANONICAL_RETENTION_LONG,
                summary_source=DataSources.CANONICAL_RETENTION_SUMMARY,
                value_col="retained_students_full_time",
                y_title="Full-time Cohort Size",
                y_domain=None,
                value_format=",.0f",
            ),
            CANONICAL_DATASET_RETENTION_RATE: self._build_dataset_config(
                long_source=DataSources.CANONICAL_RETENTION_RATE_LONG,
                summary_source=DataSources.CANONICAL_RETENTION_RATE_SUMMARY,
                value_col="retention_rate_full_time",
                y_title="Full-time Retention Rate (%)",
                y_domain=[0, 100],
                value_format=".1f",
            ),
        }
        self._special_charts = {
            CANONICAL_DATASET_GRAD_Z: self._render_grad_quadrants_view,
        }

    def _build_dataset_config(
        self,
        *,
        long_source,
        summary_source,
        value_col: str,
        y_title: str,
        y_domain: list[int] | None,
        value_format: str,
    ) -> dict:
        return {
            "long": self._load_parquet(long_source),
            "summary": self._load_parquet(summary_source),
            "value_col": value_col,
            "y_title": y_title,
            "y_domain": y_domain,
            "value_format": value_format,
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
        st.info("Use the sidebar to switch between canonical datasets.")
        self._render_overview_content(CANONICAL_DATASET_GRAD)

    def render_chart(self, chart_name: str) -> None:  # pragma: no cover
        if chart_name in self._datasets:
            self._render_overview_content(chart_name)
        elif chart_name in self._special_charts:
            self._special_charts[chart_name]()
        else:
            st.error(f"Unknown chart: {chart_name}")

    def get_available_charts(self) -> List[str]:
        return list(self._datasets.keys()) + list(self._special_charts.keys())

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
        y_domain = dataset_info.get("y_domain")
        value_format = dataset_info.get("value_format", ".1f")

        y_scale = alt.Scale(domain=y_domain) if y_domain else alt.Scale(zero=True)
        chart = (
            alt.Chart(inst_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Cohort Year"),
                y=alt.Y(f"{value_col}:Q", title=y_title, scale=y_scale),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip(f"{value_col}:Q", title=y_title, format=value_format),
                    alt.Tooltip("source_flag:N", title="Source"),
                    alt.Tooltip("is_revised:N", title="Revised"),
                ],
            )
            .properties(height=400, title=f"{dataset} — {selected}")
        )
        st.altair_chart(chart.interactive(), use_container_width=True)

    def _render_grad_quadrants_view(self) -> None:
        self.render_section_header(CANONICAL_IPEDS_SECTION, CANONICAL_DATASET_GRAD_Z)

        canonical_df = getattr(self.data_manager, "canonical_grad_df", pd.DataFrame())
        headcount_df = getattr(self.data_manager, "headcount_df", pd.DataFrame())
        headcount_fallback = getattr(
            self.data_manager, "headcount_fallback_map", None
        )

        if canonical_df.empty:
            st.warning("Canonical graduation data is not available.")
            return

        available_years = sorted(canonical_df["year"].dropna().unique())
        if not available_years:
            st.warning("No cohort years available for canonical graduation data.")
            return

        col_year, col_threshold = st.columns(2)
        selected_year = int(
            col_year.selectbox(
                "Cohort year",
                options=available_years[::-1],
                index=0,
            )
        )
        threshold_options = [cfg["label"] for cfg in HEADCOUNT_THRESHOLDS]
        selected_threshold = col_threshold.selectbox(
            "Headcount filter",
            options=threshold_options,
            index=0,
        )

        try:
            peer_df, stats, _ = compute_peer_distribution(
                canonical_df,
                headcount_df,
                year=selected_year,
                threshold_label=selected_threshold,
                fallback_series=headcount_fallback,
            )
        except (ValueError, KeyError) as exc:
            st.warning(f"Unable to compute distribution: {exc}")
            return

        if peer_df.empty:
            st.info("No institutions available after applying the selected filters.")
            return

        peer_df = peer_df.copy()
        peer_df["z_score"] = pd.to_numeric(peer_df["z_score"], errors="coerce")
        peer_df["grad_rate_150"] = pd.to_numeric(
            peer_df["grad_rate_150"], errors="coerce"
        )

        quadrant_labels = [
            ("🚀 High (z > 1)", lambda z: z > 1),
            ("👍 Above Avg (0 < z ≤ 1)", lambda z: (z > 0) & (z <= 1)),
            ("⚖️ Slightly Below (-1 ≤ z ≤ 0)", lambda z: (z >= -1) & (z <= 0)),
            ("⚠️ Low (z < -1)", lambda z: z < -1),
        ]

        def _label_quadrant(value: float | None) -> str:
            if pd.isna(value):
                return "No z-score"
            for label, matcher in quadrant_labels:
                if matcher(value):
                    return label
            return "No z-score"

        peer_df["quadrant"] = peer_df["z_score"].apply(_label_quadrant)

        chart = (
            alt.Chart(peer_df)
            .mark_circle(size=80, opacity=0.8)
            .encode(
                x=alt.X(
                    "z_score:Q",
                    title="Z-score",
                    scale=alt.Scale(domain=[peer_df["z_score"].min() - 0.5, peer_df["z_score"].max() + 0.5]),
                ),
                y=alt.Y(
                    "grad_rate_150:Q",
                    title="Graduation Rate (150%)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                color=alt.Color("sector:N", title="Sector"),
                tooltip=[
                    alt.Tooltip("instnm:N", title="Institution"),
                    alt.Tooltip("grad_rate_150:Q", title="Grad rate", format=".1f"),
                    alt.Tooltip("z_score:Q", title="Z-score", format=".2f"),
                    alt.Tooltip("ft_ug_headcount:Q", title="Headcount", format=",.0f"),
                    alt.Tooltip("sector:N", title="Sector"),
                ],
            )
            .interactive()
            .properties(height=400, title="Graduation rate distribution by z-score")
        )

        dividers = alt.Chart(pd.DataFrame({"z": [-1, 0, 1]})).mark_rule(
            color="#555555", strokeDash=[6, 4]
        ).encode(x="z:Q")

        st.altair_chart((chart + dividers), use_container_width=True)

        headcount_descriptor = (
            f"≥ {stats.min_headcount:,} FT undergraduate 12-month headcount"
            if stats.min_headcount > 0
            else "All institutions"
        )
        st.caption(
            f"Peer group: {stats.peer_count:,} institutions • {headcount_descriptor} • "
            f"Mean rate {stats.mean:.1f}% | Median {stats.median:.1f}%"
        )

        tabs = st.tabs([label for label, _ in quadrant_labels])
        for tab, (label, _) in zip(tabs, quadrant_labels):
            subset = (
                peer_df[peer_df["quadrant"] == label]
                .sort_values("z_score", ascending=False)
                .loc[:, ["instnm", "grad_rate_150", "z_score", "sector", "ft_ug_headcount"]]
            )
            subset.rename(
                columns={
                    "instnm": "Institution",
                    "grad_rate_150": "Grad rate (150%)",
                    "z_score": "Z-score",
                    "sector": "Sector",
                    "ft_ug_headcount": "FT UG headcount",
                },
                inplace=True,
            )
            with tab:
                if subset.empty:
                    st.write("No institutions in this quadrant.")
                else:
                    st.dataframe(
                        subset,
                        hide_index=True,
                        use_container_width=True,
                    )
