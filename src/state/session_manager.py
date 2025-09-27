"""Session state management for the dashboard."""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st

from src.config.constants import DEFAULT_SESSION_STATE
from src.config.navigation import NavigationConfig


class SessionManager:
    """Manages Streamlit session state for the dashboard."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize session state with default values."""
        for key, value in DEFAULT_SESSION_STATE.items():
            st.session_state.setdefault(key, value)
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a value from session state.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to set
        """
        st.session_state[key] = value
    
    @staticmethod
    def get_active_section() -> str:
        """Get the currently active section."""
        return SessionManager.get("active_section", DEFAULT_SESSION_STATE["active_section"])
    
    @staticmethod
    def set_active_section(section: str) -> None:
        """Set the active section."""
        SessionManager.set("active_section", section)
    
    @staticmethod
    def get_active_chart(section_name: str) -> Optional[str]:
        """
        Get the active chart for a given section.
        
        Args:
            section_name: Name of the section
            
        Returns:
            Active chart name or None
        """
        section = NavigationConfig.get_section_by_name(section_name)
        if section and section.session_key:
            return SessionManager.get(section.session_key)
        return None
    
    @staticmethod
    def set_active_chart(section_name: str, chart_name: str) -> None:
        """
        Set the active chart for a given section.
        
        Args:
            section_name: Name of the section
            chart_name: Name of the chart
        """
        section = NavigationConfig.get_section_by_name(section_name)
        if section and section.session_key:
            SessionManager.set(section.session_key, chart_name)
    
    @staticmethod
    def is_section_active(section_name: str) -> bool:
        """
        Check if a section is currently active.
        
        Args:
            section_name: Name of the section
            
        Returns:
            True if the section is active
        """
        return SessionManager.get_active_section() == section_name