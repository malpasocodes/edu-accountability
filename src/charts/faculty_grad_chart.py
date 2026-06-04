"""Adjunct-reliance-versus-graduation scatter (quadrant) chart utilities.

Plots six-year graduation rate (y) against the part-time/adjunct share of
instructional staff (x), with median crosshairs splitting institutions into four
quadrants. Mirrors the College Value Grid cost-vs-graduation chart.
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
class GradScatterResult:
    points: pd.DataFrame
    pct_median: float
    grad_median: float
    segment_size: int
    min_enrollment: int


@st.cache_data(show_spinner=False)
def _prepare_grad_scatter(
    faculty_df: pd.DataFrame,
    sector: str,
    min_enrollment: int,
) -> GradScatterResult:
    if faculty_df is None or faculty_df.empty:
        return GradScatterResult(pd.DataFrame(), 0.0, 0.0, 0, min_enrollment)

    working = faculty_df.copy()
    working["SECTOR"] = pd.to_numeric(working["SECTOR"], errors="coerce")
    if sector == "four_year":
        working = working[working["SECTOR"].isin(FOUR_YEAR_SECTORS)]
    elif sector == "two_year":
        working = working[working["SECTOR"].isin(TWO_YEAR_SECTORS)]

    working["graduation_rate"] = pd.to_numeric(
        working["graduation_rate"], errors="coerce"
    )
    working["pct_parttime"] = pd.to_numeric(working["pct_parttime"], errors="coerce")
    working["enrollment"] = pd.to_numeric(working["enrollment"], errors="coerce")

    # Segment = institutions with both axes present. Medians come from the full
    # segment so the quadrant crosshairs stay fixed as the enrollment filter moves.
    segment = working.dropna(subset=["graduation_rate", "pct_parttime"]).copy()
    if segment.empty:
        return GradScatterResult(pd.DataFrame(), 0.0, 0.0, 0, min_enrollment)

    pct_median = float(segment["pct_parttime"].median())
    grad_median = float(segment["graduation_rate"].median())

    points = segment
    if min_enrollment > 0:
        points = segment[segment["enrollment"] >= min_enrollment]

    points = points[
        [
            "institution",
            "sector",
            "state",
            "enrollment",
            "graduation_rate",
            "pct_parttime",
        ]
    ].copy()
    points["sector"] = points["sector"].astype("string").fillna("Unknown")

    return GradScatterResult(
        points=points,
        pct_median=pct_median,
        grad_median=grad_median,
        segment_size=len(segment),
        min_enrollment=min_enrollment,
    )


def _clamp(value: float, lower: float, upper: float) -> float:
    if lower == upper:
        return lower
    cushion = (upper - lower) * 0.05 or 0.01
    return min(max(value, lower + cushion), upper - cushion)


def render_faculty_grad_scatter(
    faculty_df: pd.DataFrame,
    *,
    sector: str,
    title: str,
    min_enrollment: int = 0,
) -> None:
    """Render the adjunct-reliance-versus-graduation quadrant scatter."""

    prepared = _prepare_grad_scatter(faculty_df, sector, min_enrollment)
    points = prepared.points

    if points.empty:
        if min_enrollment <= 1:
            filter_text = "enrollment > 0"
        else:
            filter_text = f"enrollment >= {min_enrollment:,}"
        st.warning(
            "No institutions have both a graduation rate and adjunct share for the "
            f"current filters ({filter_text})."
        )
        return

    pct_min = float(points["pct_parttime"].min())
    pct_max = float(points["pct_parttime"].max())
    grad_min = float(points["graduation_rate"].min())
    grad_max = float(points["graduation_rate"].max())

    scatter = (
        alt.Chart(points)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "pct_parttime:Q",
                title="Adjunct (Part-time) Share of Instructional Staff (%)",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(titleFontSize=18, titleFontWeight="bold"),
            ),
            y=alt.Y(
                "graduation_rate:Q",
                title="Graduation Rate",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(titleFontSize=18, titleFontWeight="bold"),
            ),
            color=alt.Color(
                "sector:N",
                legend=alt.Legend(title="Sector"),
                scale=SECTOR_COLOR_SCALE,
            ),
            size=alt.Size(
                "enrollment:Q",
                legend=None,
                scale=alt.Scale(range=[30, 600]),
            ),
            tooltip=[
                alt.Tooltip("institution:N", title="Institution"),
                alt.Tooltip(
                    "pct_parttime:Q", title="% Adjunct (part-time)", format=".1f"
                ),
                alt.Tooltip("graduation_rate:Q", title="Graduation Rate", format=".1f"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip(
                    "enrollment:Q", title="Undergrad Enrollment", format=",.0f"
                ),
            ],
        )
    )

    medians = pd.DataFrame(
        {
            "pct_parttime": [prepared.pct_median],
            "graduation_rate": [prepared.grad_median],
        }
    )
    vline = (
        alt.Chart(medians)
        .mark_rule(color="gray", strokeDash=[6, 4], size=3)
        .encode(x="pct_parttime:Q")
    )
    hline = (
        alt.Chart(medians)
        .mark_rule(color="gray", strokeDash=[6, 4], size=3)
        .encode(y="graduation_rate:Q")
    )

    pct_span = max(pct_max - pct_min, 1.0)
    grad_span = max(grad_max - grad_min, 1.0)
    x_offset = pct_span * 0.25
    y_offset = grad_span * 0.25

    annotation_positions = pd.DataFrame(
        [
            {  # I: low adjunct, high grad (best)
                "label": "I",
                "x": _clamp(prepared.pct_median - x_offset, pct_min, pct_max),
                "y": _clamp(prepared.grad_median + y_offset, grad_min, grad_max),
            },
            {  # II: high adjunct, high grad
                "label": "II",
                "x": _clamp(prepared.pct_median + x_offset, pct_min, pct_max),
                "y": _clamp(prepared.grad_median + y_offset, grad_min, grad_max),
            },
            {  # III: low adjunct, low grad
                "label": "III",
                "x": _clamp(prepared.pct_median - x_offset, pct_min, pct_max),
                "y": _clamp(prepared.grad_median - y_offset, grad_min, grad_max),
            },
            {  # IV: high adjunct, low grad (concern)
                "label": "IV",
                "x": _clamp(prepared.pct_median + x_offset, pct_min, pct_max),
                "y": _clamp(prepared.grad_median - y_offset, grad_min, grad_max),
            },
        ]
    )
    annotations = (
        alt.Chart(annotation_positions)
        .mark_text(fontWeight="bold", fontSize=34, color="#313131")
        .encode(x="x:Q", y="y:Q", text="label:N")
    )

    chart = (scatter + vline + hline + annotations).properties(height=500)

    st.subheader(title)
    if min_enrollment <= 1:
        enrollment_text = "all enrollment levels"
    else:
        enrollment_text = f">= {min_enrollment:,} undergraduate degree-seeking students"
    st.caption(
        "Six-year graduation rate compared with the part-time (adjunct) share of "
        f"instructional staff. Points represent institutions with {enrollment_text}; "
        "dashed lines show segment medians. IPEDS has no “adjunct” field; part-time "
        "instructional staff is the standard proxy. "
        "_Sources: IPEDS EAP2023 (staffing) and GR2023 (150% of normal time, 2015 "
        "entering cohort)._"
    )
    st.markdown(
        "**Quadrant legend:** I = High GradRate, Low Adjunct; "
        "II = High GradRate, High Adjunct; III = Low GradRate, Low Adjunct; "
        "IV = Low GradRate, High Adjunct"
    )
    render_altair_chart(chart)

    classification = points.copy()
    classification["adjunct_group"] = classification["pct_parttime"].apply(
        lambda value: "Low" if value <= prepared.pct_median else "High"
    )
    classification["grad_group"] = classification["graduation_rate"].apply(
        lambda value: "High" if value >= prepared.grad_median else "Low"
    )

    quadrants = {
        "High GradRate, Low Adjunct": classification.query(
            "grad_group == 'High' and adjunct_group == 'Low'"
        ),
        "High GradRate, High Adjunct": classification.query(
            "grad_group == 'High' and adjunct_group == 'High'"
        ),
        "Low GradRate, Low Adjunct": classification.query(
            "grad_group == 'Low' and adjunct_group == 'Low'"
        ),
        "Low GradRate, High Adjunct": classification.query(
            "grad_group == 'Low' and adjunct_group == 'High'"
        ),
    }

    tabs = st.tabs(list(quadrants.keys()))
    for tab, (label, quadrant_data) in zip(tabs, quadrants.items()):
        with tab:
            st.write(
                f"{len(quadrant_data):,} institutions"
                if not quadrant_data.empty
                else "No institutions found"
            )
            if not quadrant_data.empty:
                display_cols = [
                    "institution",
                    "sector",
                    "pct_parttime",
                    "graduation_rate",
                    "enrollment",
                ]
                formatted = quadrant_data[display_cols].sort_values(
                    by=["graduation_rate", "pct_parttime"], ascending=[False, True]
                )
                render_dataframe(formatted, width="stretch")
