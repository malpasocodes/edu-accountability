"""Pell graduation rate scatter chart implementation."""

from __future__ import annotations

from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe


SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"]
)


def render_pell_grad_rate_scatter(
    df: pd.DataFrame,
    title: str = "Pell Graduation Rate vs Total Pell Dollars",
    metadata_df: Optional[pd.DataFrame] = None,
) -> None:
    """
    Render a scatter plot of Pell graduation rate vs total Pell dollars.

    Args:
        df: DataFrame with columns: Institution, PellGraduationRate, PellDollars,
            Enrollment, Sector
        title: Chart title
        metadata_df: Optional metadata DataFrame (for consistency with other charts)
    """
    if df.empty:
        st.warning("No data available for this chart.")
        return

    # Create working copy
    working = df.copy()

    # Convert numeric columns
    numeric_columns = ["PellGraduationRate", "PellDollars", "Enrollment"]
    for col in numeric_columns:
        if col in working.columns:
            working[col] = pd.to_numeric(working[col], errors="coerce")

    # Convert Pell dollars to billions for display
    working["PellDollarsBillions"] = working["PellDollars"] / 1_000_000_000

    # Ensure Sector column exists and handle missing values
    working["Sector"] = working.get("Sector", "Unknown").fillna("Unknown").replace("", "Unknown")
    working["Institution"] = working.get("Institution", "")
    working["State"] = working.get("State", "")

    # Filter for valid numeric data
    filtered = working.dropna(subset=["PellGraduationRate", "PellDollarsBillions", "Enrollment"])
    filtered = filtered[filtered["Enrollment"] > 0]

    if filtered.empty:
        st.warning("No valid numeric data available for the scatter chart.")
        return

    # Sort by Pell dollars - show all institutions
    all_filtered = filtered.sort_values("PellDollarsBillions", ascending=False)

    # Create the scatter plot with Altair
    scatter = (
        alt.Chart(all_filtered)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "PellDollarsBillions:Q",
                title="Total Pell Dollars (Billions)",
                axis=alt.Axis(format="$,.1f"),
            ),
            y=alt.Y(
                "PellGraduationRate:Q",
                title="Pell Student Graduation Rate (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "Sector:N",
                title="Sector",
                scale=SECTOR_COLOR_SCALE
            ),
            size=alt.Size(
                "Enrollment:Q",
                title="Enrollment",
                scale=alt.Scale(range=[30, 600]),
            ),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("PellGraduationRate:Q", title="Pell Graduation Rate (%)", format=".1f"),
                alt.Tooltip("PellDollarsBillions:Q", title="Total Pell Dollars (Billions)", format="$,.2f"),
                alt.Tooltip("Enrollment:Q", title="Enrollment", format=","),
                alt.Tooltip("Sector:N", title="Sector"),
                alt.Tooltip("State:N", title="State"),
            ],
        )
        .properties(height=520)
    )

    # Display the chart with caption
    st.subheader(title)
    st.caption(
        "Each point represents an institution with available Pell graduation rate and "
        "total Pell dollars data; bubble size scales with enrollment. Showing all institutions "
        "with available data."
    )
    render_altair_chart(scatter)

    # Add summary statistics for all institutions
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_grad_rate = all_filtered["PellGraduationRate"].mean()
        st.metric("Avg Pell Graduation Rate", f"{avg_grad_rate:.1f}%")
    with col2:
        total_pell = all_filtered["PellDollars"].sum() / 1_000_000_000
        st.metric("Total Pell Dollars", f"${total_pell:.1f}B")
    with col3:
        num_institutions = len(all_filtered)
        st.metric("Number of Institutions", f"{num_institutions:,}")

    # Create data table - show top 50 for readability
    top_50_for_table = all_filtered.head(50)
    display_columns = [
        "Institution",
        "State",
        "Sector",
        "PellDollarsBillions",
        "PellGraduationRate",
        "Enrollment",
    ]
    table_df = (
        top_50_for_table[display_columns]
        .copy()
        .rename(
            columns={
                "PellDollarsBillions": "Pell Dollars (Billions)",
                "PellGraduationRate": "Pell Graduation Rate (%)",
                "Enrollment": "Enrollment",
            }
        )
        .sort_values("Pell Dollars (Billions)", ascending=False)
    )
    table_df["Pell Dollars (Billions)"] = table_df["Pell Dollars (Billions)"].round(2)
    table_df["Pell Graduation Rate (%)"] = table_df["Pell Graduation Rate (%)"].round(1)
    table_df["Enrollment"] = table_df["Enrollment"].round().astype(int)

    st.markdown("**Top 50 Institutions by Pell Dollars**")
    render_dataframe(table_df, width="stretch")