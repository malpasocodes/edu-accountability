"""Line chart utilities for Pell grant trends over time."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

from src.ui.renderers import render_altair_chart

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


def render_pell_trend_chart(df: pd.DataFrame, *, title: str) -> None:
    """Render a multi-line trend chart for Pell dollars across years."""

    if df.empty:
        st.warning("No Pell grant trend data available to chart.")
        return

    working = df.copy()
    working["Year"] = pd.to_numeric(working.get("Year"), errors="coerce")
    working["PellDollarsBillions"] = pd.to_numeric(
        working.get("PellDollarsBillions"), errors="coerce"
    )
    working["Institution"] = working.get("Institution", "").astype(str)
    working["Sector"] = (
        working.get("Sector", "Unknown").fillna("Unknown").replace("", "Unknown")
    )

    filtered = working.dropna(subset=["Year", "PellDollarsBillions"])
    if filtered.empty:
        st.warning("Trend data contains no numeric values to plot.")
        return

    chart = (
        alt.Chart(filtered)
        .mark_line(point=True)
        .encode(
            x=alt.X("Year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y("PellDollarsBillions:Q", title="Pell dollars (billions)"),
            color=alt.Color("Sector:N", title="Sector", scale=SECTOR_COLOR_SCALE),
            detail=alt.Detail("Institution:N"),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("Year:Q", title="Year", format=".0f"),
                alt.Tooltip(
                    "PellDollarsBillions:Q",
                    title="Pell dollars (billions)",
                    format=".2f",
                ),
                alt.Tooltip("Sector:N", title="Sector"),
            ],
        )
        .properties(height=520)
    )

    st.subheader(title)
    st.caption(
        "Trends for the top 25 Pell grant recipients in this segment, showing annual dollar totals; colors indicate sector."
    )
    render_altair_chart(chart, width="stretch")
