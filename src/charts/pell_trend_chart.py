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

    # Add UnitID if not present for grouping
    if "UnitID" not in filtered.columns:
        # Create a unique identifier for each institution
        institution_to_id = {inst: idx for idx, inst in enumerate(filtered["Institution"].unique())}
        filtered["UnitID"] = filtered["Institution"].map(institution_to_id)

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

    # Calculate year-over-year changes for dot coloring
    filtered = filtered.sort_values(["UnitID", "Year"])
    filtered["PrevYearPellDollars"] = filtered.groupby("UnitID")["PellDollarsBillions"].shift(1)
    filtered["YoYChange"] = filtered["PellDollarsBillions"] - filtered["PrevYearPellDollars"]
    filtered["YoYChangePercent"] = (
        (filtered["PellDollarsBillions"] - filtered["PrevYearPellDollars"]) / filtered["PrevYearPellDollars"] * 100
    ).round(1)

    # Determine change direction for dot coloring
    filtered["ChangeDirection"] = pd.cut(filtered["YoYChange"], bins=[-float('inf'), -0.001, 0.001, float('inf')],
                                       labels=["Decrease", "Same", "Increase"], include_lowest=True)
    filtered["ChangeDirection"] = filtered["ChangeDirection"].fillna("Same").astype(str)

    # For first year of each institution, mark as "Same" since no previous year
    first_year_mask = filtered["PrevYearPellDollars"].isna()
    filtered.loc[first_year_mask, "ChangeDirection"] = "Same"
    filtered.loc[first_year_mask, "YoYChangePercent"] = 0.0

    # Create institution-based color scale
    institutions = filtered["Institution"].unique()
    institution_color_scale = alt.Scale(
        domain=list(institutions),
        scheme="category20"
    )

    # Create change direction color scale for dots
    change_color_scale = alt.Scale(
        domain=["Increase", "Same", "Decrease"],
        range=["#28a745", "#6c757d", "#dc3545"]  # Green, Gray, Red
    )

    # Line layer with dotted lines colored by institution
    lines = alt.Chart(filtered).mark_line(
        strokeDash=[3, 3],  # Dotted line pattern
        point=False
    ).encode(
        x=alt.X("Year:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y("PellDollarsBillions:Q", title="Pell dollars (billions)"),
        color=alt.Color(
            "Institution:N",
            title="Institution",
            scale=institution_color_scale
        ),
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

    # Point layer with year-over-year change coloring
    points = alt.Chart(filtered).mark_circle(size=80).encode(
        x=alt.X("Year:Q"),
        y=alt.Y("PellDollarsBillions:Q"),
        color=alt.Color(
            "ChangeDirection:N",
            title="Year-over-Year Change",
            scale=change_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "PellDollarsBillions:Q",
                title="Pell dollars (billions)",
                format=".2f",
            ),
            alt.Tooltip("Sector:N", title="Sector"),
            alt.Tooltip("YoYChangePercent:Q", title="Year-over-year change (%)", format=".1f"),
            alt.Tooltip("ChangeDirection:N", title="Change direction"),
        ],
    )

    # Combine layers
    chart = (lines + points).resolve_scale(
        color="independent"
    ).properties(height=520)


    st.subheader(title)
    if anchor_year is None:
        caption = (
            "Trends for the top Pell grant recipients in this segment, showing annual dollar totals. "
            "Dotted lines colored by institution; dots colored by year-over-year change (green=increase/same, red=decrease)."
        )
    else:
        caption = (
            f"Top 10 institutions by Pell dollars in {anchor_year}, with annual totals over time. "
            "Dotted lines colored by institution; dots colored by year-over-year change (green=increase/same, red=decrease)."
        )
    st.caption(caption)
    render_altair_chart(chart)
