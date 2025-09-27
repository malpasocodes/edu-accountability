"""Federal loan top-dollar chart rendering utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

YEAR_COLUMN_PATTERN = re.compile(r"^YR(\d{4})$", re.IGNORECASE)
SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)


@dataclass(frozen=True)
class LoanTopDollarResult:
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


def _normalize_unit_ids(series: pd.Series) -> pd.Series:
    # Preserve exact values while allowing numeric inputs in raw files.
    coerced = pd.to_numeric(series, errors="coerce")
    return coerced.astype("Int64")


def _prepare_top_dollar_dataframe(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    top_n: int,
) -> LoanTopDollarResult:
    if loans_df.empty:
        return LoanTopDollarResult(period_label=None, chart_data=loans_df)

    year_columns = _identify_year_columns(loans_df.columns)
    if not year_columns:
        raise ValueError("No year columns found in loan dataset (expected columns named like 'YR2022').")

    working = loans_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Loan dataset missing 'UnitID' column required for charting.")
    year_field_names = [column for _, column in year_columns]
    for column in year_field_names:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working["UnitID"] = _normalize_unit_ids(working.get("UnitID"))
    metadata = metadata_df.copy()
    required_metadata = {"UnitID", "institution", "sector"}
    missing_metadata = [column for column in required_metadata if column not in metadata.columns]
    if missing_metadata:
        raise ValueError(
            "Cannot merge loan dataset with metadata. Missing columns: "
            + ", ".join(sorted(missing_metadata))
        )
    metadata["UnitID"] = _normalize_unit_ids(metadata.get("UnitID"))
    metadata["sector"] = metadata["sector"].astype("string")

    merged = pd.merge(
        working,
        metadata[["UnitID", "institution", "sector"]],
        on="UnitID",
        how="inner",
    )
    if merged.empty:
        return LoanTopDollarResult(period_label=None, chart_data=merged)

    merged["loan_dollars"] = merged[year_field_names].sum(axis=1, skipna=True)
    trimmed = merged[merged["loan_dollars"] > 0].copy()
    if trimmed.empty:
        return LoanTopDollarResult(period_label=None, chart_data=trimmed)

    trimmed["Institution"] = trimmed["institution"].where(
        trimmed["institution"].notna() & (trimmed["institution"].astype(str) != ""),
        trimmed.get("Institution"),
    )
    trimmed["Institution"] = trimmed["Institution"].fillna("")
    trimmed["sector"] = trimmed["sector"].fillna("Unknown").replace("", "Unknown")

    top = trimmed.sort_values("loan_dollars", ascending=False).head(top_n).copy()
    top["rank"] = range(1, len(top) + 1)

    # Reshape data to long format for stacked bar chart
    id_vars = ["UnitID", "Institution", "sector", "loan_dollars", "rank"]
    year_data = top[id_vars + year_field_names].melt(
        id_vars=id_vars,
        value_vars=year_field_names,
        var_name="year_column",
        value_name="year_loan_dollars",
    )

    # Extract year from column name and convert to integer for proper sorting
    year_data["year"] = year_data["year_column"].str.extract(r"YR(\d{4})")[0].astype(int)
    year_data["year_loan_dollars_billions"] = year_data["year_loan_dollars"] / 1_000_000_000

    # Filter out NaN values to avoid chart issues
    year_data = year_data[year_data["year_loan_dollars"].notna() & (year_data["year_loan_dollars"] > 0)]

    # Sort by year for proper stacking order
    year_data = year_data.sort_values("year", ascending=True)

    # Calculate total for display
    year_data["loan_dollars_billions"] = year_data["loan_dollars"] / 1_000_000_000

    min_year = year_columns[0][0]
    max_year = year_columns[-1][0]
    period_label = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

    return LoanTopDollarResult(period_label=period_label, chart_data=year_data)


def render_loan_top_dollars_chart(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    top_n: int = 25,
    title: str,
) -> None:
    """Render a horizontal bar chart of top federal loan recipients with supporting table."""

    try:
        prepared = _prepare_top_dollar_dataframe(loans_df, metadata_df, top_n)
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.chart_data.empty:
        st.warning("No federal loan information available to chart.")
        return

    chart_data = prepared.chart_data.copy()
    chart_data.rename(columns={"sector": "Sector"}, inplace=True)

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
                "sum(year_loan_dollars_billions):Q",
                title="Federal loan dollars (billions)",
                axis=alt.Axis(format=".2f"),
                stack="zero",
            ),
            y=alt.Y(
                "Institution:N",
                sort=alt.EncodingSortField(field="loan_dollars", op="max", order="descending"),
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
                alt.Tooltip("year_loan_dollars_billions:Q", title="Loan dollars this year (billions)", format=".3f"),
                alt.Tooltip("loan_dollars_billions:Q", title="Total loan dollars (billions)", format=".2f"),
                alt.Tooltip("Sector:N", title="Sector"),
            ],
        )
        .properties(height=max(320, 32 * num_institutions), title=chart_title)
    )

    st.subheader(chart_title)
    period_text = prepared.period_label or "the available years"
    num_institutions_display = chart_data["Institution"].nunique()
    st.caption(
        f"Top {num_institutions_display} institutions by federal loan dollars across {period_text}. Each bar shows yearly breakdown."
    )
    render_altair_chart(chart, width="stretch")

    # Create summary table with yearly breakdown
    table = chart_data.pivot_table(
        index=["Institution", "Sector", "loan_dollars_billions"],
        columns="year",
        values="year_loan_dollars_billions",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # Sort by total loan dollars descending
    table = table.sort_values("loan_dollars_billions", ascending=False)

    # Rename total column for clarity
    table.rename(columns={"loan_dollars_billions": "Total (billions)"}, inplace=True)

    # Format year columns as billions with 2 decimals
    year_cols = [col for col in table.columns if isinstance(col, (int, float))]
    for col in year_cols:
        table[col] = table[col].round(3)

    table["Total (billions)"] = table["Total (billions)"].round(2)

    # Convert all column names to strings to avoid mixed type warning
    table.columns = [str(col) for col in table.columns]

    render_dataframe(table, width="stretch")
