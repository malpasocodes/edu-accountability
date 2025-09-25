"""Cost-versus-graduation chart rendering utilities."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

from src.ui.renderers import render_altair_chart, render_dataframe


SECTOR_COLOR_SCALE = alt.Scale(
    domain=[
        "Public",
        "Private, not-for-profit",
        "Private, for-profit",
    ],
    range=["#2ca02c", "#9467bd", "#1f77b4"],
)


def render_cost_vs_grad_scatter(
    filtered_df: pd.DataFrame,
    *,
    min_enrollment: int,
    global_cost_median: float,
    global_grad_median: float,
) -> None:
    """Render the cost-versus-graduation chart and supporting tables."""

    if filtered_df.empty:
        st.warning(
            "No institutions match the current filters "
            f"(enrollment >= {min_enrollment:,} and selected sectors)."
        )
        return

    scatter = (
        alt.Chart(filtered_df)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X("cost:Q", title="Cost (In-State Tuition)"),
            y=alt.Y("graduation_rate:Q", title="Graduation Rate"),
            color=alt.Color(
                "sector:N",
                legend=alt.Legend(title="Sector"),
                scale=SECTOR_COLOR_SCALE,
            ),
            size=alt.Size(
                "enrollment:Q",
                title="Undergrad Degree Enrollment",
                scale=alt.Scale(range=[30, 600]),
            ),
            tooltip=[
                alt.Tooltip("institution:N", title="Institution"),
                alt.Tooltip("cost:Q", title="Cost", format="$,.0f"),
                alt.Tooltip("graduation_rate:Q", title="Graduation Rate", format=".1f"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("enrollment:Q", title="Undergrad Enrollment", format=",.0f"),
            ],
        )
    )

    medians = pd.DataFrame(
        {
            "cost": [global_cost_median],
            "graduation_rate": [global_grad_median],
        }
    )
    vline = (
        alt.Chart(medians)
        .mark_rule(color="gray", strokeDash=[6, 4], size=3)
        .encode(x="cost:Q")
    )
    hline = (
        alt.Chart(medians)
        .mark_rule(color="gray", strokeDash=[6, 4], size=3)
        .encode(y="graduation_rate:Q")
    )

    chart = (scatter + vline + hline).properties(height=500)

    st.subheader("Cost vs. Graduation Rate (Level 1 Institutions)")
    st.caption(
        "In-state tuition cost compared against six-year graduation rates. "
        f"Points represent institutions with >= {min_enrollment:,} undergraduate degree students; "
        "dashed lines show global medians (no enrollment filter)."
    )
    render_altair_chart(chart, width="stretch")

    classification = filtered_df.copy()
    classification["cost_group"] = classification["cost"].apply(
        lambda value: "Low" if value <= global_cost_median else "High"
    )
    classification["grad_group"] = classification["graduation_rate"].apply(
        lambda value: "High" if value >= global_grad_median else "Low"
    )

    quadrants = {
        "High GradRate, Low Cost": classification.query(
            "grad_group == 'High' and cost_group == 'Low'"
        ),
        "High GradRate, High Cost": classification.query(
            "grad_group == 'High' and cost_group == 'High'"
        ),
        "Low GradRate, Low Cost": classification.query(
            "grad_group == 'Low' and cost_group == 'Low'"
        ),
        "Low GradRate, High Cost": classification.query(
            "grad_group == 'Low' and cost_group == 'High'"
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
                    "cost",
                    "graduation_rate",
                    "enrollment",
                ]
                formatted = quadrant_data[display_cols].sort_values(
                    by=["graduation_rate", "cost"], ascending=[False, True]
                )
                render_dataframe(formatted, width="stretch")
