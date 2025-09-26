"""Line chart utilities for federal loan totals across time."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from src.charts.loan_top_dollars_chart import (
    SECTOR_COLOR_SCALE,
    _identify_year_columns,
    _normalize_unit_ids,
)
from src.ui.renderers import render_altair_chart


def _prepare_loan_trend_dataframe(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    top_n: int = 10,
) -> tuple[pd.DataFrame, int | None]:
    if loans_df.empty:
        return pd.DataFrame(), None

    year_info = _identify_year_columns(loans_df.columns)
    if not year_info:
        raise ValueError("No year columns found in loan dataset (expected headers like 'YR2022').")

    working = loans_df.copy()
    if "UnitID" not in working.columns:
        raise ValueError("Loan dataset missing 'UnitID' column required for trend charting.")

    year_columns = [column for _, column in year_info]
    for column in year_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    working["UnitID"] = _normalize_unit_ids(working.get("UnitID"))

    required_metadata = {"UnitID", "institution", "sector"}
    missing_metadata = [column for column in required_metadata if column not in metadata_df.columns]
    if missing_metadata:
        raise ValueError(
            "Cannot prepare loan trend dataset. Missing metadata columns: "
            + ", ".join(sorted(missing_metadata))
        )

    metadata = metadata_df.copy()
    metadata["UnitID"] = _normalize_unit_ids(metadata.get("UnitID"))
    metadata["institution"] = metadata["institution"].astype("string")
    metadata["sector"] = metadata["sector"].astype("string")

    merged = pd.merge(
        working,
        metadata[["UnitID", "institution", "sector"]],
        on="UnitID",
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame(), None

    long_form = merged.melt(
        id_vars=["UnitID", "institution", "sector"],
        value_vars=year_columns,
        var_name="YearLabel",
        value_name="loan_dollars",
    )

    long_form["loan_dollars"] = pd.to_numeric(long_form["loan_dollars"], errors="coerce")
    long_form.dropna(subset=["loan_dollars"], inplace=True)
    if long_form.empty:
        return pd.DataFrame(), None

    long_form["Year"] = (
        long_form["YearLabel"].str.extract(r"(\d{4})").astype(float)
    )
    long_form.dropna(subset=["Year"], inplace=True)
    if long_form.empty:
        return pd.DataFrame(), None

    long_form["Year"] = long_form["Year"].astype(int)

    anchor_year = int(long_form["Year"].max()) if not long_form.empty else None
    if anchor_year is not None:
        anchor_subset = long_form[long_form["Year"] == anchor_year]
        anchor_subset = anchor_subset.sort_values("loan_dollars", ascending=False)
        top_ids = anchor_subset.dropna(subset=["loan_dollars"])["UnitID"].head(top_n).tolist()
        filtered = long_form[long_form["UnitID"].isin(top_ids)].copy()
        if filtered.empty:
            return pd.DataFrame(), None
    else:
        filtered = long_form.copy()

    filtered["Institution"] = filtered["institution"].astype(str)
    filtered["Sector"] = (
        filtered["sector"].fillna("Unknown").replace("", "Unknown")
    )
    filtered["LoanDollarsBillions"] = filtered["loan_dollars"] / 1_000_000_000
    filtered["AnchorYear"] = anchor_year
    filtered.drop(columns=["YearLabel", "loan_dollars"], inplace=True, errors="ignore")

    columns = [
        "UnitID",
        "Institution",
        "Sector",
        "Year",
        "LoanDollarsBillions",
        "AnchorYear",
    ]
    return filtered.loc[:, columns], anchor_year


def render_loan_trend_chart(
    loans_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    *,
    title: str,
    top_n: int = 10,
) -> None:
    """Render a multi-line trend chart for federal loan totals."""

    try:
        prepared, anchor_year = _prepare_loan_trend_dataframe(
            loans_df,
            metadata_df,
            top_n=top_n,
        )
    except ValueError as exc:
        st.error(str(exc))
        return

    if prepared.empty:
        st.warning("No federal loan trend data available to chart.")
        return

    chart = (
        alt.Chart(prepared)
        .mark_line(point=True)
        .encode(
            x=alt.X("Year:Q", title="Year", axis=alt.Axis(format="d")),
            y=alt.Y(
                "LoanDollarsBillions:Q",
                title="Federal loan dollars (billions)",
            ),
            color=alt.Color("Sector:N", title="Sector", scale=SECTOR_COLOR_SCALE),
            detail=alt.Detail("Institution:N"),
            tooltip=[
                alt.Tooltip("Institution:N", title="Institution"),
                alt.Tooltip("Year:Q", title="Year", format=".0f"),
                alt.Tooltip(
                    "LoanDollarsBillions:Q",
                    title="Loan dollars (billions)",
                    format=".2f",
                ),
                alt.Tooltip("Sector:N", title="Sector"),
            ],
        )
        .properties(height=520)
    )

    st.subheader(title)
    if anchor_year is None:
        caption = (
            "Trends for institutions with available federal loan totals across the selected segment; "
            "colors indicate sector."
        )
    else:
        caption = (
            f"Top {top_n} institutions by federal loan dollars in {anchor_year}, with annual totals over time; "
            "colors indicate sector."
        )
    st.caption(caption)
    render_altair_chart(chart, width="stretch")
