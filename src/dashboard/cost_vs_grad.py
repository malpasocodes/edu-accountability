"""Streamlit layout and interaction for the Cost vs. Graduation dashboard."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter


MIN_ENROLLMENT_THRESHOLD = 1000


def _minimum_enrollment_for_label(label: str) -> int:
    if "2-year" in label.lower():
        return 0
    return MIN_ENROLLMENT_THRESHOLD


@dataclass(frozen=True)
class PreparedDataset:
    frame: pd.DataFrame
    enrollment_values: np.ndarray


@st.cache_data(show_spinner=False)
def _prepare_dataset(label: str, df: pd.DataFrame) -> PreparedDataset:
    """Standardize, sort, and cache dataset details for quick filtering."""

    _ = label  # included to differentiate cache entries per dataset label

    if "enrollment" not in df.columns:
        working = df.assign(enrollment=0)
    else:
        working = df.copy()

    working["enrollment"] = pd.to_numeric(working["enrollment"], errors="coerce").fillna(0)
    sorted_frame = (
        working.sort_values("enrollment", kind="mergesort").reset_index(drop=True)
    )
    enrollment_values = sorted_frame["enrollment"].to_numpy(copy=True)

    return PreparedDataset(frame=sorted_frame, enrollment_values=enrollment_values)


ENROLLMENT_CHOICES = [0, 1000, 10000, 50000]


def render_dashboard(datasets: dict[str, pd.DataFrame]) -> None:
    """Render sidebar controls and the cost-versus-graduation visualizations."""

    prepared = {label: _prepare_dataset(label, df) for label, df in datasets.items()}
    medians = {
        label: (
            bundle.frame["cost"].median(),
            bundle.frame["graduation_rate"].median(),
        )
        for label, bundle in prepared.items()
    }

    all_sectors = sorted(
        {
            sector
            for bundle in prepared.values()
            for sector in bundle.frame["sector"].dropna().unique()
        }
    )
    default_sectors = [
        "Public",
        "Private, not-for-profit",
        "Private, for-profit",
    ]
    default_selection = [sector for sector in default_sectors if sector in all_sectors] or all_sectors

    all_states = sorted(
        {
            state
            for bundle in prepared.values()
            for state in bundle.frame["state"].dropna().unique()
        }
    )
    state_all_label = "All States"

    st.sidebar.header("Chart Explorer")
    st.sidebar.write("Cost vs Graduation Rate")

    sector_container = st.sidebar.container()
    sector_container.markdown("**Sectors**")
    selected_sectors = [
        sector
        for sector in all_sectors
        if sector_container.checkbox(
            sector,
            value=sector in default_selection,
            key=f"sector_{sector.lower().replace(' ', '_').replace(',', '').replace('-', '_')}",
        )
    ]

    state_options = [state_all_label] + all_states
    selected_states = st.sidebar.multiselect(
        "States",
        options=state_options,
        default=[state_all_label],
        help="Pick one or more states; choose 'All States' to include every state.",
    )

    if state_all_label in selected_states or not selected_states:
        active_states = all_states
    else:
        active_states = [state for state in selected_states if state in all_states]

    tabs = st.tabs(list(prepared.keys()))
    for tab, label in zip(tabs, prepared.keys()):
        with tab:
            min_enrollment = _minimum_enrollment_for_label(label)

            bundle = prepared[label]
            if not bundle.frame.empty:
                start_idx = int(
                    np.searchsorted(
                        bundle.enrollment_values,
                        min_enrollment,
                        side="left",
                    )
                )
                enrollment_filtered = bundle.frame.iloc[start_idx:]
            else:
                enrollment_filtered = bundle.frame

            if selected_sectors:
                sector_filtered = enrollment_filtered[enrollment_filtered["sector"].isin(selected_sectors)]
            else:
                sector_filtered = enrollment_filtered.iloc[0:0]

            if active_states:
                filtered = sector_filtered[sector_filtered["state"].isin(active_states)]
            else:
                filtered = sector_filtered.iloc[0:0]

            filtered = filtered.loc[:, [
                col
                for col in [
                    "institution",
                    "sector",
                    "cost",
                    "graduation_rate",
                    "enrollment",
                    "state",
                ]
                if col in filtered.columns
            ]]

            cost_median, grad_median = medians[label]
            render_cost_vs_grad_scatter(
                filtered,
                min_enrollment=min_enrollment,
                global_cost_median=cost_median,
                global_grad_median=grad_median,
                group_label=label,
            )
