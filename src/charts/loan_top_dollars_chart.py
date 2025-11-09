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
    table_data: pd.DataFrame
    sector_summary: pd.DataFrame
    requested_top_n: int


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
        empty = pd.DataFrame()
        return LoanTopDollarResult(
            period_label=None,
            chart_data=empty,
            table_data=empty,
            sector_summary=empty,
            requested_top_n=top_n,
        )

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
        empty = pd.DataFrame()
        return LoanTopDollarResult(
            period_label=None,
            chart_data=empty,
            table_data=empty,
            sector_summary=empty,
            requested_top_n=top_n,
        )

    merged["loan_dollars"] = merged[year_field_names].sum(axis=1, skipna=True)
    trimmed = merged[merged["loan_dollars"] > 0].copy()
    if trimmed.empty:
        empty = pd.DataFrame()
        return LoanTopDollarResult(
            period_label=None,
            chart_data=empty,
            table_data=empty,
            sector_summary=empty,
            requested_top_n=top_n,
        )

    trimmed["Institution"] = trimmed["institution"].where(
        trimmed["institution"].notna() & (trimmed["institution"].astype(str) != ""),
        trimmed.get("Institution"),
    )
    trimmed["Institution"] = trimmed["Institution"].fillna("")
    trimmed["sector"] = trimmed["sector"].fillna("Unknown").replace("", "Unknown")

    top = trimmed.sort_values("loan_dollars", ascending=False).head(top_n).copy()
    top["rank"] = range(1, len(top) + 1)
    top["loan_dollars_billions"] = top["loan_dollars"] / 1_000_000_000

    chart_data = top[["rank", "Institution", "sector", "loan_dollars_billions", "loan_dollars"]].copy()
    chart_data.rename(columns={"sector": "Sector"}, inplace=True)

    sector_summary = (
        top.groupby("sector", as_index=False)["loan_dollars"]
        .sum()
        .rename(columns={"sector": "Sector"})
    )
    sector_summary["loan_dollars_billions"] = sector_summary["loan_dollars"] / 1_000_000_000
    sector_summary = sector_summary.sort_values("loan_dollars", ascending=False)
    total_loans = sector_summary["loan_dollars"].sum()
    if total_loans > 0:
        sector_summary["share_pct"] = (sector_summary["loan_dollars"] / total_loans) * 100
    else:
        sector_summary["share_pct"] = 0.0
    sector_summary["label_mid"] = sector_summary["loan_dollars_billions"] / 2

    id_vars = ["UnitID", "Institution", "sector", "loan_dollars", "loan_dollars_billions", "rank"]
    year_data = top[id_vars + year_field_names].melt(
        id_vars=id_vars,
        value_vars=year_field_names,
        var_name="year_column",
        value_name="year_loan_dollars",
    )
    year_data = year_data[year_data["year_loan_dollars"].notna() & (year_data["year_loan_dollars"] > 0)]
    if year_data.empty:
        table_data = pd.DataFrame()
    else:
        year_data["year"] = year_data["year_column"].str.extract(r"YR(\d{4})")[0].astype(int)
        year_data["year_loan_dollars_billions"] = year_data["year_loan_dollars"] / 1_000_000_000
        year_data["loan_dollars_billions"] = year_data["loan_dollars"] / 1_000_000_000
        year_data = year_data.sort_values(["loan_dollars", "year"], ascending=[False, True])

        table = year_data.pivot_table(
            index=["Institution", "sector", "loan_dollars_billions"],
            columns="year",
            values="year_loan_dollars_billions",
            aggfunc="sum",
            fill_value=0,
        ).reset_index()
        table = table.sort_values("loan_dollars_billions", ascending=False)
        table.rename(columns={"sector": "Sector", "loan_dollars_billions": "Total (billions)"}, inplace=True)
        year_cols = [col for col in table.columns if isinstance(col, (int, float))]
        for col in year_cols:
            table[col] = table[col].round(3)
        table["Total (billions)"] = table["Total (billions)"].round(2)
        table.columns = [str(col) for col in table.columns]
        table_data = table

    min_year = year_columns[0][0]
    max_year = year_columns[-1][0]
    period_label = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

    return LoanTopDollarResult(
        period_label=period_label,
        chart_data=chart_data,
        table_data=table_data,
        sector_summary=sector_summary,
        requested_top_n=top_n,
    )


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

    chart_data = prepared.chart_data.copy().sort_values("loan_dollars", ascending=False)
    chart_data["Institution"] = pd.Categorical(chart_data["Institution"], categories=chart_data["Institution"], ordered=True)

    period_suffix = f" ({prepared.period_label})" if prepared.period_label else ""
    chart_title = f"{title}{period_suffix}"

    # Calculate number of unique institutions for height
    num_institutions = chart_data["Institution"].nunique()

    base = alt.Chart(chart_data).encode(
        y=alt.Y(
            "Institution:N",
            sort=None,
            title="Institution",
            axis=alt.Axis(labelFontSize=13, labelFontWeight="bold", titleFontSize=14, titleFontWeight="bold"),
        )
    )

    bars = base.mark_bar().encode(
        x=alt.X(
            "loan_dollars_billions:Q",
            title="Federal loan dollars (billions)",
            axis=alt.Axis(
                format=".2f",
                labelFontSize=12,
                labelFontWeight="bold",
                titleFontSize=14,
                titleFontWeight="bold",
            ),
        ),
        color=alt.Color(
            "Sector:N",
            scale=SECTOR_COLOR_SCALE,
            title="Sector",
        ),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Sector:N", title="Sector"),
            alt.Tooltip("loan_dollars_billions:Q", title="Total loan dollars (billions)", format=".2f"),
            alt.Tooltip("loan_dollars:Q", title="Total loan dollars", format=",.0f"),
            alt.Tooltip("rank:Q", title="Rank"),
        ],
    )

    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=4,
        color="#111111",
        fontSize=11,
        fontWeight="bold",
    ).encode(
        x=alt.X("loan_dollars_billions:Q"),
        text=alt.Text("loan_dollars_billions:Q", format=".2f"),
    )

    chart = (
        (bars + labels)
        .properties(
            height=max(320, 32 * num_institutions),
            width=540,
            title=chart_title,
        )
    )

    st.subheader(chart_title)
    period_text = prepared.period_label or "the available years"
    num_institutions_display = chart_data["Institution"].nunique()
    selection_note = ""
    if num_institutions_display < prepared.requested_top_n:
        selection_note = (
            f" (requested Top {prepared.requested_top_n}, data available for {num_institutions_display})"
        )
    st.caption(
        f"Top {num_institutions_display} institutions by federal loan dollars across {period_text}{selection_note}. "
        "Bars show total loan portfolios, colored by sector."
    )
    render_altair_chart(chart)

    if not prepared.sector_summary.empty:
        st.markdown("#### Sector Totals")
        sector_chart = (
            alt.Chart(prepared.sector_summary)
            .mark_bar()
            .encode(
                y=alt.Y(
                    "Sector:N",
                    sort=alt.SortField(field="loan_dollars", order="descending"),
                    title="Sector",
                    axis=alt.Axis(labelFontSize=12, labelFontWeight="bold", titleFontSize=13, titleFontWeight="bold"),
                ),
                x=alt.X(
                    "loan_dollars_billions:Q",
                    title="Federal loan dollars (billions)",
                    axis=alt.Axis(format=".2f", labelFontSize=12, labelFontWeight="bold", titleFontSize=13, titleFontWeight="bold"),
                ),
                color=alt.Color("Sector:N", scale=SECTOR_COLOR_SCALE, legend=None),
                tooltip=[
                    alt.Tooltip("Sector:N", title="Sector"),
                    alt.Tooltip("loan_dollars_billions:Q", title="Loan dollars (billions)", format=".2f"),
                    alt.Tooltip("loan_dollars:Q", title="Loan dollars", format=",.0f"),
                    alt.Tooltip("share_pct:Q", title="Share of total (%)", format=".1f"),
                ],
            )
            .properties(height=320, width=540)
        )
        label_data = prepared.sector_summary[prepared.sector_summary["loan_dollars"] > 0]
        sector_labels = (
            alt.Chart(label_data)
            .mark_text(
                color="#ffffff",
                fontWeight="bold",
                fontSize=32,
                align="center",
                baseline="middle",
            )
            .encode(
                y=alt.Y(
                    "Sector:N",
                    sort=alt.SortField(field="loan_dollars", order="descending"),
                ),
                x=alt.X("label_mid:Q"),
                text=alt.Text("label:N"),
            )
            .transform_calculate(label="format(datum.share_pct, '.1f') + '%'")
        )
        render_altair_chart(sector_chart + sector_labels)
        st.caption("Sector totals aggregate only the institutions included in the ranking above.")

    if prepared.table_data.empty:
        st.warning("Unable to build year-by-year breakdown for the selected institutions.")
    else:
        render_dataframe(prepared.table_data, width="stretch")
