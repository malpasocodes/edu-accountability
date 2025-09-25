"""Streamlit layout and interaction for the Cost vs. Graduation dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter


def _prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    if "enrollment" not in df.columns:
        prepared = df.assign(enrollment=0)
    else:
        prepared = df.copy()
    prepared["enrollment"] = pd.to_numeric(
        prepared["enrollment"], errors="coerce"
    ).fillna(0)
    return prepared


def _build_enrollment_options(max_enrollment: int) -> list[int]:
    if max_enrollment <= 0:
        return [0]

    base_setpoints = [0, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
    options: list[int] = []
    for point in base_setpoints:
        if point <= max_enrollment and point not in options:
            options.append(point)

    if max_enrollment < 100000 and max_enrollment not in options:
        options.append(max_enrollment)

    if not options:
        options = [max_enrollment]

    return options


def render_dashboard(datasets: dict[str, pd.DataFrame]) -> None:
    """Render sidebar controls and the cost-versus-graduation visualizations."""

    prepared = {label: _prepare_dataset(df) for label, df in datasets.items()}
    medians = {
        label: (
            frame["cost"].median(),
            frame["graduation_rate"].median(),
        )
        for label, frame in prepared.items()
    }

    max_enrollment = max(
        (int(frame["enrollment"].max()) for frame in prepared.values() if not frame.empty),
        default=0,
    )
    slider_max = max(0, max_enrollment)

    all_sectors = sorted(
        {
            sector
            for frame in prepared.values()
            for sector in frame["sector"].dropna().unique()
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
            for frame in prepared.values()
            for state in frame["state"].dropna().unique()
        }
    )
    state_all_label = "All States"

    st.sidebar.header("Chart Explorer")
    st.sidebar.write("Cost vs Graduation Rate")

    enrollment_options = _build_enrollment_options(slider_max)
    default_value = 1000 if slider_max >= 1000 else slider_max
    if default_value not in enrollment_options:
        default_value = enrollment_options[-1]

    min_enrollment = st.sidebar.selectbox(
        "Minimum undergraduate enrollment",
        options=enrollment_options,
        index=enrollment_options.index(default_value),
        help="Filter institutions by undergraduate degree-seeking enrollment (ENR_UGD).",
    )

    selected_sectors = st.sidebar.multiselect(
        "Sectors",
        options=all_sectors,
        default=default_selection,
    )

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
            frame = prepared[label]
            filtered = frame.loc[
                (frame["enrollment"] >= min_enrollment)
                & (frame["sector"].isin(selected_sectors))
                & (frame["state"].isin(active_states))
            ]

            cost_median, grad_median = medians[label]
            render_cost_vs_grad_scatter(
                filtered,
                min_enrollment=min_enrollment,
                global_cost_median=cost_median,
                global_grad_median=grad_median,
                group_label=label,
            )
