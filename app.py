"""Streamlit entry point for the College ACT chart dashboard."""

from __future__ import annotations

import streamlit as st

from src.data.datasets import load_processed
from src.dashboard.cost_vs_grad import render_dashboard


def main() -> None:
    st.set_page_config(page_title="College ACT Charts", layout="wide")
    st.title("College Accountability Dashboard")
    st.caption("Explore tuition, enrollment, and outcomes across institutions.")

    try:
        data = load_processed("cost_vs_grad")
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    render_dashboard(data)


if __name__ == "__main__":
    main()
