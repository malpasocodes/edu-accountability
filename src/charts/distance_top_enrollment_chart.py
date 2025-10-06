"""Distance education top enrollment chart rendering utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

# Pattern to match total enrollment columns
TOTAL_ENROLL_PATTERN = re.compile(r"^TOTAL_ENROLL_(\d{4})$", re.IGNORECASE)
# Pattern to match exclusive distance education columns
DE_ENROLL_PATTERN = re.compile(r"^DE_ENROLL_(\d{4})$", re.IGNORECASE)
# Pattern to match some distance education columns
SDE_ENROLL_PATTERN = re.compile(r"^SDE_ENROLL_(\d{4})$", re.IGNORECASE)

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


@dataclass(frozen=True)
class DistanceTopEnrollmentResult:
    period_label: Optional[str]
    chart_data: pd.DataFrame


def _identify_enrollment_columns(columns: Iterable[str]) -> tuple[List[tuple[int, str]], List[tuple[int, str]], List[tuple[int, str]]]:
    """Identify total, exclusive DE, and some DE enrollment columns."""
    total_columns: List[tuple[int, str]] = []
    de_columns: List[tuple[int, str]] = []
    sde_columns: List[tuple[int, str]] = []

    for column in columns:
        normalized = column.strip()

        # Check for total enrollment
        total_match = TOTAL_ENROLL_PATTERN.match(normalized)
        if total_match:
            year = int(total_match.group(1))
            total_columns.append((year, column))
            continue

        # Check for exclusive distance education
        de_match = DE_ENROLL_PATTERN.match(normalized)
        if de_match:
            year = int(de_match.group(1))
            de_columns.append((year, column))
            continue

        # Check for some distance education (handle special case for 2024)
        if column == "SDE_ENROLL_TOTAL":
            sde_columns.append((2024, column))
            continue

        sde_match = SDE_ENROLL_PATTERN.match(normalized)
        if sde_match:
            year = int(sde_match.group(1))
            sde_columns.append((year, column))

    return sorted(total_columns), sorted(de_columns), sorted(sde_columns)


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    """Normalize UnitID values to consistent format."""
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")


def _prepare_distance_enrollment_dataframe(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    top_n: int,
    year: int = 2024
) -> DistanceTopEnrollmentResult:
    """Prepare data for distance education enrollment chart."""
    if distance_df.empty:
        return DistanceTopEnrollmentResult(period_label=None, chart_data=distance_df)

    total_columns, de_columns, sde_columns = _identify_enrollment_columns(distance_df.columns)

    if not total_columns:
        raise ValueError("No total enrollment columns found in distance education dataset.")

    working = distance_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Distance education dataset missing 'UnitID' column required for charting.")

    # Find the specific year columns we need
    total_col = None
    de_col = None
    sde_col = None

    for year_val, col_name in total_columns:
        if year_val == year:
            total_col = col_name
            break

    for year_val, col_name in de_columns:
        if year_val == year:
            de_col = col_name
            break

    for year_val, col_name in sde_columns:
        if year_val == year:
            sde_col = col_name
            break

    if not total_col:
        raise ValueError(f"No total enrollment data found for year {year}")

    # Convert enrollment columns to numeric
    working[total_col] = pd.to_numeric(working[total_col], errors="coerce")
    if de_col:
        working[de_col] = pd.to_numeric(working[de_col], errors="coerce")
    if sde_col:
        working[sde_col] = pd.to_numeric(working[sde_col], errors="coerce")

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
        return DistanceTopEnrollmentResult(period_label=None, chart_data=merged)

    # Filter to institutions with valid total enrollment data
    merged = merged[merged[total_col].notna() & (merged[total_col] > 0)].copy()
    if merged.empty:
        return DistanceTopEnrollmentResult(period_label=None, chart_data=merged)

    # Get top N institutions by total enrollment
    top_institutions = merged.nlargest(top_n, total_col).copy()

    # Prepare chart data
    chart_data = []
    for _, row in top_institutions.iterrows():
        institution = row["institution"]
        sector = row["sector"]
        unit_id = row["UnitID"]
        total_enrollment = row[total_col]

        # Get DE enrollments, default to 0 if missing
        exclusive_de = row[de_col] if de_col and pd.notna(row[de_col]) else 0
        some_de = row[sde_col] if sde_col and pd.notna(row[sde_col]) else 0

        # Calculate in-person enrollment (remaining after DE students)
        in_person = max(0, total_enrollment - exclusive_de - some_de)

        # Add rows for each enrollment type
        chart_data.extend([
            {
                "Institution": institution,
                "Sector": sector,
                "UnitID": unit_id,
                "Enrollment_Type": "Exclusively Distance Education",
                "Enrollment": exclusive_de,
                "Total_Enrollment": total_enrollment,
                "Year": year
            },
            {
                "Institution": institution,
                "Sector": sector,
                "UnitID": unit_id,
                "Enrollment_Type": "Some Distance Education",
                "Enrollment": some_de,
                "Total_Enrollment": total_enrollment,
                "Year": year
            },
            {
                "Institution": institution,
                "Sector": sector,
                "UnitID": unit_id,
                "Enrollment_Type": "In-Person Only",
                "Enrollment": in_person,
                "Total_Enrollment": total_enrollment,
                "Year": year
            }
        ])

    chart_df = pd.DataFrame(chart_data)

    # Fill missing sectors
    chart_df["Sector"] = chart_df["Sector"].fillna("Unknown").replace("", "Unknown")

    return DistanceTopEnrollmentResult(
        period_label=str(year),
        chart_data=chart_df
    )


def render_distance_top_enrollment_chart(
    distance_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    top_n: int = 25,
    title: str,
    year: int = 2024
) -> None:
    """Render a horizontal stacked bar chart of top institutions by enrollment with distance education breakdown."""

    try:
        prepared = _prepare_distance_enrollment_dataframe(
            distance_df, metadata_df, top_n, year
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.chart_data.empty:
        st.warning("No distance education enrollment data available to chart.")
        return

    chart_data = prepared.chart_data.copy()

    period_suffix = f" ({prepared.period_label})" if prepared.period_label else ""
    chart_title = f"{title}{period_suffix}"

    # Create enrollment type color scale for stacking
    enrollment_type_color_scale = alt.Scale(
        domain=["Exclusively Distance Education", "Some Distance Education", "In-Person Only"],
        range=["#d62728", "#ff7f0e", "#2ca02c"]  # Red, Orange, Green
    )

    # Calculate number of unique institutions for height
    num_institutions = chart_data["Institution"].nunique()

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "sum(Enrollment):Q",
                title="Student Enrollment",
                stack="zero",
            ),
            y=alt.Y(
                "Institution:N",
                sort=alt.EncodingSortField(field="Total_Enrollment", op="max", order="descending"),
                title="Institution",
            ),
            color=alt.Color(
                "Enrollment_Type:N",
                title="Enrollment Type",
                scale=enrollment_type_color_scale,
                sort=["Exclusively Distance Education", "Some Distance Education", "In-Person Only"],
            ),
            order=alt.Order("Enrollment_Type:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("Enrollment_Type:N", title="Enrollment Type"),
                alt.Tooltip("Enrollment:Q", title="Students", format=","),
                alt.Tooltip("Total_Enrollment:Q", title="Total Enrollment", format=","),
                alt.Tooltip("Sector:N", title="Sector"),
            ],
        )
        .properties(height=max(400, 25 * num_institutions), title=chart_title)
    )

    st.subheader(chart_title)
    period_text = prepared.period_label or "the available year"
    caption_text = f"Top {num_institutions} institutions by total enrollment for {period_text}. Each bar shows the breakdown by distance education participation (exclusive DE, some DE, and in-person only)."
    st.caption(caption_text)
    render_altair_chart(chart, width="stretch")

    # Create summary table
    summary_table = chart_data.pivot_table(
        index=["Institution", "Sector", "Total_Enrollment"],
        columns="Enrollment_Type",
        values="Enrollment",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # Sort by total enrollment descending
    summary_table = summary_table.sort_values("Total_Enrollment", ascending=False)

    # Rename columns for clarity
    summary_table.rename(
        columns={
            "Total_Enrollment": "Total Enrollment",
            "Sector": "Sector",
            "Exclusively Distance Education": "Exclusive DE",
            "Some Distance Education": "Some DE",
            "In-Person Only": "In-Person"
        },
        inplace=True,
    )

    # Format numbers
    for col in ["Total Enrollment", "Exclusive DE", "Some DE", "In-Person"]:
        if col in summary_table.columns:
            summary_table[col] = summary_table[col].astype(int)

    render_dataframe(summary_table, width="stretch")