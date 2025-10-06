"""ROI Distribution by Sector chart (California institutions only)."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private nonprofit", "Private for-profit"],
    range=["#2ca02c", "#9467bd", "#1f77b4"],
)


def render_roi_distribution_chart(
    df: pd.DataFrame,
    *,
    baseline: str = "statewide",
    title: str = "ROI Distribution by Sector",
) -> None:
    """
    Render box plot showing ROI distribution across sectors.

    Args:
        df: DataFrame with ROI metrics (from load_roi_metrics())
        baseline: Either "statewide" or "regional" for ROI calculation
        title: Chart title
    """
    if df.empty:
        st.warning("No ROI data available. Run `python src/data/build_roi_metrics.py` to generate.")
        return

    working = df.copy()

    # Select appropriate ROI column based on baseline
    roi_col = f"roi_{baseline}_years"
    roi_months_col = f"roi_{baseline}_months"

    # Filter out invalid ROI (999 = negative premium flag)
    working = working[working[roi_col] < 999].copy()

    if working.empty:
        st.warning("No valid ROI data available for selected baseline.")
        return

    # Prepare data
    working["roi_years"] = pd.to_numeric(working[roi_col], errors="coerce")
    working["roi_months"] = pd.to_numeric(working[roi_months_col], errors="coerce")
    working["sector_clean"] = working["Sector"].str.strip()

    # Drop rows with missing values
    filtered = working.dropna(subset=["roi_years", "sector_clean"])

    if filtered.empty:
        st.warning("No valid data available after filtering.")
        return

    # Create box plot
    box_plot = (
        alt.Chart(filtered)
        .mark_boxplot(size=50, extent="min-max")
        .encode(
            x=alt.X(
                "sector_clean:N",
                title="Sector",
                axis=alt.Axis(labelAngle=-45),
            ),
            y=alt.Y(
                "roi_years:Q",
                title="ROI (years to recoup investment)",
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color(
                "sector_clean:N",
                title="Sector",
                scale=SECTOR_COLOR_SCALE,
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("sector_clean:N", title="Sector"),
            ],
        )
        .properties(height=400)
    )

    # Add individual points as overlay (jittered)
    points = (
        alt.Chart(filtered)
        .mark_circle(size=30, opacity=0.3)
        .encode(
            x=alt.X(
                "sector_clean:N",
                axis=alt.Axis(labelAngle=-45),
            ),
            y=alt.Y("roi_years:Q"),
            color=alt.Color(
                "sector_clean:N",
                scale=SECTOR_COLOR_SCALE,
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("County:N", title="County"),
                alt.Tooltip("sector_clean:N", title="Sector"),
                alt.Tooltip("roi_years:Q", title="ROI (years)", format=".2f"),
                alt.Tooltip("roi_months:Q", title="ROI (months)", format=".0f"),
            ],
        )
        .transform_calculate(
            # Add jitter to x-axis
            jitter="random()"
        )
    )

    # Combine box plot and points
    chart = box_plot + points

    # Render chart
    baseline_label = "Statewide" if baseline == "statewide" else "Regional (County-specific)"
    st.subheader(f"{title} - {baseline_label} Baseline")
    st.caption(
        f"Distribution of ROI across sectors for California institutions. "
        f"Box shows median (line), quartiles (box edges), and min/max (whiskers). "
        f"Individual institutions shown as points."
    )
    render_altair_chart(chart, width="stretch")

    # Calculate summary statistics by sector
    st.markdown("### Sector Summary Statistics")

    summary = (
        filtered.groupby("sector_clean")
        .agg(
            count=("Institution", "count"),
            mean_roi=("roi_years", "mean"),
            median_roi=("roi_years", "median"),
            min_roi=("roi_years", "min"),
            max_roi=("roi_years", "max"),
            q25_roi=("roi_years", lambda x: x.quantile(0.25)),
            q75_roi=("roi_years", lambda x: x.quantile(0.75)),
        )
        .reset_index()
    )

    summary.columns = [
        "Sector",
        "Count",
        "Mean ROI (years)",
        "Median ROI (years)",
        "Min ROI (years)",
        "Max ROI (years)",
        "Q25 (years)",
        "Q75 (years)",
    ]

    summary = summary.sort_values("Median ROI (years)")

    # Round numeric columns
    for col in summary.columns:
        if "years" in col.lower():
            summary[col] = summary[col].round(2)

    render_dataframe(summary, width="stretch")

    # Overall statistics
    st.markdown("### Overall Statistics")
    overall_cols = st.columns(4)
    with overall_cols[0]:
        st.metric("All Institutions", len(filtered))
    with overall_cols[1]:
        st.metric("Overall Mean ROI", f"{filtered['roi_years'].mean():.2f} years")
    with overall_cols[2]:
        st.metric("Overall Median ROI", f"{filtered['roi_years'].median():.2f} years")
    with overall_cols[3]:
        st.metric("Overall Range", f"{filtered['roi_years'].min():.2f} - {filtered['roi_years'].max():.2f} years")

    # Detailed institution list by sector
    st.markdown("### All Institutions by Sector")

    # Create detailed table
    detailed_df = (
        filtered[["Institution", "County", "sector_clean", "roi_years", "roi_months"]]
        .copy()
        .rename(
            columns={
                "sector_clean": "Sector",
                "roi_years": "ROI (years)",
                "roi_months": "ROI (months)",
            }
        )
        .sort_values(["Sector", "ROI (years)"])
    )

    detailed_df["ROI (years)"] = detailed_df["ROI (years)"].round(2)
    detailed_df["ROI (months)"] = detailed_df["ROI (months)"].round(0).astype(int)

    render_dataframe(detailed_df, width="stretch")
