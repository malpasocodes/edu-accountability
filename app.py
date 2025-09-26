"""Streamlit Phase 1 skeleton with structured sidebar sections."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st

from src.charts.cost_vs_grad_chart import render_cost_vs_grad_scatter
from src.charts.loan_top_dollars_chart import render_loan_top_dollars_chart
from src.charts.loan_vs_grad_scatter_chart import render_loan_vs_grad_scatter
from src.data.datasets import load_processed
from src.ui.renderers import render_dataframe
from src.charts.pell_top_dollars_chart import render_pell_top_dollars_chart
from src.charts.pell_vs_grad_scatter_chart import render_pell_vs_grad_scatter
from src.charts.pell_trend_chart import render_pell_trend_chart

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PELL_SOURCE = DATA_DIR / "raw" / "pelltotals.csv"
LOAN_SOURCE = DATA_DIR / "raw" / "loantotals.csv"
PELL_TOP_DOLLARS_SOURCE = DATA_DIR / "processed" / "pell_top_dollars.csv"
PELL_TOP_DOLLARS_FOUR_SOURCE = DATA_DIR / "processed" / "pell_top_dollars_four_year.csv"
PELL_TOP_DOLLARS_TWO_SOURCE = DATA_DIR / "processed" / "pell_top_dollars_two_year.csv"
PELL_TOP_DOLLARS_TREND_FOUR_SOURCE = DATA_DIR / "processed" / "pell_top_dollars_trend_four_year.csv"
PELL_TOP_DOLLARS_TREND_TWO_SOURCE = DATA_DIR / "processed" / "pell_top_dollars_trend_two_year.csv"
PELL_VS_GRAD_SOURCE = DATA_DIR / "processed" / "pell_vs_grad_scatter.csv"
PELL_VS_GRAD_FOUR_SOURCE = DATA_DIR / "processed" / "pell_vs_grad_scatter_four_year.csv"
PELL_VS_GRAD_TWO_SOURCE = DATA_DIR / "processed" / "pell_vs_grad_scatter_two_year.csv"

OVERVIEW_SECTION = "Project Overview"
VALUE_GRID_SECTION = "College Value Grid"
FEDERAL_LOANS_SECTION = "Federal Loans"
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
FOUR_YEAR_VALUE_GRID_LABEL = VALUE_GRID_CHART_CONFIGS[0].label
TWO_YEAR_VALUE_GRID_LABEL = VALUE_GRID_CHART_CONFIGS[1].label

PELL_TOP_DOLLARS_FOUR_LABEL = "Top 25 Pell Dollar Recipients (4-year)"
PELL_TOP_DOLLARS_TWO_LABEL = "Top 25 Pell Dollar Recipients (2-year)"
PELL_VS_GRAD_FOUR_LABEL = "Pell Dollars vs Graduation Rate (4-year)"
PELL_VS_GRAD_TWO_LABEL = "Pell Dollars vs Graduation Rate (2-year)"
PELL_TREND_FOUR_LABEL = "Pell Dollars Trend (4-year)"
PELL_TREND_TWO_LABEL = "Pell Dollars Trend (2-year)"
PELL_CHARTS = [
    PELL_TOP_DOLLARS_FOUR_LABEL,
    PELL_TOP_DOLLARS_TWO_LABEL,
    PELL_VS_GRAD_FOUR_LABEL,
    PELL_VS_GRAD_TWO_LABEL,
    PELL_TREND_FOUR_LABEL,
    PELL_TREND_TWO_LABEL,
]

LOAN_TOP_DOLLARS_FOUR_LABEL = "Top 25 Federal Loan Dollars (4-year)"
LOAN_TOP_DOLLARS_TWO_LABEL = "Top 25 Federal Loan Dollars (2-year)"
LOAN_VS_GRAD_FOUR_LABEL = "Federal Loans vs Graduation Rate (4-year)"
LOAN_VS_GRAD_TWO_LABEL = "Federal Loans vs Graduation Rate (2-year)"
LOAN_CHARTS = [
    LOAN_TOP_DOLLARS_FOUR_LABEL,
    LOAN_TOP_DOLLARS_TWO_LABEL,
    LOAN_VS_GRAD_FOUR_LABEL,
    LOAN_VS_GRAD_TWO_LABEL,
]


def _init_session_state() -> None:
    defaults: Dict[str, str] = {
        "active_section": OVERVIEW_SECTION,
        "value_grid_chart": VALUE_GRID_CHARTS[0],
        "loan_chart": LOAN_CHARTS[0],
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
def load_loan_dataset(path_str: str) -> pd.DataFrame:
    """Load the federal loan totals dataset."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Loan dataset not found at {path}.")
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_pell_top_dollars_dataset(path_str: str) -> pd.DataFrame:
    """Load the processed Pell top dollars dataset."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Pell top dollars dataset not found at {path}.")
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_pell_vs_grad_dataset(path_str: str) -> pd.DataFrame:
    """Load the processed Pell vs graduation dataset."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Pell vs graduation dataset not found at {path}.")
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_pell_trend_dataset(path_str: str) -> pd.DataFrame:
    """Load the processed Pell trend dataset."""
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"Pell trend dataset not found at {path}.")
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


