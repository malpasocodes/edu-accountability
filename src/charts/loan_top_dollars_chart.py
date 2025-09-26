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

    min_year = year_columns[0][0]
    max_year = year_columns[-1][0]
    period_label = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)
    trimmed["years_covered"] = period_label
    trimmed["loan_dollars_billions"] = trimmed["loan_dollars"] / 1_000_000_000

    top = trimmed.sort_values("loan_dollars", ascending=False).head(top_n).copy()
    top["rank"] = range(1, len(top) + 1)
    ordered = top.sort_values("loan_dollars", ascending=True)

    display_columns = [
        "rank",
        "UnitID",
        "Institution",
        "sector",
        "loan_dollars",
        "loan_dollars_billions",
        "years_covered",
    ]
    chart_data = ordered.loc[:, [col for col in display_columns if col in ordered.columns]]
    return LoanTopDollarResult(period_label=period_label, chart_data=chart_data)


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

    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "loan_dollars_billions:Q",
                title="Federal loan dollars (billions)",
                axis=alt.Axis(format=".2f"),
            ),
            y=alt.Y(
                "Institution:N",
                sort=alt.EncodingSortField(field="loan_dollars", order="descending"),
                title="Institution",
            ),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("loan_dollars_billions:Q", title="Loan dollars (billions)", format=".2f"),
                alt.Tooltip("Sector:N", title="Sector"),
                alt.Tooltip("years_covered:N", title="Years"),
            ],
            color=alt.Color("Sector:N", title="Sector", scale=SECTOR_COLOR_SCALE),
        )
        .properties(height=max(320, 32 * len(chart_data)), title=chart_title)
    )

    st.subheader(chart_title)
    period_text = prepared.period_label or "the available years"
    st.caption(
        f"Top {len(chart_data)} institutions by federal loan dollars across {period_text}."
    )
    render_altair_chart(chart, width="stretch")

    table = chart_data.sort_values("loan_dollars", ascending=False).copy()
    table.rename(
        columns={
            "loan_dollars_billions": "Loan dollars (billions)",
            "years_covered": "Years",
        },
        inplace=True,
    )
    if "UnitID" in table.columns:
        table.drop(columns=["UnitID"], inplace=True, errors="ignore")
    render_dataframe(table, width="stretch")
