"""Streamlit dashboard for exploring College ACT datasets."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


def _render_altair_chart(chart: alt.Chart, *, width: str = "stretch") -> None:
    """Render Altair chart with forward-compatible width handling."""

    try:
        st.altair_chart(chart, width=width)
    except TypeError:
        st.altair_chart(chart, use_container_width=(width == "stretch"))


def _render_dataframe(df: pd.DataFrame, *, width: str = "stretch") -> None:
    """Render dataframe with width fallback for older Streamlit releases."""

    try:
        st.dataframe(df, width=width)
    except TypeError:
        st.dataframe(df, use_container_width=(width == "stretch"))

BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DATASETS = {
    "cost_vs_grad": PROCESSED_DIR / "tuition_vs_graduation.csv",
}

SECTOR_COLOR_SCALE = alt.Scale(
    domain=[
        "Public",
        "Private, not-for-profit",
        "Private, for-profit",
    ],
    range=["#2ca02c", "#9467bd", "#1f77b4"],
)


@st.cache_data(show_spinner=False)
def _load_csv(path: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path)


def load_processed(name: str) -> pd.DataFrame:
    path = PROCESSED_DATASETS[name]
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}")
    return _load_csv(str(path), path.stat().st_mtime)


def render_cost_vs_grad_scatter(
    filtered_df: pd.DataFrame,
    min_enrollment: int,
    selected_sectors: list[str],
    global_cost_median: float,
    global_grad_median: float,
) -> None:
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

    medians = pd.DataFrame({
        "cost": [global_cost_median],
        "graduation_rate": [global_grad_median],
    })
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
    _render_altair_chart(chart, width="stretch")

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
    for tab, (label, data) in zip(tabs, quadrants.items()):
        with tab:
            st.write(
                f"{len(data):,} institutions" if not data.empty else "No institutions found"
            )
            if not data.empty:
                display_cols = [
                    "institution",
                    "sector",
                    "cost",
                    "graduation_rate",
                    "enrollment",
                ]
                formatted = data[display_cols].sort_values(
                    by=["graduation_rate", "cost"], ascending=[False, True]
                )
                _render_dataframe(
                    formatted,
                    width="stretch",
                )


def main() -> None:
    st.set_page_config(page_title="College ACT Charts", layout="wide")
    st.title("College Accountability Dashboard")
    st.caption("Explore tuition, enrollment, and outcomes across institutions.")

    st.sidebar.header("Chart Explorer")
    st.sidebar.write("Cost vs Graduation Rate")

    try:
        data = load_processed("cost_vs_grad")
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    if "enrollment" not in data.columns:
        data = data.assign(enrollment=0)
    else:
        data = data.copy()

    data["enrollment"] = pd.to_numeric(data["enrollment"], errors="coerce").fillna(0)

    global_cost_median = data["cost"].median()
    global_grad_median = data["graduation_rate"].median()

    enrollment_series = data["enrollment"]
    max_enrollment = int(enrollment_series.max()) if not enrollment_series.empty else 0
    slider_min = 0
    slider_max = max(0, max_enrollment)

    min_enrollment = st.sidebar.slider(
        "Minimum undergraduate enrollment",
        slider_min,
        slider_max,
        value=1000 if slider_max >= 1000 else slider_max,
        step=100 if slider_max - slider_min >= 100 else 10 if slider_max - slider_min >= 10 else 1,
        help="Filter institutions by undergraduate degree-seeking enrollment (ENR_UGD).",
    )

    sectors = sorted(data["sector"].dropna().unique())
    default_sectors = [
        "Public",
        "Private, not-for-profit",
        "Private, for-profit",
    ]
    default_selection = [s for s in default_sectors if s in sectors] or sectors

    selected_sectors = st.sidebar.multiselect(
        "Sectors",
        options=sectors,
        default=default_selection,
    )

    filtered = data.loc[
        (data["enrollment"] >= min_enrollment) & (data["sector"].isin(selected_sectors))
    ]

    render_cost_vs_grad_scatter(
        filtered,
        min_enrollment,
        selected_sectors,
        global_cost_median,
        global_grad_median,
    )


if __name__ == "__main__":
    main()
