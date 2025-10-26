"""Streamlit rendering utilities."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st


def render_altair_chart(chart: alt.Chart, *, width: str = "stretch") -> None:
    """Render an Altair chart with Streamlit width parameter."""
    st.altair_chart(chart, width=width)


def render_dataframe(df: pd.DataFrame, *, width: str = "stretch") -> None:
    """Render a dataframe with Streamlit width parameter."""
    st.dataframe(df, width=width)
