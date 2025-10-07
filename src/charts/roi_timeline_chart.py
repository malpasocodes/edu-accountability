"""ROI Timeline visualization showing earnings trajectories and tuition period."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def render_roi_timeline_chart() -> None:
    """
    Render an interactive timeline showing college graduate vs high school graduate
    earnings trajectories, with tuition period and evaluation point.

    This chart illustrates the ROI concept using Maya (college graduate) and Jordan
    (high school graduate) as examples, with realistic growth rates over 15 years.
    """
    # --- Parameters ---
    years = np.arange(0, 16)  # 0–15 years after enrollment
    enrollment_years = 5  # Maya is in school for 5 years
    tuition_total = 50000  # total tuition & fees
    tuition_per_year = tuition_total / enrollment_years

    # Annual earnings assumptions
    jordan_start = 45000  # Jordan starts at $45k
    jordan_growth = 0.02

    maya_start = 70000  # Maya starts at $70k after graduation
    maya_growth = 0.03

    # --- Annual earnings series ---
    jordan_earn = np.array([jordan_start * ((1 + jordan_growth) ** t) for t in years])

    maya_earn = np.zeros_like(years, dtype=float)
    for t in years:
        if t >= enrollment_years:
            years_after_grad = t - enrollment_years
            maya_earn[t] = maya_start * ((1 + maya_growth) ** years_after_grad)

    # --- Build figure ---
    fig = go.Figure()

    # Jordan's line
    fig.add_trace(
        go.Scatter(
            x=years,
            y=jordan_earn,
            mode="lines+markers",
            name="Jordan (High School Graduate)",
            line=dict(color="gray", width=3, dash="dash"),
            marker=dict(size=6),
            hovertemplate="<b>Jordan</b><br>Year: %{x}<br>Earnings: $%{y:,.0f}<extra></extra>",
        )
    )

    # Maya's line
    fig.add_trace(
        go.Scatter(
            x=years,
            y=maya_earn,
            mode="lines+markers",
            name="Maya (College Graduate)",
            line=dict(color="blue", width=3),
            marker=dict(size=6),
            hovertemplate="<b>Maya</b><br>Year: %{x}<br>Earnings: $%{y:,.0f}<extra></extra>",
        )
    )

    # Shaded area: Maya's cost while in school
    fig.add_vrect(
        x0=0,
        x1=enrollment_years,
        fillcolor="lightblue",
        opacity=0.3,
        layer="below",
        annotation_text="Tuition & Fees (\$50,000 total)",
        annotation_position="top left",
        annotation=dict(font=dict(size=11, color="#1f77b4")),
    )

    # Graduation marker
    fig.add_vline(x=enrollment_years, line_width=2, line_dash="dot", line_color="black")
    fig.add_annotation(
        x=enrollment_years,
        y=maya_start * 0.8,
        text="Graduation (Year 5)",
        showarrow=False,
        font=dict(size=11, color="black"),
    )

    # Annotation for evaluation (some number of years, e.g. five)
    evaluation_year = enrollment_years + 5
    fig.add_vline(x=evaluation_year, line_width=1, line_dash="dot", line_color="green")
    fig.add_annotation(
        x=evaluation_year,
        y=maya_start * 1.5,
        text="Evaluation: some number of years<br>(e.g., five) after graduation",
        showarrow=False,
        font=dict(size=10, color="green"),
    )

    # Update layout
    fig.update_layout(
        title="Maya vs. Jordan: Annual Earnings and Tuition Period",
        xaxis_title="Years Since Enrollment",
        yaxis_title="Annual Earnings (\$)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=500,
        yaxis=dict(tickformat="$,.0f"),
    )

    # Render in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Add explanatory caption
    st.caption(
        "**Interactive Chart**: Hover over the lines to see earnings at each year. "
        "The light blue shaded area represents Maya's tuition period (5 years, \$50,000 total). "
        "The green dotted line marks the evaluation point—5 years after graduation (Year 10)—when "
        "the Earnings Premium Test compares graduate earnings to the high school baseline."
    )
