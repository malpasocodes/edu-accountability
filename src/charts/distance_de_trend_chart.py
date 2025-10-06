"""Line chart utilities for exclusive distance education enrollment trends over time."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

import pandas as pd
import streamlit as st
import altair as alt

from src.ui.renderers import render_altair_chart

# Pattern to match exclusive distance education enrollment columns
DE_ENROLL_PATTERN = re.compile(r"^DE_ENROLL_(\d{4})$", re.IGNORECASE)

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


def _identify_de_enrollment_columns(columns: Iterable[str]) -> List[tuple[int, str]]:
    """Identify exclusive distance education enrollment columns and extract years."""
    discovered: List[tuple[int, str]] = []
    for column in columns:
        normalized = column.strip()
        match = DE_ENROLL_PATTERN.match(normalized)
        if match:
            year = int(match.group(1))
            discovered.append((year, column))
    return sorted(discovered)


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    """Normalize UnitID values to consistent format."""
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")


def _prepare_de_trend_dataframe(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    top_n: int = 10,
    anchor_year: int = 2024
) -> pd.DataFrame:
    """Prepare data for DE enrollment trend chart."""
    if distance_df.empty:
        return pd.DataFrame()

    de_columns = _identify_de_enrollment_columns(distance_df.columns)
    if not de_columns:
        raise ValueError("No exclusive distance education enrollment columns found in dataset.")

    working = distance_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Distance education dataset missing 'UnitID' column required for charting.")

    # Convert DE enrollment columns to numeric
    de_field_names = [column for _, column in de_columns]
    for column in de_field_names:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working["UnitID"] = _normalize_unit_ids(working.get("UnitID"))

    # Prepare metadata
    metadata = metadata_df.copy()
    required_metadata = {"UnitID", "institution", "sector"}
    missing_metadata = [column for column in required_metadata if column not in metadata.columns]
    if missing_metadata:
        raise ValueError(
            "Cannot merge distance education dataset with metadata. Missing columns: "
            + ", ".join(sorted(missing_metadata))
        )
    metadata["UnitID"] = _normalize_unit_ids(metadata.get("UnitID"))
    metadata["sector"] = metadata["sector"].astype("string")

    # Merge with metadata
    merged = pd.merge(
        working,
        metadata[["UnitID", "institution", "sector"]],
        on="UnitID",
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame()

    # Find anchor year column
    anchor_col = None
    for year, col in de_columns:
        if year == anchor_year:
            anchor_col = col
            break

    if anchor_col is None:
        raise ValueError(f"No DE enrollment data found for anchor year {anchor_year}")

    # Get top N institutions by anchor year DE enrollment
    anchor_data = merged[merged[anchor_col].notna() & (merged[anchor_col] > 0)].copy()
    if anchor_data.empty:
        return pd.DataFrame()

    top_institutions = (
        anchor_data.nlargest(top_n, anchor_col)["institution"].tolist()
    )

    # Filter to top institutions
    filtered = merged[merged["institution"].isin(top_institutions)].copy()
    if filtered.empty:
        return pd.DataFrame()

    # Reshape to long format
    id_vars = ["UnitID", "institution", "sector"]
    long_form = filtered.melt(
        id_vars=id_vars,
        value_vars=de_field_names,
        var_name="YearLabel",
        value_name="de_enrollment",
    )

    # Extract year from column name
    long_form["Year"] = (
        long_form["YearLabel"].str.extract(r"DE_ENROLL_(\d{4})")[0].astype(float)
    )
    long_form.dropna(subset=["Year"], inplace=True)
    if long_form.empty:
        return pd.DataFrame()

    long_form["Year"] = long_form["Year"].astype(int)

    # Convert DE enrollment to numeric and filter valid values (allow 0 for meaningful trend)
    long_form["de_enrollment"] = pd.to_numeric(long_form["de_enrollment"], errors="coerce")
    long_form = long_form.dropna(subset=["de_enrollment"])
    if long_form.empty:
        return pd.DataFrame()

    # Calculate total enrollment per year across top N institutions for percentage calculation
    year_totals = long_form.groupby("Year")["de_enrollment"].sum().reset_index()
    year_totals.rename(columns={"de_enrollment": "year_total_enrollment"}, inplace=True)

    # Merge year totals back to long_form
    long_form = long_form.merge(year_totals, on="Year", how="left")

    # Calculate percentage of total for each institution-year
    long_form["de_percentage"] = (
        (long_form["de_enrollment"] / long_form["year_total_enrollment"] * 100)
        .fillna(0)
        .round(2)
    )

    # Calculate year-over-year changes for dot coloring
    long_form = long_form.sort_values(["UnitID", "Year"])
    long_form["PrevYearDEEnrollment"] = long_form.groupby("UnitID")["de_enrollment"].shift(1)
    long_form["YoYChange"] = long_form["de_enrollment"] - long_form["PrevYearDEEnrollment"]

    # Handle percentage calculation - avoid division by zero
    with pd.option_context('mode.chained_assignment', None):
        long_form["YoYChangePercent"] = 0.0  # Default value
        mask = long_form["PrevYearDEEnrollment"] > 0
        long_form.loc[mask, "YoYChangePercent"] = (
            (long_form.loc[mask, "de_enrollment"] - long_form.loc[mask, "PrevYearDEEnrollment"]) /
            long_form.loc[mask, "PrevYearDEEnrollment"] * 100
        ).round(1)

    # Determine change direction for dot coloring
    long_form["ChangeDirection"] = pd.cut(
        long_form["YoYChange"],
        bins=[-float('inf'), -0.1, 0.1, float('inf')],
        labels=["Decrease", "Same", "Increase"],
        include_lowest=True
    )
    long_form["ChangeDirection"] = long_form["ChangeDirection"].fillna("Same").astype(str)

    # For first year of each institution, mark as "Same" since no previous year
    first_year_mask = long_form["PrevYearDEEnrollment"].isna()
    long_form.loc[first_year_mask, "ChangeDirection"] = "Same"
    long_form.loc[first_year_mask, "YoYChangePercent"] = 0.0

    # Prepare final columns
    long_form["Institution"] = long_form["institution"].astype(str)
    long_form["Sector"] = (
        long_form["sector"].fillna("Unknown").replace("", "Unknown")
    )
    long_form["AnchorYear"] = anchor_year

    # Clean up columns
    final_columns = [
        "UnitID",
        "Institution",
        "Sector",
        "Year",
        "de_enrollment",
        "de_percentage",
        "year_total_enrollment",
        "AnchorYear",
        "ChangeDirection",
        "YoYChangePercent",
    ]

    return long_form[final_columns].copy()


def _render_de_data_table(
    prepared: pd.DataFrame,
    top_n: int,
    anchor_year: int
) -> None:
    """Render data table showing exclusive distance education enrollment figures and percentages for each institution by year."""
    if prepared.empty:
        return

    # Create pivot tables from long format data - one for enrollment, one for percentage
    pivot_enrollment = prepared.pivot_table(
        index=["Institution", "Sector"],
        columns="Year",
        values="de_enrollment",
        aggfunc="first"
    ).reset_index()

    pivot_percentage = prepared.pivot_table(
        index=["Institution", "Sector"],
        columns="Year",
        values="de_percentage",
        aggfunc="first"
    ).reset_index()

    # Convert year column names to strings to avoid mixed type warning
    year_columns_enroll = [col for col in pivot_enrollment.columns if isinstance(col, int)]
    column_mapping_enroll = {col: str(col) for col in year_columns_enroll}
    pivot_enrollment = pivot_enrollment.rename(columns=column_mapping_enroll)

    year_columns_pct = [col for col in pivot_percentage.columns if isinstance(col, int)]
    column_mapping_pct = {col: f"{col} %" for col in year_columns_pct}
    pivot_percentage = pivot_percentage.rename(columns=column_mapping_pct)

    # Merge enrollment and percentage data
    pivot_data = pivot_enrollment.copy()
    for col in pivot_percentage.columns:
        if col not in ["Institution", "Sector"]:
            pivot_data[col] = pivot_percentage[col]

    # Format DE enrollment numbers and calculate change
    year_columns = [col for col in pivot_data.columns if col.isdigit()]
    year_columns.sort()

    # Calculate total change from first to last year
    if len(year_columns) >= 2:
        first_year, last_year = year_columns[0], year_columns[-1]
        # Handle division by zero for percentage calculation
        total_change = []
        for _, row in pivot_data.iterrows():
            first_val = row[first_year]
            last_val = row[last_year]
            if pd.notna(first_val) and pd.notna(last_val) and first_val > 0:
                change_pct = ((last_val - first_val) / first_val * 100)
                total_change.append(round(change_pct, 1))
            else:
                total_change.append(None)
        pivot_data["Total Change"] = total_change

    # Format the display table
    display_data = pivot_data.copy()

    # Format enrollment columns
    for year in year_columns:
        display_data[year] = display_data[year].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

    # Format percentage columns
    pct_columns = [col for col in display_data.columns if col.endswith(" %")]
    for col in pct_columns:
        display_data[col] = display_data[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")

    if "Total Change" in display_data.columns:
        display_data["Total Change"] = display_data["Total Change"].apply(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
        )

    # Sort by anchor year DE enrollment (descending)
    anchor_year_str = str(anchor_year)
    if anchor_year_str in pivot_data.columns:
        sort_col_idx = pivot_data.columns.get_loc(anchor_year_str)
        numeric_data = pivot_data.iloc[:, sort_col_idx]
        display_data = display_data.iloc[numeric_data.sort_values(ascending=False).index]

    st.subheader("📊 Exclusive Distance Education Enrollment Data")
    st.caption(
        f"Exclusive distance education enrollment figures and percentages for top {top_n} institutions by {anchor_year} DE enrollment. "
        f"Percentage columns (%) show each institution's share of total enrollment among the top {top_n} for that year."
    )
    st.dataframe(display_data, width="stretch", hide_index=True)


def render_distance_de_trend_chart(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    top_n: int = 10,
    anchor_year: int = 2024
) -> None:
    """Render a multi-line trend chart for exclusive distance education enrollment across years."""

    try:
        prepared = _prepare_de_trend_dataframe(
            distance_df,
            metadata_df,
            top_n=top_n,
            anchor_year=anchor_year,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.empty:
        st.warning("No exclusive distance education enrollment trend data available to chart.")
        return

    # Create institution-based color scale
    institutions = prepared["Institution"].unique()
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
    lines = alt.Chart(prepared).mark_line(
        strokeDash=[3, 3],  # Dotted line pattern
        point=False
    ).encode(
        x=alt.X(
            "Year:Q",
            title="Year",
            axis=alt.Axis(
                format="d",
                labelFontSize=14,
                titleFontSize=16,
                titleFontWeight="bold"
            )
        ),
        y=alt.Y(
            "de_enrollment:Q",
            title="Exclusive Distance Education Enrollment",
            axis=alt.Axis(
                format=".1s",  # Show as thousands: 5k, 10k
                labelFontSize=14,
                titleFontSize=16,
                titleFontWeight="bold"
            ),
        ),
        color=alt.Color(
            "Institution:N",
            title="Institution",
            scale=institution_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "de_enrollment:Q",
                title="Exclusive DE Enrollment",
                format=",",
            ),
            alt.Tooltip("Sector:N", title="Sector"),
        ],
    )

    # Point layer with year-over-year change coloring
    points = alt.Chart(prepared).mark_circle(size=80).encode(
        x=alt.X("Year:Q"),
        y=alt.Y("de_enrollment:Q"),
        color=alt.Color(
            "ChangeDirection:N",
            title="Year-over-Year Change",
            scale=change_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "de_enrollment:Q",
                title="Exclusive DE Enrollment",
                format=",",
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
    caption = (
        f"Top {top_n} institutions by exclusive distance education enrollment in {anchor_year}, showing annual exclusive DE enrollment trends over time (2020-2024). "
        "Dotted lines colored by institution; dots colored by year-over-year change (green=increase, gray=same, red=decrease)."
    )
    st.caption(caption)
    render_altair_chart(chart, width="stretch")

    # Percentage chart - showing each institution's share of total enrollment among top N
    st.markdown("")  # Spacing
    st.subheader("Percentage of Total Enrollment (Among Top 10 Institutions)")

    # Line layer with dotted lines colored by institution for percentage
    pct_lines = alt.Chart(prepared).mark_line(
        strokeDash=[3, 3],  # Dotted line pattern
        point=False
    ).encode(
        x=alt.X(
            "Year:Q",
            title="Year",
            axis=alt.Axis(
                format="d",
                labelFontSize=14,
                titleFontSize=16,
                titleFontWeight="bold"
            )
        ),
        y=alt.Y(
            "de_percentage:Q",
            title="Percentage of Total (%)",
            scale=alt.Scale(domain=[0, 25]),
            axis=alt.Axis(
                format=".1f",
                labelFontSize=14,
                titleFontSize=16,
                titleFontWeight="bold"
            ),
        ),
        color=alt.Color(
            "Institution:N",
            title="Institution",
            scale=institution_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip("de_percentage:Q", title="Percentage of Total", format=".2f"),
            alt.Tooltip("de_enrollment:Q", title="DE Enrollment", format=","),
            alt.Tooltip("year_total_enrollment:Q", title="Total (Top 10)", format=","),
            alt.Tooltip("Sector:N", title="Sector"),
        ],
    )

    # Point layer for percentage chart
    pct_points = alt.Chart(prepared).mark_circle(size=80).encode(
        x=alt.X("Year:Q"),
        y=alt.Y("de_percentage:Q"),
        color=alt.Color(
            "ChangeDirection:N",
            title="Year-over-Year Change",
            scale=change_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip("de_percentage:Q", title="Percentage of Total", format=".2f"),
            alt.Tooltip("de_enrollment:Q", title="DE Enrollment", format=","),
            alt.Tooltip("year_total_enrollment:Q", title="Total (Top 10)", format=","),
            alt.Tooltip("Sector:N", title="Sector"),
        ],
    )

    # Combine percentage chart layers
    pct_chart = (pct_lines + pct_points).resolve_scale(
        color="independent"
    ).properties(height=520)

    pct_caption = (
        f"Each institution's share of total exclusive DE enrollment among the top {top_n} institutions (2020-2024). "
        f"Percentages are calculated as: (institution enrollment / sum of top {top_n} enrollment) × 100. "
        "Dotted lines colored by institution; dots colored by year-over-year enrollment change."
    )
    st.caption(pct_caption)
    render_altair_chart(pct_chart, width="stretch")

    # Create data table
    _render_de_data_table(prepared, top_n, anchor_year)