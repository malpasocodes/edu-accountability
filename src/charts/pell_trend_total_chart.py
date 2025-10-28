"""Line chart for aggregate total Pell grant dollars across time."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.charts.pell_top_dollars_chart import (
    _identify_year_columns,
    _normalize_unit_ids,
)
from src.ui.renderers import render_altair_chart


def _prepare_pell_trend_total_dataframe(
    pell_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    sector: str,
) -> pd.DataFrame:
    """
    Prepare aggregated Pell trend data summing across all institutions per year.

    Parameters
    ----------
    pell_df : pd.DataFrame
        Pell grant dataset with year columns (YR2008-YR2022)
    metadata_df : pd.DataFrame
        Metadata with UnitID, institution, sector columns
    sector : str
        Sector to filter ("four_year" or "two_year")

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Year, TotalPellDollars, TotalPellDollarsBillions,
        YoYChangePercent, ChangeDirection
    """
    if pell_df.empty:
        return pd.DataFrame()

    year_info = _identify_year_columns(pell_df.columns)
    if not year_info:
        raise ValueError("No year columns found in Pell dataset (expected headers like 'YR2022').")

    working = pell_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Pell dataset missing 'UnitID' column required for trend charting.")

    year_columns = [column for _, column in year_info]
    for column in year_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    working["UnitID"] = _normalize_unit_ids(working.get("UnitID"))

    required_metadata = {"UnitID", "sector"}
    missing_metadata = [column for column in required_metadata if column not in metadata_df.columns]
    if missing_metadata:
        raise ValueError(
            "Cannot prepare Pell trend total dataset. Missing metadata columns: "
            + ", ".join(sorted(missing_metadata))
        )

    metadata = metadata_df.copy()
    metadata["UnitID"] = _normalize_unit_ids(metadata.get("UnitID"))
    metadata["sector"] = metadata["sector"].astype("string")

    # Merge to get sector information
    merged = pd.merge(
        working,
        metadata[["UnitID", "sector"]],
        on="UnitID",
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame()

    # Convert to long format
    long_form = merged.melt(
        id_vars=["UnitID", "sector"],
        value_vars=year_columns,
        var_name="YearLabel",
        value_name="pell_dollars",
    )

    long_form["pell_dollars"] = pd.to_numeric(long_form["pell_dollars"], errors="coerce")
    long_form.dropna(subset=["pell_dollars"], inplace=True)
    if long_form.empty:
        return pd.DataFrame()

    long_form["Year"] = (
        long_form["YearLabel"].str.extract(r"(\d{4})").astype(float)
    )
    long_form.dropna(subset=["Year"], inplace=True)
    if long_form.empty:
        return pd.DataFrame()

    long_form["Year"] = long_form["Year"].astype(int)

    # Aggregate by year (sum across all institutions)
    aggregated = (
        long_form.groupby("Year", as_index=False)["pell_dollars"]
        .sum()
        .sort_values("Year")
    )

    if aggregated.empty:
        return pd.DataFrame()

    # Convert to billions
    aggregated["TotalPellDollarsBillions"] = aggregated["pell_dollars"] / 1_000_000_000

    # Calculate year-over-year changes
    aggregated["YoYChangePercent"] = (
        aggregated["pell_dollars"].pct_change() * 100
    )

    # Categorize change direction
    def categorize_change(change_pct):
        if pd.isna(change_pct):
            return "Same"
        elif change_pct > 0.5:  # More than 0.5% increase
            return "Increase"
        elif change_pct < -0.5:  # More than 0.5% decrease
            return "Decrease"
        else:
            return "Same"

    aggregated["ChangeDirection"] = aggregated["YoYChangePercent"].apply(categorize_change)

    # Select final columns
    columns = [
        "Year",
        "TotalPellDollarsBillions",
        "YoYChangePercent",
        "ChangeDirection",
    ]
    return aggregated.loc[:, columns]


def _render_pell_trend_data_table(prepared: pd.DataFrame, sector: str) -> None:
    """
    Render data table showing Pell grant totals by year with cumulative totals.

    Parameters
    ----------
    prepared : pd.DataFrame
        Prepared dataframe with Year, TotalPellDollarsBillions, YoYChangePercent columns
    sector : str
        Sector identifier ("four_year" or "two_year")
    """
    if prepared.empty:
        return

    # Prepare display data
    display_data = prepared.copy()

    # Calculate raw dollars from billions
    display_data["TotalPellDollars"] = display_data["TotalPellDollarsBillions"] * 1_000_000_000

    # Calculate cumulative total
    display_data["CumulativeTotalDollars"] = display_data["TotalPellDollars"].cumsum()

    # Format columns for display
    display_data["Year"] = display_data["Year"].astype(str)
    display_data["Total Pell Dollars"] = display_data["TotalPellDollars"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
    )
    display_data["Total (Billions)"] = display_data["TotalPellDollarsBillions"].apply(
        lambda x: f"${x:,.2f}B" if pd.notna(x) else "N/A"
    )
    display_data["Cumulative Total"] = display_data["CumulativeTotalDollars"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
    )
    display_data["Year-over-Year Change"] = display_data["YoYChangePercent"].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
    )

    # Select display columns
    final_columns = [
        "Year",
        "Total Pell Dollars",
        "Total (Billions)",
        "Cumulative Total",
        "Year-over-Year Change"
    ]

    # Render table
    sector_label = "4-year" if sector == "four_year" else "2-year"
    st.subheader("📊 Pell Grant Trend Data")
    st.caption(
        f"Annual Pell grant dollar totals for {sector_label} institutions (2008-2022), "
        "with cumulative totals and year-over-year percentage changes."
    )
    st.dataframe(display_data[final_columns], width="stretch", hide_index=True)


def render_pell_trend_total_chart(
    pell_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    sector: str,
) -> None:
    """
    Render a line chart showing total Pell grant dollars across all institutions per year.

    Parameters
    ----------
    pell_df : pd.DataFrame
        Pell grant dataset with year columns
    metadata_df : pd.DataFrame
        Metadata for filtering to sector
    title : str
        Chart title
    sector : str
        Sector to filter ("four_year" or "two_year")
    """
    try:
        prepared = _prepare_pell_trend_total_dataframe(
            pell_df,
            metadata_df,
            sector=sector,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.empty:
        st.warning("No Pell grant trend data available to chart.")
        return

    # Create change direction color scale for dots
    change_color_scale = alt.Scale(
        domain=["Increase", "Same", "Decrease"],
        range=["#28a745", "#6c757d", "#dc3545"]  # Green, Gray, Red
    )

    # Line layer with dotted line
    lines = alt.Chart(prepared).mark_line(
        strokeDash=[3, 3],  # Dotted line pattern
        point=False,
        color="#9467bd",  # Purple color for Pell grants
        strokeWidth=2
    ).encode(
        x=alt.X("Year:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y(
            "TotalPellDollarsBillions:Q",
            title="Total Pell grant dollars (billions)",
        ),
        tooltip=[
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "TotalPellDollarsBillions:Q",
                title="Total Pell dollars (billions)",
                format=".2f",
            ),
        ],
    )

    # Point layer with year-over-year change coloring
    points = alt.Chart(prepared).mark_circle(size=80).encode(
        x=alt.X("Year:Q"),
        y=alt.Y("TotalPellDollarsBillions:Q"),
        color=alt.Color(
            "ChangeDirection:N",
            title="Year-over-Year Change",
            scale=change_color_scale
        ),
        tooltip=[
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "TotalPellDollarsBillions:Q",
                title="Total Pell dollars (billions)",
                format=".2f",
            ),
            alt.Tooltip("YoYChangePercent:Q", title="Year-over-year change (%)", format=".1f"),
            alt.Tooltip("ChangeDirection:N", title="Change direction"),
        ],
    )

    # Combine layers
    chart = (lines + points).resolve_scale(
        color="independent"
    ).properties(height=520)

    st.subheader(title)

    sector_label = "4-year" if sector == "four_year" else "2-year"
    caption = (
        f"Total Pell grant dollars summed across all {sector_label} institutions per year (2008-2022). "
        "Dotted line shows aggregate trend; dots colored by year-over-year change (green=increase, gray=same, red=decrease)."
    )
    st.caption(caption)
    render_altair_chart(chart)

    # Add spacing before table
    st.markdown("")

    # Render data table
    _render_pell_trend_data_table(prepared, sector)
