"""Cost vs Earnings Quadrant chart for ROI analysis (California institutions only)."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

# Color scale for ROI years (green = fast ROI, red = slow ROI)
ROI_COLOR_SCALE = alt.Scale(
    domain=[0, 1, 2, 5, 10],
    range=["#2ca02c", "#98df8a", "#ffdd71", "#ff9896", "#d62728"],
    type="threshold",
)

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private nonprofit", "Private for-profit"],
    range=["#2ca02c", "#9467bd", "#1f77b4"],
)


def render_roi_quadrant_chart(
    df: pd.DataFrame,
    *,
    baseline: str = "statewide",
    title: str = "Cost vs Earnings Quadrant",
) -> None:
    """
    Render a quadrant scatter plot of cost vs earnings with ROI coloring.

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
    working["cost"] = pd.to_numeric(working["total_net_price"], errors="coerce")
    working["earnings"] = pd.to_numeric(working["median_earnings_10yr"], errors="coerce")
    working["roi_years"] = pd.to_numeric(working[roi_col], errors="coerce")
    working["roi_months"] = pd.to_numeric(working[roi_months_col], errors="coerce")
    working["sector_clean"] = working["Sector"].str.strip()

    # Drop rows with missing values
    filtered = working.dropna(subset=["cost", "earnings", "roi_years"])

    if filtered.empty:
        st.warning("No valid data available after filtering.")
        return

    # Calculate quadrant reference lines (medians)
    median_cost = filtered["cost"].median()
    median_earnings = filtered["earnings"].median()

    # Create scatter plot
    scatter = (
        alt.Chart(filtered)
        .mark_circle(opacity=0.75, size=100)
        .encode(
            x=alt.X(
                "cost:Q",
                title="Total Net Price ($)",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(format="$,.0f"),
            ),
            y=alt.Y(
                "earnings:Q",
                title="Median Earnings (10 years after entry, $)",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(format="$,.0f"),
            ),
            color=alt.Color(
                "sector_clean:N",
                title="Sector",
                scale=SECTOR_COLOR_SCALE,
                legend=alt.Legend(orient="right"),
            ),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("County:N", title="County"),
                alt.Tooltip("sector_clean:N", title="Sector"),
                alt.Tooltip("cost:Q", title="Net Price", format="$,.0f"),
                alt.Tooltip("earnings:Q", title="Earnings", format="$,.0f"),
                alt.Tooltip("roi_years:Q", title="ROI (years)", format=".2f"),
                alt.Tooltip("roi_months:Q", title="ROI (months)", format=".0f"),
            ],
        )
        .properties(height=520)
    )

    # Add quadrant reference lines
    vline = (
        alt.Chart(pd.DataFrame({"x": [median_cost]}))
        .mark_rule(strokeDash=[5, 5], color="gray", opacity=0.5)
        .encode(x="x:Q")
    )

    hline = (
        alt.Chart(pd.DataFrame({"y": [median_earnings]}))
        .mark_rule(strokeDash=[5, 5], color="gray", opacity=0.5)
        .encode(y="y:Q")
    )

    # Combine layers
    chart = scatter + vline + hline

    # Render chart
    baseline_label = "Statewide" if baseline == "statewide" else "Regional (County-specific)"
    st.subheader(f"{title} - {baseline_label} Baseline")
    st.caption(
        f"Each point represents a California institution colored by sector. "
        f"Quadrant lines show median cost (${median_cost:,.0f}) and median earnings (${median_earnings:,.0f}). "
        f"**Top-left quadrant** = best value (high earnings, low cost)."
    )
    render_altair_chart(chart, width="stretch")

    # Identify quadrant for each institution
    filtered["quadrant"] = "Other"
    filtered.loc[
        (filtered["earnings"] > median_earnings) & (filtered["cost"] < median_cost),
        "quadrant",
    ] = "High Earnings, Low Cost"
    filtered.loc[
        (filtered["earnings"] > median_earnings) & (filtered["cost"] >= median_cost),
        "quadrant",
    ] = "High Earnings, High Cost"
    filtered.loc[
        (filtered["earnings"] <= median_earnings) & (filtered["cost"] < median_cost),
        "quadrant",
    ] = "Low Earnings, Low Cost"
    filtered.loc[
        (filtered["earnings"] <= median_earnings) & (filtered["cost"] >= median_cost),
        "quadrant",
    ] = "Low Earnings, High Cost"

    # Create quadrant dictionary for tabs
    quadrants = {
        "High Earnings, Low Cost": filtered[filtered["quadrant"] == "High Earnings, Low Cost"].copy(),
        "High Earnings, High Cost": filtered[filtered["quadrant"] == "High Earnings, High Cost"].copy(),
        "Low Earnings, Low Cost": filtered[filtered["quadrant"] == "Low Earnings, Low Cost"].copy(),
        "Low Earnings, High Cost": filtered[filtered["quadrant"] == "Low Earnings, High Cost"].copy(),
    }

    # Add custom CSS for larger tab font
    st.markdown(
        """
        <style>
        div[data-testid="stTabs"] button[role="tab"] div p {
            font-size: 1.25rem !important;
            font-weight: 600;
        }
        div[data-testid="stTabs"] button[role="tab"] div {
            font-size: 1.25rem !important;
        }
        div[data-testid="stTabs"] button[role="tab"] p {
            font-size: 1.25rem !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Create tabs for each quadrant
    tabs = st.tabs(list(quadrants.keys()))
    for tab, (label, quadrant_data) in zip(tabs, quadrants.items()):
        with tab:
            st.write(
                f"{len(quadrant_data):,} institutions"
                if not quadrant_data.empty
                else "No institutions found"
            )
            if not quadrant_data.empty:
                display_cols = [
                    "Institution",
                    "County",
                    "sector_clean",
                    "cost",
                    "earnings",
                    "roi_years",
                    "roi_months",
                ]
                formatted = quadrant_data[display_cols].copy()
                formatted = formatted.rename(
                    columns={
                        "sector_clean": "Sector",
                        "cost": "Net Price ($)",
                        "earnings": "Earnings ($)",
                        "roi_years": "ROI (years)",
                        "roi_months": "ROI (months)",
                    }
                )
                # Sort by ROI (best first) within each quadrant
                formatted = formatted.sort_values("ROI (years)")

                # Format currency columns
                formatted["Net Price ($)"] = formatted["Net Price ($)"].apply(lambda x: f"${x:,.0f}")
                formatted["Earnings ($)"] = formatted["Earnings ($)"].apply(lambda x: f"${x:,.0f}")
                formatted["ROI (years)"] = formatted["ROI (years)"].round(2)
                formatted["ROI (months)"] = formatted["ROI (months)"].round(0).astype(int)

                render_dataframe(formatted, width="stretch")
