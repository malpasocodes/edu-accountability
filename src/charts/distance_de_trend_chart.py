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
    top_n: int = 25,
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
        "AnchorYear",
        "ChangeDirection",
        "YoYChangePercent",
    ]

    return long_form[final_columns].copy()


def render_distance_de_trend_chart(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    top_n: int = 25,
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
        f"Top {top_n} institutions by exclusive distance education enrollment in {anchor_year}, with annual DE enrollment over time. "
        "Dotted lines colored by institution; dots colored by year-over-year change (green=increase/same, red=decrease)."
    )
    st.caption(caption)
    render_altair_chart(chart, width="stretch")