def render_overview() -> None:
    """Display the landing page with project context and navigation tips."""

    st.title("College Value Explorer")
    st.caption(
        "A data-first dashboard built from IPEDS extracts to track affordability, outcomes, "
        "and Pell Grant momentum across U.S. colleges."
    )
    st.markdown(
        """
        This project aggregates canonical IPEDS releases into reproducible datasets and charts so
        educators, journalists, and policy partners can evaluate how institutions balance costs,
        completion, and Pell Grant support.
        """
    )
    st.markdown(
        """
        **How to use the dashboard**

        - Choose **College Value Grid** to compare net price against graduation outcomes for four-year and two-year institutions.
        - Review **Federal Loans** to see which institutions draw the largest federal loan volumes.
        - Open **Pell Grants** to review award concentrations, multi-year trends, and outcome relationships.
        - Regenerate or extend datasets with the scripts in `data/processed/` and explore raw pulls in `data/raw/` to keep analyses reproducible.
        """
    )
    st.markdown(
        """
        Use the navigation sidebar to switch between sections. Each chart module lives under `src/`, mirrored by tests in `tests/`, so you can extend the dashboard with new visuals that share the same data pipeline.
        """
    )


def render_sidebar() -> None:
    sidebar = st.sidebar
    sidebar.title("Navigation")

    active_section = sidebar.radio(
        "Explore",
        [OVERVIEW_SECTION, VALUE_GRID_SECTION, FEDERAL_LOANS_SECTION, PELL_SECTION],
        key="active_section",
    )

    if active_section == VALUE_GRID_SECTION:
        sidebar.radio(
            "Chart Type",
            VALUE_GRID_CHARTS,
            key="value_grid_chart",
            help="Switch between four-year and two-year value grid charts.",
        )
    elif active_section == FEDERAL_LOANS_SECTION:
        sidebar.radio(
            "Chart Type",
            LOAN_CHARTS,
            key="loan_chart",
            help="Select a federal loan view to explore.",
        )
    elif active_section == PELL_SECTION:
        sidebar.radio(
            "Chart Type",
            PELL_CHARTS,
            key="pell_chart",
            help="Select a Pell grant view to explore.",
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
    active_chart: str | None,
    value_grid_datasets: Dict[str, pd.DataFrame],
    loan_df: pd.DataFrame,
    pell_df: pd.DataFrame,
    pell_resources: Dict[str, pd.DataFrame | None],
) -> None:
    if active_section == OVERVIEW_SECTION:
        render_overview()
        return

    if not active_chart:
        st.info("Select a chart from the sidebar to begin exploring the data.")
        return

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
    elif active_section == FEDERAL_LOANS_SECTION:
        if loan_df.empty:
            st.warning(
                "Loan dataset is unavailable. Confirm `data/raw/loantotals.csv` exists and reload."
            )
            return
        if active_chart == LOAN_TOP_DOLLARS_FOUR_LABEL:
            metadata = value_grid_datasets.get(FOUR_YEAR_VALUE_GRID_LABEL)
            if metadata is not None:
                render_loan_top_dollars_chart(
                    loan_df,
                    metadata,
                    top_n=25,
                    title=LOAN_TOP_DOLLARS_FOUR_LABEL,
                )
            else:
                st.error("Missing metadata for four-year institutions.")
        elif active_chart == LOAN_TOP_DOLLARS_TWO_LABEL:
            metadata = value_grid_datasets.get(TWO_YEAR_VALUE_GRID_LABEL)
            if metadata is not None:
                render_loan_top_dollars_chart(
                    loan_df,
                    metadata,
                    top_n=25,
                    title=LOAN_TOP_DOLLARS_TWO_LABEL,
                )
            else:
                st.error("Missing metadata for two-year institutions.")
        elif active_chart == LOAN_VS_GRAD_FOUR_LABEL:
            metadata = value_grid_datasets.get(FOUR_YEAR_VALUE_GRID_LABEL)
            if metadata is not None:
                render_loan_vs_grad_scatter(
                    loan_df,
                    metadata,
                    title=LOAN_VS_GRAD_FOUR_LABEL,
                )
            else:
                st.error("Missing metadata for four-year institutions.")
        elif active_chart == LOAN_VS_GRAD_TWO_LABEL:
            metadata = value_grid_datasets.get(TWO_YEAR_VALUE_GRID_LABEL)
            if metadata is not None:
                render_loan_vs_grad_scatter(
                    loan_df,
                    metadata,
                    title=LOAN_VS_GRAD_TWO_LABEL,
                )
            else:
                st.error("Missing metadata for two-year institutions.")
    elif active_section == PELL_SECTION:
        if active_chart == PELL_TOP_DOLLARS_FOUR_LABEL:
            dataset = pell_resources.get("top_four")
            if dataset is not None:
                render_pell_top_dollars_chart(dataset, top_n=25, title=PELL_TOP_DOLLARS_FOUR_LABEL)
            else:
                st.warning(
                    "Missing processed dataset for four-year institutions. Run `python data/processed/build_pell_top_dollars.py` to regenerate."
                )
        elif active_chart == PELL_TOP_DOLLARS_TWO_LABEL:
            dataset = pell_resources.get("top_two")
            if dataset is not None:
                render_pell_top_dollars_chart(dataset, top_n=25, title=PELL_TOP_DOLLARS_TWO_LABEL)
            else:
                st.warning(
                    "Missing processed dataset for two-year institutions. Run `python data/processed/build_pell_top_dollars.py` to regenerate."
                )
        elif active_chart == PELL_VS_GRAD_FOUR_LABEL:
            dataset = pell_resources.get("scatter_four")
            if dataset is not None:
                render_pell_vs_grad_scatter(dataset, title=PELL_VS_GRAD_FOUR_LABEL)
            else:
                st.warning(
                    "Pell vs graduation dataset (4-year) not found. Run `python data/processed/build_pell_vs_grad_scatter.py` to generate it."
                )
        elif active_chart == PELL_VS_GRAD_TWO_LABEL:
            dataset = pell_resources.get("scatter_two")
            if dataset is not None:
                render_pell_vs_grad_scatter(dataset, title=PELL_VS_GRAD_TWO_LABEL)
            else:
                st.warning(
                    "Pell vs graduation dataset (2-year) not found. Run `python data/processed/build_pell_vs_grad_scatter.py` to generate it."
                )
        elif active_chart == PELL_TREND_FOUR_LABEL:
            dataset = pell_resources.get("trend_four")
            if dataset is not None:
                render_pell_trend_chart(dataset, title=PELL_TREND_FOUR_LABEL)
            else:
                st.warning(
                    "Pell trend dataset (4-year) not found. Run `python data/processed/build_pell_top_dollars.py` to regenerate."
                )
        elif active_chart == PELL_TREND_TWO_LABEL:
            dataset = pell_resources.get("trend_two")
            if dataset is not None:
                render_pell_trend_chart(dataset, title=PELL_TREND_TWO_LABEL)
            else:
                st.warning(
                    "Pell trend dataset (2-year) not found. Run `python data/processed/build_pell_top_dollars.py` to regenerate."
                )
        else:
            st.info(
                f"{active_chart} will be available in a later phase. Until then, preview the "
                "underlying Pell dataset below."
            )
            render_dataframe(pell_df.head(20), width="stretch")
    else:
        st.info("Section coming soon. In the meantime, review the available datasets below.")
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

    try:
        loan_df = load_loan_dataset(str(LOAN_SOURCE))
    except FileNotFoundError as exc:
        st.sidebar.error(str(exc))
        loan_df = pd.DataFrame()

    try:
        pell_top_dollars_all_df = load_pell_top_dollars_dataset(str(PELL_TOP_DOLLARS_SOURCE))
    except FileNotFoundError:
        pell_top_dollars_all_df = None

    try:
        pell_top_dollars_four_df = load_pell_top_dollars_dataset(str(PELL_TOP_DOLLARS_FOUR_SOURCE))
    except FileNotFoundError:
        pell_top_dollars_four_df = None

    try:
        pell_top_dollars_two_df = load_pell_top_dollars_dataset(str(PELL_TOP_DOLLARS_TWO_SOURCE))
    except FileNotFoundError:
        pell_top_dollars_two_df = None

    try:
        pell_trend_four_df = load_pell_trend_dataset(str(PELL_TOP_DOLLARS_TREND_FOUR_SOURCE))
    except FileNotFoundError:
        pell_trend_four_df = None

    try:
        pell_trend_two_df = load_pell_trend_dataset(str(PELL_TOP_DOLLARS_TREND_TWO_SOURCE))
    except FileNotFoundError:
        pell_trend_two_df = None

    try:
        pell_vs_grad_all_df = load_pell_vs_grad_dataset(str(PELL_VS_GRAD_SOURCE))
    except FileNotFoundError:
        pell_vs_grad_all_df = None

    try:
        pell_vs_grad_four_df = load_pell_vs_grad_dataset(str(PELL_VS_GRAD_FOUR_SOURCE))
    except FileNotFoundError:
        pell_vs_grad_four_df = None

    try:
        pell_vs_grad_two_df = load_pell_vs_grad_dataset(str(PELL_VS_GRAD_TWO_SOURCE))
    except FileNotFoundError:
        pell_vs_grad_two_df = None

    value_grid_datasets: Dict[str, pd.DataFrame] = {}

    pell_resources: Dict[str, pd.DataFrame | None] = {
        "raw": pell_df,
        "top_all": pell_top_dollars_all_df,
        "top_four": pell_top_dollars_four_df,
        "top_two": pell_top_dollars_two_df,
        "trend_four": pell_trend_four_df,
        "trend_two": pell_trend_two_df,
        "scatter_all": pell_vs_grad_all_df,
        "scatter_four": pell_vs_grad_four_df,
        "scatter_two": pell_vs_grad_two_df,
    }
    for config in VALUE_GRID_CHART_CONFIGS:
        try:
            value_grid_datasets[config.label] = load_processed(config.dataset_key)
        except FileNotFoundError as exc:
            st.sidebar.error(str(exc))
            st.error("Missing processed dataset required for value grid charts.")
            return

    render_sidebar()

    active_section = st.session_state["active_section"]
    if active_section == VALUE_GRID_SECTION:
        active_chart = st.session_state["value_grid_chart"]
    elif active_section == FEDERAL_LOANS_SECTION:
        active_chart = st.session_state["loan_chart"]
    elif active_section == PELL_SECTION:
        active_chart = st.session_state["pell_chart"]
    else:
        active_chart = None
    render_main(
        active_section,
        active_chart,
        value_grid_datasets,
        loan_df,
        pell_df,
        pell_resources,
    )


if __name__ == "__main__":
    main()
