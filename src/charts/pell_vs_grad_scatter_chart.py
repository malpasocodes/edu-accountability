"""Scatter chart for Pell grant dollars versus graduation rate."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")


def render_pell_vs_grad_scatter(
    df: pd.DataFrame,
    *,
    title: str,
    metadata_df: pd.DataFrame | None = None,
) -> None:
    """Render a scatter plot of Pell dollars (billions) versus graduation rate."""

    if df.empty:
        st.warning("No Pell/graduation overlap found to chart.")
        return

    working = df.copy()
    numeric_columns = {
        "GraduationRate": "graduation_rate",
        "PellDollarsBillions": "pell_dollars_billions",
        "Enrollment": "enrollment",
    }
    for column, alias in numeric_columns.items():
        if column in working.columns:
            working[alias] = pd.to_numeric(working[column], errors="coerce")
        else:
            working[alias] = pd.NA

    if metadata_df is not None and "UnitID" in working.columns:
        if "UnitID" in metadata_df.columns and "enrollment" in metadata_df.columns:
            metadata = metadata_df.copy()
            metadata["UnitID"] = _normalize_unit_ids(metadata.get("UnitID"))
            metadata["enrollment"] = pd.to_numeric(metadata["enrollment"], errors="coerce")
            working["UnitID"] = _normalize_unit_ids(working.get("UnitID"))
            working = working.merge(
                metadata[["UnitID", "enrollment"]], on="UnitID", how="left"
            )
            if "enrollment_x" in working.columns and "enrollment_y" in working.columns:
                working["enrollment"] = working["enrollment_x"].where(
                    working["enrollment_x"].notna(), working["enrollment_y"]
                )
                working.drop(columns=["enrollment_x", "enrollment_y"], inplace=True)
            elif "enrollment_y" in working.columns:
                working.rename(columns={"enrollment_y": "enrollment"}, inplace=True)

    if "enrollment" in working.columns:
        working["enrollment"] = pd.to_numeric(working["enrollment"], errors="coerce")

    working["Sector"] = working.get("Sector", "Unknown").fillna("Unknown").replace("", "Unknown")
    working["Institution"] = working.get("Institution", "")
    working["YearsCovered"] = working.get("YearsCovered", "")

    filtered = working.dropna(subset=["graduation_rate", "pell_dollars_billions", "enrollment"])
    filtered = filtered[filtered["enrollment"] > 0]
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
                alt.Tooltip("enrollment:Q", title="Enrollment", format=","),
                alt.Tooltip("Sector:N", title="Sector"),
                alt.Tooltip("YearsCovered:N", title="Years"),
            ],
            size=alt.Size(
                "enrollment:Q",
                title="Enrollment",
                scale=alt.Scale(range=[30, 600]),
            ),
        )
        .properties(height=520)
    )

    st.subheader(title)
    st.caption(
        "Each point represents an institution with available Pell grant totals (billions) and "
        "graduation rate data; bubble size scales with enrollment. Showing top 50 institutions "
        "by Pell dollars."
    )
    render_altair_chart(scatter)

    display_columns = [
        "Institution",
        "Sector",
        "YearsCovered",
        "pell_dollars_billions",
        "graduation_rate",
        "enrollment",
    ]
    table_df = (
        top_filtered[display_columns]
        .copy()
        .rename(
            columns={
                "YearsCovered": "Years",
                "pell_dollars_billions": "Pell dollars (billions)",
                "graduation_rate": "Graduation rate (%)",
                "enrollment": "Enrollment",
            }
        )
        .sort_values("Pell dollars (billions)", ascending=False)
    )
    table_df["Pell dollars (billions)"] = table_df["Pell dollars (billions)"].round(2)
    table_df["Graduation rate (%)"] = table_df["Graduation rate (%)"].round(1)
    table_df["Enrollment"] = table_df["Enrollment"].round().astype(int)

    st.markdown("**Institutions (top 50 by Pell dollars)**")
    render_dataframe(table_df, width="stretch")
