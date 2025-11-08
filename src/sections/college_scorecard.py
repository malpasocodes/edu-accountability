"""College Scorecard canonical metrics explorer (median debt and 3-year repayment)."""

from __future__ import annotations

from typing import List

import altair as alt
import pandas as pd
import streamlit as st

from src.config.constants import (
    SCORECARD_SECTION,
    SCORECARD_OVERVIEW_LABEL,
    SCORECARD_DATASET_MEDIAN_DEBT,
    SCORECARD_DATASET_REPAYMENT_3YR,
    SCORECARD_DATASET_REPAYMENT_SCATTER_FOUR,
    SCORECARD_DATASET_REPAYMENT_SCATTER_TWO,
)
from src.config.data_sources import DataSources
from src.core.data_loader import DataLoader
from src.core.exceptions import DataLoadError
from .base import BaseSection


class CollegeScorecardSection(BaseSection):
    def __init__(self, data_manager):
        super().__init__(data_manager)
        self.loader: DataLoader = data_manager.loader
        self._long = self._load_parquet(DataSources.SCORECARD_DEBT_REPAY_LONG)
        self._latest = self._load_parquet(DataSources.SCORECARD_DEBT_REPAY_LATEST)
        self._summary = self._load_parquet(DataSources.SCORECARD_DEBT_REPAY_SUMMARY)

    def _load_parquet(self, source) -> pd.DataFrame:
        try:
            return self.loader.load_parquet(str(source.path), source.description)
        except DataLoadError as exc:
            st.warning(str(exc))
            return pd.DataFrame()

    def render_overview(self) -> None:
        st.info("Select an institution to explore median debt and 3-year repayment.")
        self.render_chart(SCORECARD_DATASET_MEDIAN_DEBT)

    def render_chart(self, chart_name: str) -> None:  # pragma: no cover
        if chart_name == SCORECARD_DATASET_MEDIAN_DEBT:
            self._render_median_debt()
        elif chart_name == SCORECARD_DATASET_REPAYMENT_3YR:
            self._render_repayment_3yr()
        elif chart_name == SCORECARD_DATASET_REPAYMENT_SCATTER_FOUR:
            self._render_repayment_scatter(level_filter="4-year")
        elif chart_name == SCORECARD_DATASET_REPAYMENT_SCATTER_TWO:
            self._render_repayment_scatter(level_filter="2-year")
        else:
            st.error(f"Unknown chart: {chart_name}")

    def get_available_charts(self) -> List[str]:
        return [
            SCORECARD_DATASET_MEDIAN_DEBT,
            SCORECARD_DATASET_REPAYMENT_3YR,
            SCORECARD_DATASET_REPAYMENT_SCATTER_FOUR,
            SCORECARD_DATASET_REPAYMENT_SCATTER_TWO,
        ]

    def _select_institution(self, df: pd.DataFrame) -> str | None:
        if df.empty:
            st.error("Scorecard data is unavailable.")
            return None
        options = sorted(df["instnm"].dropna().unique())
        selection = st.selectbox("Institution", ["Select an institution"] + options, index=0)
        if selection == "Select an institution":
            return None
        return selection

    def _render_median_debt(self) -> None:
        self.render_section_header(SCORECARD_SECTION, SCORECARD_DATASET_MEDIAN_DEBT)
        df = self._long
        inst = self._select_institution(df)
        if not inst:
            return
        inst_df = df[df["instnm"] == inst].sort_values("year")
        if inst_df.empty:
            st.warning("No records for selection.")
            return
        chart = (
            alt.Chart(inst_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("median_debt_completers:Q", title="Median Debt (Completers)", scale=alt.Scale(zero=True)),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip("median_debt_completers:Q", title="Median Debt", format="$,.0f"),
                    alt.Tooltip("control:N", title="Control"),
                    alt.Tooltip("level:N", title="Level"),
                ],
            )
            .properties(height=380, title=f"Median Debt — {inst}")
        )
        st.altair_chart(chart.interactive(), use_container_width=True)

    def _render_repayment_3yr(self) -> None:
        self.render_section_header(SCORECARD_SECTION, SCORECARD_DATASET_REPAYMENT_3YR)
        df = self._long
        inst = self._select_institution(df)
        if not inst:
            return
        inst_df = df[df["instnm"] == inst]
        if inst_df.empty:
            st.warning("No records for selection.")
            return
        repay_cols = [c for c in inst_df.columns if c.startswith("repay_3yr_")]
        # Determine years with any repayment data present for this institution
        year_has_data = (
            inst_df[["year"] + repay_cols]
            .assign(_has=inst_df[repay_cols].notna().any(axis=1))
            .loc[lambda d: d["_has"], "year"]
            .dropna()
            .astype(int)
            .sort_values()
            .unique()
        )
        if len(year_has_data) == 0:
            st.info("No 3-year repayment data available for this institution.")
            return
        latest_year = int(year_has_data[-1])
        if len(year_has_data) == 1:
            year = latest_year
            st.caption(f"Showing {year} (only year with 3-year repayment data).")
        else:
            year = st.slider(
                "Year",
                min_value=int(year_has_data[0]),
                max_value=int(year_has_data[-1]),
                value=latest_year,
            )
        year_df = inst_df[inst_df["year"] == year]
        if year_df.empty:
            st.warning("No data for selected year.")
            return
        melted = year_df.melt(
            id_vars=["unitid", "instnm", "year"], value_vars=repay_cols, var_name="status", value_name="percent"
        ).dropna(subset=["percent"])  # drop empty categories to avoid blank chart
        # Pretty labels
        label_map = {
            "repay_3yr_forbearance": "Forbearance",
            "repay_3yr_not_making_progress": "Not Making Progress",
            "repay_3yr_deferment": "Deferment",
            "repay_3yr_default": "Defaulted",
            "repay_3yr_making_progress": "Making Progress",
            "repay_3yr_delinquent": "Delinquent",
            "repay_3yr_paid_in_full": "Paid in Full",
            "repay_3yr_discharged": "Discharged",
        }
        melted["status_label"] = melted["status"].map(label_map)

        # Keep a stable display order similar to the website
        order = [
            "Forbearance",
            "Not Making Progress",
            "Deferment",
            "Defaulted",
            "Making Progress",
            "Delinquent",
            "Paid in Full",
            "Discharged",
        ]
        melted["status_label"] = pd.Categorical(melted["status_label"], categories=order, ordered=True)

        chart = (
            alt.Chart(melted)
            .mark_bar()
            .encode(
                x=alt.X("status_label:N", title="Repayment Status", sort=order),
                y=alt.Y("percent:Q", title="Percent", scale=alt.Scale(domain=[0, 100])),
                tooltip=[alt.Tooltip("percent:Q", title="Percent", format=".1f")],
                color=alt.Color("status_label:N", legend=None),
            )
            .properties(height=380, title=f"3-year Repayment Status — {inst} ({year})")
        )
        text_layer = chart.mark_text(dy=-10, color="#333", fontWeight="bold").encode(
            text=alt.Text("percent:Q", format=".1f")
        )
        st.altair_chart(chart + text_layer, use_container_width=True)

        # Consolidated traffic-light summary
        consolidation_map = {
            "Making Progress": "Green",
            "Paid in Full": "Green",
            "Discharged": "Green",
            "Forbearance": "Yellow",
            "Not Making Progress": "Yellow",
            "Deferment": "Yellow",
            "Defaulted": "Red",
            "Delinquent": "Red",
        }
        consolidated = (
            melted.assign(group=melted["status_label"].map(consolidation_map))
            .dropna(subset=["group"])
            .groupby("group", as_index=False)["percent"].sum()
        )
        if not consolidated.empty:
            color_scale = alt.Scale(domain=["Green", "Yellow", "Red"], range=["#2ca02c", "#f2c037", "#d62728"])
            summary_chart = (
                alt.Chart(consolidated)
                .mark_bar()
                .encode(
                    x=alt.X("group:N", title="Consolidated Status"),
                    y=alt.Y("percent:Q", title="Percent", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color("group:N", scale=color_scale, legend=None),
                    tooltip=[alt.Tooltip("group:N", title="Group"), alt.Tooltip("percent:Q", title="Percent", format=".1f")],
                )
                .properties(title="Traffic-light summary", height=220)
            )
            summary_text = summary_chart.mark_text(dy=-10, color="#333", fontWeight="bold").encode(
                text=alt.Text("percent:Q", format=".1f")
            )
            st.altair_chart(summary_chart + summary_text, use_container_width=True)
            descriptions = {
                "Green": "Loans are paid in full, discharged, or actively amortizing (making progress).",
                "Yellow": "Loans are paused or not reducing balances (forbearance, deferment, not making progress).",
                "Red": "Loans are delinquent or in default.",
            }
            st.markdown(
                "\n".join(
                    f"**{group}:** {descriptions[group]}" for group in ["Green", "Yellow", "Red"] if group in consolidated["group"].values
                )
            )

    def _render_repayment_scatter(self, level_filter: str) -> None:
        label = (
            SCORECARD_DATASET_REPAYMENT_SCATTER_FOUR
            if level_filter == "4-year"
            else SCORECARD_DATASET_REPAYMENT_SCATTER_TWO
        )
        self.render_section_header(SCORECARD_SECTION, label)
        df = self._latest
        if df.empty:
            st.error("Scorecard latest dataset unavailable.")
            return
        view = df[df["level"] == level_filter].copy()
        if view.empty:
            st.info(f"No {level_filter} institutions available.")
            return
        enrollment_options = {
            "All": 0,
            ">1,000": 1000,
            ">5,000": 5000,
            ">10,000": 10000,
        }
        selected_filter = st.selectbox("Minimum enrollment", list(enrollment_options.keys()), index=0)
        min_enrollment = enrollment_options[selected_filter]
        view = view[view["enrollment"].fillna(0) >= min_enrollment]
        if view.empty:
            st.warning("No institutions meet the enrollment filter.")
            return

        status_choice = st.radio(
            "Consolidated status",
            ["Red", "Yellow", "Green"],
            index=0,
            horizontal=True,
        )
        status_column = {
            "Green": "repay_3yr_green",
            "Yellow": "repay_3yr_yellow",
            "Red": "repay_3yr_red",
        }[status_choice]
        metric_label = f"{status_choice} Share (%)"

        view = view.dropna(subset=["median_debt_completers", status_column, "enrollment"])
        if view.empty:
            st.warning("No data available after filtering.")
            return

        chart = (
            alt.Chart(view)
            .mark_circle(opacity=0.8)
            .encode(
                x=alt.X("median_debt_completers:Q", title="Median Debt (Completers)", scale=alt.Scale(zero=False)),
                y=alt.Y(f"{status_column}:Q", title=metric_label, scale=alt.Scale(domain=[0, 100])),
                size=alt.Size(
                    "enrollment:Q",
                    title="Enrollment",
                    scale=alt.Scale(domain=[view["enrollment"].min(), view["enrollment"].max()], range=[40, 800]),
                ),
                color=alt.Color("sector:N", title="Sector"),
                tooltip=[
                    alt.Tooltip("instnm:N", title="Institution"),
                    alt.Tooltip("median_debt_completers:Q", title="Median Debt", format="$,.0f"),
                    alt.Tooltip(f"{status_column}:Q", title=metric_label, format=".1f"),
                    alt.Tooltip("enrollment:Q", title="Enrollment", format=",.0f"),
                    alt.Tooltip("sector:N", title="Sector"),
                ],
            )
            .properties(height=500)
        )
        st.altair_chart(chart.interactive(), use_container_width=True)
