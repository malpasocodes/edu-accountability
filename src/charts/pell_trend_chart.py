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

    anchor_year = None
    if "AnchorYear" in filtered.columns:
        anchor_candidates = (
            filtered["AnchorYear"].dropna().astype(float).astype(int).unique()
        )
        if anchor_candidates.size:
            anchor_year = int(anchor_candidates[0])

    if anchor_year is not None:
        anchor_subset = filtered[filtered["Year"] == anchor_year]
        top_institutions = (
            anchor_subset.sort_values("PellDollarsBillions", ascending=False)
            .drop_duplicates(subset=["Institution"], keep="first")
            .head(10)["Institution"]
            .tolist()
        )
        filtered = filtered[filtered["Institution"].isin(top_institutions)]
        if filtered.empty:
            st.warning(
                "Unable to plot Pell trends because no institutions had positive Pell dollars in the anchor year."
            )
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
    if anchor_year is None:
        caption = (
            "Trends for the top Pell grant recipients in this segment, showing annual dollar totals; "
            "colors indicate sector."
        )
    else:
        caption = (
            f"Top 10 institutions by Pell dollars in {anchor_year}, with annual totals over time; "
            "colors indicate sector."
        )
    st.caption(caption)
    render_altair_chart(chart, width="stretch")
