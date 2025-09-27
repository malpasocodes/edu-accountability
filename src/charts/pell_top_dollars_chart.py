"""Pell grant top-dollar chart rendering utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

YEAR_COLUMN_PATTERN = re.compile(r"^YR(\\d{4})$", re.IGNORECASE)
SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


@dataclass(frozen=True)
class PellTopDollarResult:
    period_label: Optional[str]
    chart_data: pd.DataFrame


def _identify_year_columns(columns: Iterable[str]) -> List[tuple[int, str]]:
    discovered: List[tuple[int, str]] = []
    for column in columns:
        normalized = column.strip()
        match = YEAR_COLUMN_PATTERN.match(normalized)
        if match:
            year = int(match.group(1))
            discovered.append((year, column))
    return sorted(discovered)


def _prepare_top_dollar_dataframe(df: pd.DataFrame, top_n: int) -> PellTopDollarResult:
    working = df.copy()
    lower_map = {column.lower(): column for column in working.columns}

    value_column = None
    for candidate in ("pelldollars", "pell_dollars"):
        if candidate in lower_map:
            value_column = lower_map[candidate]
            break

    period_label: Optional[str] = None

    if value_column is not None:
        working[value_column] = pd.to_numeric(working[value_column], errors="coerce")
        trimmed = working.dropna(subset=[value_column])
        sorted_trimmed = trimmed.sort_values(value_column, ascending=False).head(top_n).copy()
        sorted_trimmed.rename(columns={value_column: "pell_dollars"}, inplace=True)

        billions_column = lower_map.get("pelldollarsbillions") or lower_map.get("pell_dollars_billions")
        if billions_column and billions_column in sorted_trimmed.columns:
            sorted_trimmed.rename(columns={billions_column: "pell_dollars_billions"}, inplace=True)
            sorted_trimmed["pell_dollars_billions"] = pd.to_numeric(
                sorted_trimmed["pell_dollars_billions"], errors="coerce"
            )
            if sorted_trimmed["pell_dollars_billions"].isna().any():
                sorted_trimmed["pell_dollars_billions"] = (
                    sorted_trimmed["pell_dollars"] / 1_000_000_000
                )
        else:
            sorted_trimmed["pell_dollars_billions"] = sorted_trimmed["pell_dollars"] / 1_000_000_000

        rank_column = lower_map.get("rank")
        if rank_column and rank_column in sorted_trimmed.columns:
            if rank_column != "rank":
                sorted_trimmed.rename(columns={rank_column: "rank"}, inplace=True)
            sorted_trimmed["rank"] = pd.to_numeric(sorted_trimmed["rank"], errors="coerce")
            if sorted_trimmed["rank"].isna().any():
                sorted_trimmed["rank"] = range(1, len(sorted_trimmed) + 1)
        else:
            sorted_trimmed["rank"] = range(1, len(sorted_trimmed) + 1)

        institution_column = lower_map.get("institution")
        if institution_column and institution_column != "Institution":
            sorted_trimmed.rename(columns={institution_column: "Institution"}, inplace=True)
        elif "Institution" not in sorted_trimmed.columns:
            sorted_trimmed["Institution"] = ""

        unitid_column = lower_map.get("unitid")
        if unitid_column and unitid_column != "UnitID":
            sorted_trimmed.rename(columns={unitid_column: "UnitID"}, inplace=True)

        sector_column = lower_map.get("sector")
        if sector_column:
            if sector_column != "sector":
                sorted_trimmed.rename(columns={sector_column: "sector"}, inplace=True)
        if "sector" not in sorted_trimmed.columns:
            sorted_trimmed["sector"] = "Unknown"
        else:
            sorted_trimmed["sector"] = (
                sorted_trimmed["sector"].fillna("Unknown").replace("", "Unknown")
            )

        years_column = lower_map.get("yearscovered")
        if years_column and years_column in sorted_trimmed.columns:
            sorted_trimmed.rename(columns={years_column: "years_covered"}, inplace=True)
            labels = sorted_trimmed["years_covered"].dropna().astype(str)
            if not labels.empty:
                period_label = labels.iloc[0]
        else:
            year_column = lower_map.get("year")
            if year_column and year_column in sorted_trimmed.columns:
                years = pd.to_numeric(sorted_trimmed[year_column], errors="coerce").dropna()
                if not years.empty:
                    period_label = str(int(years.iloc[0]))
                sorted_trimmed.drop(columns=[year_column], inplace=True, errors="ignore")
                sorted_trimmed["years_covered"] = period_label

        if "years_covered" not in sorted_trimmed.columns:
            sorted_trimmed["years_covered"] = period_label or ""

        ordered = sorted_trimmed.sort_values("pell_dollars", ascending=True)
        return PellTopDollarResult(period_label=period_label, chart_data=ordered)

    year_columns = _identify_year_columns(working.columns)
    if not year_columns:
        raise ValueError("No year columns found in Pell dataset (expected columns named like 'YR2022').")

    value_columns = [column for _, column in year_columns]
    for column in value_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working["pell_dollars"] = working[value_columns].sum(axis=1, skipna=True)
    trimmed = working[working["pell_dollars"] > 0].copy()
    if trimmed.empty:
        return PellTopDollarResult(period_label=None, chart_data=trimmed)

    keep_columns = [
        column
        for column in ["UnitID", "Institution", "sector", "pell_dollars"]
        if column in trimmed.columns
    ]
    top = trimmed.loc[:, keep_columns].sort_values("pell_dollars", ascending=False).head(top_n).copy()
    if "sector" not in top.columns:
        top["sector"] = "Unknown"
    else:
        top["sector"] = top["sector"].fillna("Unknown").replace("", "Unknown")
    top["rank"] = range(1, len(top) + 1)

    # Reshape data to long format for stacked bar chart
    id_vars = ["UnitID", "Institution", "sector", "pell_dollars", "rank"] if "UnitID" in top.columns else ["Institution", "sector", "pell_dollars", "rank"]
    year_data = top[id_vars + value_columns].melt(
        id_vars=id_vars,
        value_vars=value_columns,
        var_name="year_column",
        value_name="year_pell_dollars",
    )

    # Extract year from column name and convert to integer for proper sorting
    year_data["year"] = year_data["year_column"].str.extract(r"YR(\d{4})")[0].astype(int)
    year_data["year_pell_dollars_billions"] = year_data["year_pell_dollars"] / 1_000_000_000

    # Filter out NaN values to avoid chart issues
    year_data = year_data[year_data["year_pell_dollars"].notna() & (year_data["year_pell_dollars"] > 0)]

    # Sort by year for proper stacking order
    year_data = year_data.sort_values("year", ascending=True)

    # Calculate total for display
    year_data["pell_dollars_billions"] = year_data["pell_dollars"] / 1_000_000_000

    min_year = year_columns[0][0]
    max_year = year_columns[-1][0]
    period_label = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

    return PellTopDollarResult(period_label=period_label, chart_data=year_data)





def render_pell_top_dollars_chart(df: pd.DataFrame, *, top_n: int = 25, title: str) -> None:
    """Render a horizontal bar chart of top Pell dollar recipients with supporting table."""

    try:
        prepared = _prepare_top_dollar_dataframe(df, top_n)
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.chart_data.empty:
        st.warning("No Pell dollar information available to chart.")
        return

    chart_data = prepared.chart_data.copy()
    if "sector" in chart_data.columns:
        chart_data["sector"] = chart_data["sector"].fillna("Unknown").replace("", "Unknown")
    else:
        chart_data["sector"] = "Unknown"

    period_suffix = f" ({prepared.period_label})" if prepared.period_label else ""
    chart_title = f"{title}{period_suffix}"

    # Create year color scale for stacking
    year_color_scale = alt.Scale(
        scheme="viridis",
        reverse=False  # Older years darker, newer years lighter
    )

    # Calculate number of unique institutions for height
    num_institutions = chart_data["Institution"].nunique()

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "sum(year_pell_dollars_billions):Q",
                title="Pell grant dollars (billions)",
                axis=alt.Axis(format=".2f"),
                stack="zero",
            ),
            y=alt.Y(
                "Institution:N",
                sort=alt.EncodingSortField(field="pell_dollars", op="max", order="descending"),
                title="Institution",
            ),
            color=alt.Color(
                "year:O",
                title="Year",
                scale=year_color_scale,
                sort="ascending",
            ),
            order=alt.Order("year:O", sort="ascending"),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("year_pell_dollars_billions:Q", title="Pell dollars this year (billions)", format=".3f"),
                alt.Tooltip("pell_dollars_billions:Q", title="Total Pell dollars (billions)", format=".2f"),
                alt.Tooltip("sector:N", title="Sector"),
            ],
        )
        .properties(height=max(320, 32 * num_institutions), title=chart_title)
    )

    st.subheader(chart_title)
    period_text = prepared.period_label or "the available years"
    num_institutions_display = chart_data["Institution"].nunique()
    st.caption(
        f"Top {num_institutions_display} institutions by Pell grant dollars across {period_text}. Each bar shows yearly breakdown."
    )
    render_altair_chart(chart, width="stretch")

    # Create summary table with yearly breakdown
    table = chart_data.pivot_table(
        index=["Institution", "sector", "pell_dollars_billions"],
        columns="year",
        values="year_pell_dollars_billions",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # Sort by total Pell dollars descending
    table = table.sort_values("pell_dollars_billions", ascending=False)

    # Rename total column for clarity
    table.rename(columns={"pell_dollars_billions": "Total (billions)", "sector": "Sector"}, inplace=True)

    # Format year columns as billions with 3 decimals
    year_cols = [col for col in table.columns if isinstance(col, (int, float))]
    for col in year_cols:
        table[col] = table[col].round(3)

    table["Total (billions)"] = table["Total (billions)"].round(2)

    # Convert all column names to strings to avoid mixed type warning
    table.columns = [str(col) for col in table.columns]

    render_dataframe(table, width="stretch")
