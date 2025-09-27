"""Line chart utilities for total enrollment trends over time."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

import pandas as pd
import streamlit as st
import altair as alt

from src.ui.renderers import render_altair_chart

# Pattern to match total enrollment columns
TOTAL_ENROLL_PATTERN = re.compile(r"^TOTAL_ENROLL_(\d{4})$", re.IGNORECASE)

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


def _identify_total_enrollment_columns(columns: Iterable[str]) -> List[tuple[int, str]]:
    """Identify total enrollment columns and extract years."""
    discovered: List[tuple[int, str]] = []
    for column in columns:
        normalized = column.strip()
        match = TOTAL_ENROLL_PATTERN.match(normalized)
        if match:
            year = int(match.group(1))
            discovered.append((year, column))
    return sorted(discovered)


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    """Normalize UnitID values to consistent format."""
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")


def _prepare_enrollment_trend_dataframe(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    top_n: int = 10,
    anchor_year: int = 2024
) -> pd.DataFrame:
    """Prepare data for enrollment trend chart."""
    if distance_df.empty:
        return pd.DataFrame()

    enrollment_columns = _identify_total_enrollment_columns(distance_df.columns)
    if not enrollment_columns:
        raise ValueError("No total enrollment columns found in distance education dataset.")

    working = distance_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Distance education dataset missing 'UnitID' column required for charting.")

    # Convert enrollment columns to numeric
    enrollment_field_names = [column for _, column in enrollment_columns]
    for column in enrollment_field_names:
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
    for year, col in enrollment_columns:
        if year == anchor_year:
            anchor_col = col
            break

    if anchor_col is None:
        raise ValueError(f"No enrollment data found for anchor year {anchor_year}")

    # Get top N institutions by anchor year enrollment
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
        value_vars=enrollment_field_names,
        var_name="YearLabel",
        value_name="enrollment",
    )

    # Extract year from column name
    long_form["Year"] = (
        long_form["YearLabel"].str.extract(r"TOTAL_ENROLL_(\d{4})")[0].astype(float)
    )
    long_form.dropna(subset=["Year"], inplace=True)
    if long_form.empty:
        return pd.DataFrame()

    long_form["Year"] = long_form["Year"].astype(int)

    # Convert enrollment to numeric and filter valid values
    long_form["enrollment"] = pd.to_numeric(long_form["enrollment"], errors="coerce")
    long_form = long_form.dropna(subset=["enrollment"])
    if long_form.empty:
        return pd.DataFrame()

    # Calculate year-over-year changes for dot coloring
    long_form = long_form.sort_values(["UnitID", "Year"])
    long_form["PrevYearEnrollment"] = long_form.groupby("UnitID")["enrollment"].shift(1)
    long_form["YoYChange"] = long_form["enrollment"] - long_form["PrevYearEnrollment"]
    long_form["YoYChangePercent"] = (
        (long_form["enrollment"] - long_form["PrevYearEnrollment"]) / long_form["PrevYearEnrollment"] * 100
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
    first_year_mask = long_form["PrevYearEnrollment"].isna()
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
        "enrollment",
        "AnchorYear",
        "ChangeDirection",
        "YoYChangePercent",
    ]

    return long_form[final_columns].copy()


def _render_enrollment_data_table(
    prepared: pd.DataFrame,
    top_n: int,
    anchor_year: int
) -> None:
    """Render data table showing enrollment figures for each institution by year."""
    if prepared.empty:
        return

    # Create pivot table from long format data
    pivot_data = prepared.pivot_table(
        index=["Institution", "Sector"],
        columns="Year",
        values="enrollment",
        aggfunc="first"
    ).reset_index()

    # Convert year column names to strings to avoid mixed type warning
    year_columns = [col for col in pivot_data.columns if isinstance(col, int)]
    column_mapping = {col: str(col) for col in year_columns}
    pivot_data = pivot_data.rename(columns=column_mapping)

    # Format enrollment numbers and calculate change
    year_columns = [col for col in pivot_data.columns if col.isdigit()]
    year_columns.sort()

    # Calculate total change from first to last year
    if len(year_columns) >= 2:
        first_year, last_year = year_columns[0], year_columns[-1]
        pivot_data["Total Change"] = (
            (pivot_data[last_year] - pivot_data[first_year]) / pivot_data[first_year] * 100
        ).round(1)

    # Format the display table
    display_data = pivot_data.copy()
    for year in year_columns:
        display_data[year] = display_data[year].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

    if "Total Change" in display_data.columns:
        display_data["Total Change"] = display_data["Total Change"].apply(
            lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
        )

    # Sort by anchor year enrollment (descending)
    anchor_year_str = str(anchor_year)
    if anchor_year_str in pivot_data.columns:
        sort_col_idx = pivot_data.columns.get_loc(anchor_year_str)
        numeric_data = pivot_data.iloc[:, sort_col_idx]
        display_data = display_data.iloc[numeric_data.sort_values(ascending=False).index]

    st.subheader("📊 Enrollment Data")
    st.caption(f"Total enrollment figures for top {top_n} institutions by {anchor_year} enrollment.")
    st.dataframe(display_data, width="stretch", hide_index=True)


def render_distance_enrollment_trend_chart(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    top_n: int = 10,
    anchor_year: int = 2024
) -> None:
    """Render a multi-line trend chart for total enrollment across years."""

    try:
        prepared = _prepare_enrollment_trend_dataframe(
            distance_df,
            metadata_df,
            top_n=top_n,
            anchor_year=anchor_year,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.empty:
        st.warning("No enrollment trend data available to chart.")
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
            "enrollment:Q",
            title="Total Enrollment",
            axis=alt.Axis(
                format=".1s",  # Show as thousands: 50k, 100k
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
                "enrollment:Q",
                title="Total Enrollment",
                format=",",
            ),
            alt.Tooltip("Sector:N", title="Sector"),
        ],
    )

    # Point layer with year-over-year change coloring
    points = alt.Chart(prepared).mark_circle(size=80).encode(
        x=alt.X("Year:Q"),
        y=alt.Y("enrollment:Q"),
        color=alt.Color(
            "ChangeDirection:N",
            title="Year-over-Year Change",
            scale=change_color_scale
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Year:Q", title="Year", format=".0f"),
            alt.Tooltip(
                "enrollment:Q",
                title="Total Enrollment",
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
        f"Top {top_n} institutions by total enrollment in {anchor_year}, with annual enrollment over time. "
        "Dotted lines colored by institution; dots colored by year-over-year change (green=increase/same, red=decrease)."
    )
    st.caption(caption)
    render_altair_chart(chart, width="stretch")

    # Create data table
    _render_enrollment_data_table(prepared, top_n, anchor_year)