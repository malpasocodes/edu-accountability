"""Instructional faculty composition (adjunct reliance) chart utilities.

Ranks institutions by the part-time share of instructional staff -- the standard
IPEDS proxy for adjunct/contingent faculty. A minimum total-staff filter keeps
the ranking meaningful (a three-person department at 100% part-time is noise).
"""

from __future__ import annotations

from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st

from src.ui.renderers import render_altair_chart, render_dataframe

SECTOR_COLOR_SCALE = alt.Scale(
    domain=["Public", "Private, not-for-profit", "Private, for-profit", "Unknown"],
    range=["#2ca02c", "#9467bd", "#1f77b4", "#7f7f7f"],
)

FOUR_YEAR_SECTORS = (1, 2, 3)
TWO_YEAR_SECTORS = (4, 5, 6)


@dataclass(frozen=True)
class FacultyRankingResult:
    chart_data: pd.DataFrame
    table_data: pd.DataFrame
    total_considered: int
    min_total: int
    min_enrollment: int


@st.cache_data(show_spinner=False)
def _prepare_faculty_ranking(
    faculty_df: pd.DataFrame,
    sector: str,
    top_n: int,
    min_total: int,
    min_enrollment: int,
) -> FacultyRankingResult:
    empty = pd.DataFrame()
    if faculty_df is None or faculty_df.empty:
        return FacultyRankingResult(empty, empty, 0, min_total, min_enrollment)

    working = faculty_df.copy()
    working["SECTOR"] = pd.to_numeric(working["SECTOR"], errors="coerce")

    if sector == "four_year":
        working = working[working["SECTOR"].isin(FOUR_YEAR_SECTORS)]
    elif sector == "two_year":
        working = working[working["SECTOR"].isin(TWO_YEAR_SECTORS)]

    if min_enrollment > 0 and "enrollment" in working.columns:
        enrollment = pd.to_numeric(working["enrollment"], errors="coerce")
        working = working[enrollment >= min_enrollment]

    working = working[
        working["total_faculty"].notna()
        & (working["total_faculty"] >= min_total)
        & working["pct_parttime"].notna()
    ].copy()
    total_considered = len(working)
    if working.empty:
        return FacultyRankingResult(empty, empty, 0, min_total, min_enrollment)

    working["sector"] = working["sector"].astype("string").fillna("Unknown")
    working["pct_parttime"] = working["pct_parttime"].round(1)

    ranked = working.sort_values("pct_parttime", ascending=False)
    # top_n <= 0 means "All" (no limit).
    top = (ranked.head(top_n) if top_n and top_n > 0 else ranked).copy()
    top["rank"] = range(1, len(top) + 1)

    chart_data = top.rename(columns={"institution": "Institution", "sector": "Sector"})[
        [
            "rank",
            "Institution",
            "Sector",
            "state",
            "enrollment",
            "pct_parttime",
            "parttime_faculty",
            "fulltime_faculty",
            "total_faculty",
        ]
    ]

    table_data = chart_data.rename(
        columns={
            "rank": "Rank",
            "state": "State",
            "enrollment": "Undergrad Enrollment",
            "pct_parttime": "% Part-time",
            "parttime_faculty": "Part-time",
            "fulltime_faculty": "Full-time",
            "total_faculty": "Total instructional",
        }
    )

    return FacultyRankingResult(
        chart_data=chart_data,
        table_data=table_data,
        total_considered=total_considered,
        min_total=min_total,
        min_enrollment=min_enrollment,
    )


def render_faculty_adjunct_chart(
    faculty_df: pd.DataFrame,
    *,
    sector: str,
    title: str,
    top_n: int = 25,
    min_total: int = 50,
    min_enrollment: int = 0,
) -> None:
    """Render a horizontal bar ranking of part-time (adjunct) instructional share."""

    prepared = _prepare_faculty_ranking(
        faculty_df, sector, top_n, min_total, min_enrollment
    )

    if prepared.chart_data.empty:
        st.warning("No instructional faculty data available for the current selection.")
        return

    chart_data = prepared.chart_data.copy()
    chart_data["Institution"] = pd.Categorical(
        chart_data["Institution"], categories=chart_data["Institution"], ordered=True
    )
    num_institutions = chart_data["Institution"].nunique()

    base = alt.Chart(chart_data).encode(
        y=alt.Y(
            "Institution:N",
            sort=None,
            title="Institution",
            axis=alt.Axis(
                labelFontSize=13,
                labelFontWeight="bold",
                titleFontSize=14,
                titleFontWeight="bold",
            ),
        )
    )

    bars = base.mark_bar().encode(
        x=alt.X(
            "pct_parttime:Q",
            title="Part-time (adjunct) share of instructional staff (%)",
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(
                labelFontSize=12,
                labelFontWeight="bold",
                titleFontSize=14,
                titleFontWeight="bold",
            ),
        ),
        color=alt.Color("Sector:N", scale=SECTOR_COLOR_SCALE, title="Sector"),
        tooltip=[
            alt.Tooltip("Institution:N", title="Institution"),
            alt.Tooltip("Sector:N", title="Sector"),
            alt.Tooltip("state:N", title="State"),
            alt.Tooltip("enrollment:Q", title="Undergrad enrollment", format=",.0f"),
            alt.Tooltip("pct_parttime:Q", title="% part-time", format=".1f"),
            alt.Tooltip("parttime_faculty:Q", title="Part-time staff", format=",.0f"),
            alt.Tooltip("fulltime_faculty:Q", title="Full-time staff", format=",.0f"),
            alt.Tooltip("total_faculty:Q", title="Total instructional", format=",.0f"),
            alt.Tooltip("rank:Q", title="Rank"),
        ],
    )

    # Per-bar height shrinks as the list grows so "All" stays navigable; value
    # labels are dropped once bars get too thin for text to fit cleanly.
    if num_institutions <= 50:
        per_bar = 32
    elif num_institutions <= 100:
        per_bar = 22
    else:
        per_bar = 14

    layers = [bars]
    if num_institutions <= 60:
        labels = (
            base.mark_text(
                align="left",
                baseline="middle",
                dx=4,
                color="#111111",
                fontSize=11,
                fontWeight="bold",
            )
            .encode(
                x=alt.X("pct_parttime:Q"),
                text=alt.Text("label:N"),
            )
            .transform_calculate(
                label="format(datum.pct_parttime, '.1f') + '%  ·  '"
                " + format(datum.enrollment, ',') + ' UG'"
            )
        )
        layers.append(labels)

    chart = alt.layer(*layers).properties(
        height=max(320, per_bar * num_institutions),
        width=540,
        title=title,
    )

    enrollment_note = (
        f" and at least {prepared.min_enrollment:,} undergraduates"
        if prepared.min_enrollment > 0
        else ""
    )
    if num_institutions >= prepared.total_considered:
        count_note = f"All {prepared.total_considered:,} institutions"
    else:
        count_note = (
            f"Top {num_institutions} of {prepared.total_considered:,} institutions"
        )
    st.subheader(title)
    st.caption(
        f"{count_note} (with at least {prepared.min_total} instructional "
        f"staff{enrollment_note}) ranked by part-time share. IPEDS has no "
        "“adjunct” field; part-time instructional staff is the standard proxy. "
        "Source: IPEDS Human Resources (EAP), 2023."
    )
    render_altair_chart(chart)
    render_dataframe(prepared.table_data, width="stretch")
