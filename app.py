"""Streamlit dashboard with modular architecture."""

from __future__ import annotations

import streamlit as st

from src.config.navigation import NavigationConfig
from src.config.constants import (
    OVERVIEW_SECTION,
    VALUE_GRID_SECTION,
    FEDERAL_LOANS_SECTION,
    PELL_SECTION,
    DISTANCE_EDUCATION_SECTION,
    COLLEGE_EXPLORER_SECTION,
    ROI_SECTION,
)
from src.core import DataManager, DataLoadError
from src.sections import (
    OverviewSection,
    ValueGridSection,
    FederalLoansSection,
    PellGrantsSection,
    DistanceEducationSection,
    CollegeExplorerSection,
    ROISection,
)
from src.state import SessionManager


def render_sidebar() -> None:
    """Render the navigation sidebar."""
    sidebar = st.sidebar
    sidebar.title("Navigation")
    
    # Home button
    if sidebar.button("🏠 Home", key="nav_home", use_container_width=True):
        SessionManager.set_active_section(OVERVIEW_SECTION)
    
    # Render each section
    for section_config in NavigationConfig.get_sections()[1:]:  # Skip overview
        is_active = SessionManager.is_section_active(section_config.name)
        
        with sidebar.expander(
            f"{section_config.icon} {section_config.label}", 
            expanded=is_active
        ):
            # Overview button for the section
            if st.button(
                section_config.overview_chart.label,
                key=section_config.overview_chart.key,
                use_container_width=True,
            ):
                SessionManager.set_active_section(section_config.name)
                if section_config.session_key:
                    SessionManager.set_active_chart(
                        section_config.name,
                        section_config.overview_chart.label
                    )
            
            # Chart buttons
            for chart in section_config.charts:
                if st.button(
                    chart.label,
                    key=chart.key,
                    use_container_width=True,
                ):
                    SessionManager.set_active_section(section_config.name)
                    if section_config.session_key:
                        SessionManager.set_active_chart(
                            section_config.name,
                            chart.label
                        )


def render_main(data_manager: DataManager) -> None:
    """
    Render the main content area.
    
    Args:
        data_manager: The data manager instance
    """
    active_section = SessionManager.get_active_section()
    
    # Create section instances
    sections = {
        OVERVIEW_SECTION: OverviewSection(data_manager),
        VALUE_GRID_SECTION: ValueGridSection(data_manager),
        FEDERAL_LOANS_SECTION: FederalLoansSection(data_manager),
        PELL_SECTION: PellGrantsSection(data_manager),
        DISTANCE_EDUCATION_SECTION: DistanceEducationSection(data_manager),
        COLLEGE_EXPLORER_SECTION: CollegeExplorerSection(data_manager),
        ROI_SECTION: ROISection(data_manager),
    }
    
    # Get the active section instance
    section = sections.get(active_section)
    if section is None:
        st.error(f"Unknown section: {active_section}")
        return
    
    # Get active chart for the section
    active_chart = SessionManager.get_active_chart(active_section)
    
    # Render the section
    if active_section == OVERVIEW_SECTION:
        section.render()
    else:
        if not active_chart:
            st.info("Select a chart from the sidebar to begin exploring the data.")
        else:
            section.render(active_chart)


def main() -> None:
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="College Value Explorer", 
        layout="wide"
    )
    
    # Initialize session state
    SessionManager.initialize()
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Load all data
    try:
        data_manager.load_all_data()
    except DataLoadError as e:
        st.error(f"Critical data loading error: {e}")
        st.stop()
    
    # Display any non-critical errors
    data_manager.display_errors()
    
    # Render UI
    render_sidebar()
    render_main(data_manager)


if __name__ == "__main__":
    main()