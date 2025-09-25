"""Streamlit rendering utilities with backwards-compatible fallbacks."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


def render_altair_chart(chart: alt.Chart, *, width: str = "stretch") -> None:
    """Render an Altair chart while handling Streamlit API differences."""

    try:
        st.altair_chart(chart, width=width)
    except TypeError:
        st.altair_chart(chart, use_container_width=(width == "stretch"))


def render_dataframe(df: pd.DataFrame, *, width: str = "stretch") -> None:
    """Render a dataframe with compatibility fallbacks for Streamlit releases."""

    try:
        st.dataframe(df, width=width)
    except TypeError:
        st.dataframe(df, use_container_width=(width == "stretch"))
