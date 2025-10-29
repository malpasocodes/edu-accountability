"""Disclaimer rendering utilities."""

from __future__ import annotations
from pathlib import Path
import streamlit as st


def load_disclaimer_content() -> str:
    """Load disclaimer content from DISCLAIMER.md file.

    Returns:
        str: The full disclaimer content, or error message if file not found.
    """
    disclaimer_path = Path(__file__).parent.parent.parent / "DISCLAIMER.md"
    if disclaimer_path.exists():
        return disclaimer_path.read_text()
    return "⚠️ Disclaimer content not available. Please contact the administrator."


def render_disclaimer_summary() -> None:
    """Render a brief disclaimer summary with expandable full text.

    This function displays a concise warning message with an expandable section
    containing the full legal disclaimer and terms of use from DISCLAIMER.md.
    """
    st.markdown('<h3 style="color: red;">⚠️ Important Notice</h3>', unsafe_allow_html=True)
    st.markdown(
        """
        The **EDU Accountability Lab** provides **research-oriented, non-commercial analyses** using public datasets such as IPEDS and the U.S. Census.
        All findings, metrics, and visualizations are **for informational and policy discussion purposes only** and **must not be used** to make enrollment, investment, or financial decisions about any institution or program.

        By accessing or using this site, you acknowledge that you have **read, understood, and accepted** the <span style="color: red;">Full Disclaimer & Terms of Use</span> (below), including all limitations of accuracy, liability, and applicability.
        If you do not agree with these terms, you should **discontinue use of the site immediately**.
        """,
        unsafe_allow_html=True
    )

    with st.expander("📄 View Full Disclaimer & Terms of Use"):
        disclaimer_content = load_disclaimer_content()
        st.markdown(disclaimer_content)
        st.markdown("---")
        st.markdown(
            """
            **By accessing or using this site, you acknowledge that you have read, understood,
            and accepted these terms.** If you do not agree with these terms, you should discontinue
            use of the site immediately.
            """
        )


def render_disclaimer_footer() -> None:
    """Render a compact disclaimer footer for section pages.

    This provides a minimal reminder with link back to full disclaimer.
    Useful for adding to the bottom of analytical sections.
    """
    st.markdown("---")
    st.caption(
        "⚠️ **Beta Notice**: All data is for research purposes only. "
        "See Overview page for full disclaimer."
    )
