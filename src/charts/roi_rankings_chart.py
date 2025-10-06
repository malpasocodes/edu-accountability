"""ROI Rankings chart - Top/Bottom 25 institutions by ROI (California institutions only)."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private nonprofit", "Private for-profit"],
    range=["#2ca02c", "#9467bd", "#1f77b4"],
)

# Color scale for ROI years (green = fast ROI, red = slow ROI)
ROI_COLOR_SCALE = alt.Scale(
    domain=[0, 1, 2, 5, 10],
    range=["#2ca02c", "#98df8a", "#ffdd71", "#ff9896", "#d62728"],
    type="threshold",
)


def render_roi_rankings_chart(
    df: pd.DataFrame,
    *,
    baseline: str = "statewide",
    view: str = "top",
    n: int = 25,
    title: str = "Top 25 ROI Rankings",
) -> None:
    """
    Render horizontal bar chart of top or bottom N institutions by ROI.

    Args:
        df: DataFrame with ROI metrics (from load_roi_metrics())
        baseline: Either "statewide" or "regional" for ROI calculation
        view: Either "top" (best ROI, lowest years) or "bottom" (worst ROI, highest years)
        n: Number of institutions to show
        title: Chart title
    """
    if df.empty:
        st.warning("No ROI data available. Run `python src/data/build_roi_metrics.py` to generate.")
        return

    working = df.copy()

    # Select appropriate ROI column based on baseline
    roi_col = f"roi_{baseline}_years"
    roi_months_col = f"roi_{baseline}_months"
    rank_col = f"rank_{baseline}"

    # Filter out invalid ROI (999 = negative premium flag)
    working = working[working[roi_col] < 999].copy()

    if working.empty:
        st.warning("No valid ROI data available for selected baseline.")
        return

    # Prepare data
    working["roi_years"] = pd.to_numeric(working[roi_col], errors="coerce")
    working["roi_months"] = pd.to_numeric(working[roi_months_col], errors="coerce")
    working["rank"] = pd.to_numeric(working[rank_col], errors="coerce")
    working["cost"] = pd.to_numeric(working["total_net_price"], errors="coerce")
    working["earnings"] = pd.to_numeric(working["median_earnings_10yr"], errors="coerce")
    working["sector_clean"] = working["Sector"].str.strip()

    # Drop rows with missing values
    filtered = working.dropna(subset=["roi_years", "cost", "earnings"])

    if filtered.empty:
        st.warning("No valid data available after filtering.")
        return

    # Select top or bottom N
    if view == "top":
        # Top = best ROI = lowest years
        selected = filtered.nsmallest(n, "roi_years").copy()
        view_label = "Top"
        sort_order = "ascending"
    else:
        # Bottom = worst ROI = highest years
        selected = filtered.nlargest(n, "roi_years").copy()
        view_label = "Bottom"
        sort_order = "descending"

    # Create horizontal bar chart
    chart = (
        alt.Chart(selected)
        .mark_bar()
        .encode(
            x=alt.X(
                "roi_years:Q",
                title="ROI (years to recoup investment)",
                axis=alt.Axis(format=".2f"),
            ),
            y=alt.Y(
                "Institution:N",
                sort=alt.EncodingSortField(field="roi_years", order=sort_order),
                title="Institution",
            ),
            color=alt.Color(
                "roi_years:Q",
                title="ROI (years)",
                scale=ROI_COLOR_SCALE,
                legend=alt.Legend(orient="right"),
            ),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("County:N", title="County"),
                alt.Tooltip("sector_clean:N", title="Sector"),
                alt.Tooltip("roi_years:Q", title="ROI (years)", format=".2f"),
                alt.Tooltip("roi_months:Q", title="ROI (months)", format=".0f"),
                alt.Tooltip("cost:Q", title="Net Price", format="$,.0f"),
                alt.Tooltip("earnings:Q", title="Earnings", format="$,.0f"),
                alt.Tooltip("rank:Q", title="Rank", format=".0f"),
            ],
        )
        .properties(height=max(320, 32 * len(selected)))
    )

    # Render chart
    baseline_label = "Statewide" if baseline == "statewide" else "Regional (County-specific)"
    st.subheader(f"{view_label} {n} by ROI - {baseline_label} Baseline")
    st.caption(
        f"{view_label} {len(selected)} California institutions by ROI (years to recoup investment). "
        f"Lower ROI = faster payback. Color indicates ROI speed (green = fast, red = slow)."
    )
    render_altair_chart(chart, width="stretch")

    # Prepare data table
    display_columns = [
        "rank",
        "Institution",
        "County",
        "sector_clean",
        "roi_years",
        "roi_months",
        "cost",
        "earnings",
    ]

    table_df = (
        selected[display_columns]
        .copy()
        .rename(
            columns={
                "rank": "Rank",
                "sector_clean": "Sector",
                "roi_years": "ROI (years)",
                "roi_months": "ROI (months)",
                "cost": "Net Price ($)",
                "earnings": "Earnings ($)",
            }
        )
        .sort_values("Rank")
    )

    table_df["Net Price ($)"] = table_df["Net Price ($)"].apply(lambda x: f"${x:,.0f}")
    table_df["Earnings ($)"] = table_df["Earnings ($)"].apply(lambda x: f"${x:,.0f}")
    table_df["ROI (years)"] = table_df["ROI (years)"].round(2)
    table_df["ROI (months)"] = table_df["ROI (months)"].round(0).astype(int)
    table_df["Rank"] = table_df["Rank"].round(0).astype(int)

    st.markdown(f"**{view_label} {n} Institutions**")
    render_dataframe(table_df, width="stretch")

    # Summary statistics
    st.markdown("### Summary Statistics")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.metric("Mean ROI", f"{selected['roi_years'].mean():.2f} years")
    with summary_cols[1]:
        st.metric("Median ROI", f"{selected['roi_years'].median():.2f} years")
    with summary_cols[2]:
        st.metric("Mean Cost", f"${selected['cost'].mean():,.0f}")
    with summary_cols[3]:
        st.metric("Mean Earnings", f"${selected['earnings'].mean():,.0f}")
