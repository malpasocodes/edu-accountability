"""Streamlit Phase 1 skeleton with structured sidebar sections."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter
from src.data.datasets import load_processed
from src.ui.renderers import render_dataframe

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PELL_SOURCE = DATA_DIR / "raw" / "pelltotals.csv"

VALUE_GRID_SECTION = "College Value Grid"
PELL_SECTION = "Pell Grants"


@dataclass(frozen=True)
class ValueGridChartConfig:
    label: str
    dataset_key: str
    min_enrollment: int


VALUE_GRID_CHART_CONFIGS = (
    ValueGridChartConfig(
        label="Cost vs Graduation (4-year)",
        dataset_key="cost_vs_grad",
        min_enrollment=1000,
    ),
    ValueGridChartConfig(
        label="Cost vs Graduation (2-year)",
        dataset_key="cost_vs_grad_two_year",
        min_enrollment=0,
    ),
)
VALUE_GRID_CHARTS = [config.label for config in VALUE_GRID_CHART_CONFIGS]
VALUE_GRID_CONFIG_MAP = {config.label: config for config in VALUE_GRID_CHART_CONFIGS}

PELL_CHARTS = [
    "Pell share by institution (coming soon)",
    "Pell recipients vs Net Price (coming soon)",
    "Pell dollars by region (coming soon)",
]


def _init_session_state() -> None:
    defaults: Dict[str, str] = {
        "active_section": VALUE_GRID_SECTION,
        "value_grid_chart": VALUE_GRID_CHARTS[0],
        "pell_chart": PELL_CHARTS[0],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


@st.cache_data(show_spinner=False)
def load_pell_dataset(path_str: str) -> pd.DataFrame:
    """Load the Pell totals dataset."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Pell dataset not found at {path}.")
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def _prepare_value_grid_dataset(label: str, df: pd.DataFrame) -> pd.DataFrame:
    """Prepare dataset for cost vs graduation rendering (basic cleanup)."""

    _ = label  # differentiate cache entries per label

    working = df.copy()
    if "enrollment" in working.columns:
        working["enrollment"] = pd.to_numeric(working["enrollment"], errors="coerce").fillna(0)
    if "cost" in working.columns:
        working["cost"] = pd.to_numeric(working["cost"], errors="coerce")
    if "graduation_rate" in working.columns:
        working["graduation_rate"] = pd.to_numeric(working["graduation_rate"], errors="coerce")
    return working


def render_sidebar() -> None:
    sidebar = st.sidebar
    sidebar.title("Navigation")

    active_section = sidebar.radio(
        "Explore",
        [VALUE_GRID_SECTION, PELL_SECTION],
        key="active_section",
    )

    if active_section == VALUE_GRID_SECTION:
        sidebar.radio(
            "Chart Type",
            VALUE_GRID_CHARTS,
            key="value_grid_chart",
            help="Switch between four-year and two-year value grid charts.",
        )
    else:
        sidebar.radio(
            "Chart Type",
            PELL_CHARTS,
            key="pell_chart",
            help="Pell charts will appear once they are built.",
        )


def _render_value_grid_chart(label: str, dataset: pd.DataFrame, min_enrollment: int) -> None:
    columns_needed = {"institution", "sector", "cost", "graduation_rate"}
    missing = [column for column in columns_needed if column not in dataset.columns]
    if missing:
        st.error(
            "Cannot render cost vs graduation chart. Missing columns: " + ", ".join(missing)
        )
        return

    prepared = _prepare_value_grid_dataset(label, dataset)
    if min_enrollment > 0 and "enrollment" in prepared.columns:
        filtered = prepared[prepared["enrollment"] >= min_enrollment]
    else:
        filtered = prepared

    filtered = filtered.dropna(subset=["cost", "graduation_rate"])
    if filtered.empty:
        st.warning("No institutions meet the current baseline criteria.")
        return

    cost_median = float(prepared["cost"].dropna().median())
    grad_median = float(prepared["graduation_rate"].dropna().median())

    render_cost_vs_grad_scatter(
        filtered,
        min_enrollment=min_enrollment,
        global_cost_median=cost_median,
        global_grad_median=grad_median,
        group_label=label,
    )


def render_main(
    active_section: str,
    active_chart: str,
    value_grid_datasets: Dict[str, pd.DataFrame],
    pell_df: pd.DataFrame,
) -> None:
    st.title(f"{active_section} » {active_chart}")
    st.caption(
        "We are rebuilding the dashboard with section-scoped charts, filters, and exports. "
        "New functionality arrives as we progress through the build phases."
    )

    if active_section == VALUE_GRID_SECTION:
        config = VALUE_GRID_CONFIG_MAP[active_chart]
        dataset = value_grid_datasets.get(config.label)
        if dataset is None:
            st.error("Unable to locate dataset for the selected chart.")
            return
        _render_value_grid_chart(config.label, dataset, config.min_enrollment)
    else:
        st.info(
            f"{active_chart} will be available in a later phase. Until then, preview the "
            "underlying Pell dataset below."
        )
        render_dataframe(pell_df.head(20), width="stretch")


def main() -> None:
    st.set_page_config(page_title="College Value Explorer", layout="wide")
    _init_session_state()

    try:
        pell_df = load_pell_dataset(str(PELL_SOURCE))
    except FileNotFoundError as exc:
        st.sidebar.error(str(exc))
        st.error("Unable to load required datasets. See sidebar for details.")
        return

    value_grid_datasets: Dict[str, pd.DataFrame] = {}
    for config in VALUE_GRID_CHART_CONFIGS:
        try:
            value_grid_datasets[config.label] = load_processed(config.dataset_key)
        except FileNotFoundError as exc:
            st.sidebar.error(str(exc))
            st.error("Missing processed dataset required for value grid charts.")
            return

    render_sidebar()

    active_section = st.session_state["active_section"]
    active_chart = (
        st.session_state["value_grid_chart"]
        if active_section == VALUE_GRID_SECTION
        else st.session_state["pell_chart"]
    )
    render_main(active_section, active_chart, value_grid_datasets, pell_df)


if __name__ == "__main__":
    main()
