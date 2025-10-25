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
    group_label: str,
) -> None:
    """Render the cost-versus-graduation chart and supporting tables."""

    if filtered_df.empty:
        if min_enrollment <= 1:
            filter_text = "enrollment > 0"
        else:
            filter_text = f"enrollment >= {min_enrollment:,}"
        st.warning(
            f"No institutions match the current filters ({filter_text})."
        )
        return

    cost_min = float(filtered_df["cost"].min())
    cost_max = float(filtered_df["cost"].max())
    grad_min = float(filtered_df["graduation_rate"].min())
    grad_max = float(filtered_df["graduation_rate"].max())

    cost_domain_min = min(cost_min, global_cost_median)
    cost_domain_max = max(cost_max, global_cost_median)
    if cost_domain_min == cost_domain_max:
        cost_domain_min -= 0.5
        cost_domain_max += 0.5

    grad_domain_min = min(grad_min, global_grad_median)
    grad_domain_max = max(grad_max, global_grad_median)
    if grad_domain_min == grad_domain_max:
        grad_domain_min -= 0.5
        grad_domain_max += 0.5

    scatter = (
        alt.Chart(filtered_df)
        .mark_circle(opacity=0.75)
        .encode(
            x=alt.X(
                "cost:Q",
                title="Cost (In-State Tuition, 2023-24 USD)",
                scale=alt.Scale(domain=[cost_domain_min, cost_domain_max]),
                axis=alt.Axis(titleFontSize=18, titleFontWeight="bold"),
            ),
            y=alt.Y(
                "graduation_rate:Q",
                title="Graduation Rate",
                scale=alt.Scale(domain=[grad_domain_min, grad_domain_max]),
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
                alt.Tooltip("cost:Q", title="Cost (2023-24 Tuition)", format="$,.0f"),
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

    cost_span = max(cost_max - cost_min, 1.0)
    grad_span = max(grad_max - grad_min, 1.0)
    x_offset = cost_span * 0.25
    y_offset = grad_span * 0.25

    def _clamp(value: float, lower: float, upper: float) -> float:
        if lower == upper:
            return lower
        cushion = (upper - lower) * 0.05
        if cushion == 0:
            cushion = 0.01
        return min(max(value, lower + cushion), upper - cushion)

    annotation_positions = pd.DataFrame(
        [
            {
                "label": "I",
                "x": _clamp(global_cost_median - x_offset, cost_min, cost_max),
                "y": _clamp(global_grad_median + y_offset, grad_min, grad_max),
            },
            {
                "label": "II",
                "x": _clamp(global_cost_median + x_offset, cost_min, cost_max),
                "y": _clamp(global_grad_median + y_offset, grad_min, grad_max),
            },
            {
                "label": "III",
                "x": _clamp(global_cost_median - x_offset, cost_min, cost_max),
                "y": _clamp(global_grad_median - y_offset, grad_min, grad_max),
            },
            {
                "label": "IV",
                "x": _clamp(global_cost_median + x_offset, cost_min, cost_max),
                "y": _clamp(global_grad_median - y_offset, grad_min, grad_max),
            },
        ]
    )

    annotations = (
        alt.Chart(annotation_positions)
        .mark_text(fontWeight="bold", fontSize=34, color="#313131")
        .encode(x="x:Q", y="y:Q", text="label:N")
    )

    chart = (scatter + vline + hline + annotations).properties(height=500)

    st.subheader(group_label)

    # Format enrollment filter text
    if min_enrollment <= 1:
        enrollment_text = "all enrollment levels"
    else:
        enrollment_text = f">= {min_enrollment:,} undergraduate degree-seeking students"

    st.caption(
        "In-state tuition compared with six-year graduation rates. "
        f"Points represent {group_label.lower()} with {enrollment_text}; "
        "dashed lines show medians across the full segment. "
        "_Sources: IPEDS IC2023_AY (tuition) and GR2023 (150% of normal time, 2015 entering cohort)._"
    )
    st.markdown(
        "**Quadrant legend:** I = High GradRate, Low Cost; II = High GradRate, High Cost; "
        "III = Low GradRate, Low Cost; IV = Low GradRate, High Cost"
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

    st.markdown(
        """
        <style>
        div[data-testid="stTabs"] button[role="tab"] div p {
            font-size: 1.25rem !important;
            font-weight: 600;
        }
        div[data-testid="stTabs"] button[role="tab"] div {
            font-size: 1.25rem !important;
        }
        div[data-testid="stTabs"] button[role="tab"] p {
            font-size: 1.25rem !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
