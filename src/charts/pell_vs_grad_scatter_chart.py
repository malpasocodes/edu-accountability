"""Scatter chart for Pell grant dollars versus graduation rate."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

from src.ui.renderers import render_altair_chart

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


def render_pell_vs_grad_scatter(df: pd.DataFrame, *, title: str) -> None:
    """Render a scatter plot of Pell dollars (billions) versus graduation rate."""

    if df.empty:
        st.warning("No Pell/graduation overlap found to chart.")
        return

    working = df.copy()
    numeric_columns = {
        "GraduationRate": "graduation_rate",
        "PellDollarsBillions": "pell_dollars_billions",
    }
    for column, alias in numeric_columns.items():
        if column in working.columns:
            working[alias] = pd.to_numeric(working[column], errors="coerce")
        else:
            working[alias] = pd.NA

    working["Sector"] = working.get("Sector", "Unknown").fillna("Unknown").replace("", "Unknown")
    working["Institution"] = working.get("Institution", "")
    working["YearsCovered"] = working.get("YearsCovered", "")

    filtered = working.dropna(subset=["graduation_rate", "pell_dollars_billions"])
    if filtered.empty:
        st.warning("No valid numeric data available for the scatter chart.")
        return

    top_filtered = filtered.sort_values("pell_dollars_billions", ascending=False).head(50)

    scatter = (
        alt.Chart(top_filtered)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "graduation_rate:Q",
                title="Graduation rate",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "pell_dollars_billions:Q",
                title="Pell dollars (billions)",
            ),
            color=alt.Color("Sector:N", title="Sector", scale=SECTOR_COLOR_SCALE),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("graduation_rate:Q", title="Graduation rate", format=".1f"),
                alt.Tooltip("pell_dollars_billions:Q", title="Pell dollars (billions)", format=".2f"),
                alt.Tooltip("Sector:N", title="Sector"),
                alt.Tooltip("YearsCovered:N", title="Years"),
            ],
            size=alt.Size("pell_dollars_billions:Q", title="Pell dollars (billions)", scale=alt.Scale(range=[30, 400])),
        )
        .properties(height=520)
    )

    st.subheader(title)
    st.caption(
        "Each point represents an institution with available Pell grant totals (billions) and "
        "graduation rate data; bubble size scales with Pell dollars. Showing top 50 institutions "
        "by Pell dollars."
    )
    render_altair_chart(scatter, width="stretch")
