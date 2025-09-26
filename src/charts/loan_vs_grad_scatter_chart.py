"""Scatter chart for federal loan totals versus graduation rate."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.charts.loan_top_dollars_chart import (
    SECTOR_COLOR_SCALE,
    _identify_year_columns,
    _normalize_unit_ids,
)
from src.ui.renderers import render_altair_chart, render_dataframe


def _prepare_loan_vs_grad_dataframe(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    top_n: int,
) -> tuple[pd.DataFrame, str | None]:
    if loans_df.empty:
        return pd.DataFrame(), None

    year_columns = _identify_year_columns(loans_df.columns)
    if not year_columns:
        raise ValueError("No year columns found in loan dataset (expected columns named like 'YR2022').")

    required_metadata = {"UnitID", "institution", "sector", "graduation_rate"}
    missing_metadata = [column for column in required_metadata if column not in metadata_df.columns]
    if missing_metadata:
        raise ValueError(
            "Cannot prepare loan vs graduation dataset. Missing metadata columns: "
            + ", ".join(sorted(missing_metadata))
        )

    working = loans_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Loan dataset missing 'UnitID' column required for charting.")

    numeric_year_columns = [column for _, column in year_columns]
    for column in numeric_year_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    working["UnitID"] = _normalize_unit_ids(working["UnitID"])

    metadata = metadata_df.copy()
    metadata["UnitID"] = _normalize_unit_ids(metadata["UnitID"])
    metadata["graduation_rate"] = pd.to_numeric(metadata["graduation_rate"], errors="coerce")
    metadata["sector"] = metadata["sector"].astype("string")
    metadata["institution"] = metadata["institution"].astype("string")

    merged = pd.merge(
        working,
        metadata[["UnitID", "institution", "sector", "graduation_rate"]],
        on="UnitID",
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame(), None

    merged["loan_dollars"] = merged[numeric_year_columns].sum(axis=1, skipna=True)
    filtered = merged[(merged["loan_dollars"] > 0) & merged["graduation_rate"].notna()].copy()
    if filtered.empty:
        return pd.DataFrame(), None

    min_year = year_columns[0][0]
    max_year = year_columns[-1][0]
    period_label = f"{min_year}-{max_year}" if min_year != max_year else str(min_year)

    filtered["Institution"] = filtered["institution"].fillna("")
    filtered["Sector"] = filtered["sector"].fillna("Unknown").replace("", "Unknown")
    filtered["loan_dollars_billions"] = filtered["loan_dollars"] / 1_000_000_000
    filtered["graduation_rate"] = filtered["graduation_rate"].astype(float)
    filtered["YearsCovered"] = period_label

    top_filtered = filtered.sort_values("loan_dollars_billions", ascending=False).head(top_n).copy()
    return top_filtered, period_label


def render_loan_vs_grad_scatter(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    top_n: int = 50,
) -> None:
    """Render a scatter plot comparing graduation rate to federal loan totals."""

    try:
        prepared, period_label = _prepare_loan_vs_grad_dataframe(
            loans_df,
            metadata_df,
            top_n=top_n,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.empty:
        st.warning("No overlapping federal loan and graduation data available to chart.")
        return

    scatter = (
        alt.Chart(prepared)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "graduation_rate:Q",
                title="Graduation rate",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "loan_dollars_billions:Q",
                title="Federal loan dollars (billions)",
            ),
            color=alt.Color("Sector:N", title="Sector", scale=SECTOR_COLOR_SCALE),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("graduation_rate:Q", title="Graduation rate", format=".1f"),
                alt.Tooltip("loan_dollars_billions:Q", title="Loan dollars (billions)", format=".2f"),
                alt.Tooltip("Sector:N", title="Sector"),
                alt.Tooltip("YearsCovered:N", title="Years"),
            ],
            size=alt.Size(
                "loan_dollars_billions:Q",
                title="Loan dollars (billions)",
                scale=alt.Scale(range=[30, 400]),
            ),
        )
        .properties(height=520)
    )

    st.subheader(title if period_label is None else f"{title} ({period_label})")
    period_text = period_label or "the available years"
    st.caption(
        "Each point represents an institution with total federal loan volume and graduation rate; "
        "bubble size scales with loan totals. Showing top {top_n} institutions by loan dollars.".format(
            top_n=len(prepared)
        )
    )
    render_altair_chart(scatter, width="stretch")

    table = (
        prepared[[
            "Institution",
            "Sector",
            "YearsCovered",
            "loan_dollars_billions",
            "graduation_rate",
        ]]
        .copy()
        .rename(
            columns={
                "YearsCovered": "Years",
                "loan_dollars_billions": "Loan dollars (billions)",
                "graduation_rate": "Graduation rate (%)",
            }
        )
        .sort_values("Loan dollars (billions)", ascending=False)
    )
    table["Loan dollars (billions)"] = table["Loan dollars (billions)"].round(2)
    table["Graduation rate (%)"] = table["Graduation rate (%)"].round(1)

    st.markdown("**Institutions (top loan totals)**")
    render_dataframe(table, width="stretch")
