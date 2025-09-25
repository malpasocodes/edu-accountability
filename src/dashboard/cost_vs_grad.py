"""Streamlit layout and interaction for the Cost vs. Graduation dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter


def render_dashboard(data: pd.DataFrame) -> None:
    """Render sidebar controls and the cost-versus-graduation visualization."""

    if "enrollment" not in data.columns:
        working = data.assign(enrollment=0)
    else:
        working = data.copy()

    working["enrollment"] = pd.to_numeric(working["enrollment"], errors="coerce").fillna(0)

    global_cost_median = working["cost"].median()
    global_grad_median = working["graduation_rate"].median()

    enrollment_series = working["enrollment"]
    max_enrollment = int(enrollment_series.max()) if not enrollment_series.empty else 0
    slider_min = 0
    slider_max = max(0, max_enrollment)

    st.sidebar.header("Chart Explorer")
    st.sidebar.write("Cost vs Graduation Rate")

    min_enrollment = st.sidebar.slider(
        "Minimum undergraduate enrollment",
        slider_min,
        slider_max,
        value=1000 if slider_max >= 1000 else slider_max,
        step=100 if slider_max - slider_min >= 100 else 10 if slider_max - slider_min >= 10 else 1,
        help="Filter institutions by undergraduate degree-seeking enrollment (ENR_UGD).",
    )

    sectors = sorted(working["sector"].dropna().unique())
    default_sectors = [
        "Public",
        "Private, not-for-profit",
        "Private, for-profit",
    ]
    default_selection = [sector for sector in default_sectors if sector in sectors] or sectors

    selected_sectors = st.sidebar.multiselect(
        "Sectors",
        options=sectors,
        default=default_selection,
    )

    states = sorted(working["state"].dropna().unique())
    state_all_label = "All States"
    state_options = [state_all_label] + states
    selected_states = st.sidebar.multiselect(
        "States",
        options=state_options,
        default=[state_all_label],
        help="Pick one or more states; choose 'All States' to include every state.",
    )

    if state_all_label in selected_states or not selected_states:
        active_states = states
    else:
        active_states = [state for state in selected_states if state in states]

    filtered = working.loc[
        (working["enrollment"] >= min_enrollment)
        & (working["sector"].isin(selected_sectors))
        & (working["state"].isin(active_states))
    ]

    render_cost_vs_grad_scatter(
        filtered,
        min_enrollment=min_enrollment,
        global_cost_median=global_cost_median,
        global_grad_median=global_grad_median,
    )
