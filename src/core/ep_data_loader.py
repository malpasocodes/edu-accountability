"""
Earnings Premium data loading and caching functions.

Provides cached data loading for the EP Analysis section with helper
functions for filtering and lookups.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any


# Data version for cache invalidation
EP_DATA_VERSION = "ep_v1_real"


@st.cache_data(ttl=3600, show_spinner="Loading Earnings Premium data...")
def load_ep_data() -> pd.DataFrame:
    """
    Load processed EP analysis data from Parquet file.

    Cached for 1 hour to improve performance.

    Returns:
        DataFrame with all EP analysis columns including:
        - UnitID, institution, STABBR, sector_name
        - median_earnings, Threshold, earnings_margin, earnings_margin_pct
        - risk_level, risk_level_numeric
        - MD_EARN_WNE_P10, MD_EARN_WNE_P6
        - SECTOR, enrollment, graduation_rate, cost

    Raises:
        FileNotFoundError: If EP data file doesn't exist
    """
    base_dir = Path(__file__).parent.parent.parent
    data_path = base_dir / "data" / "processed" / "ep_analysis.parquet"

    if not data_path.exists():
        st.error(f"EP data file not found: {data_path}")
        st.info("Please run: python src/data/build_ep_metrics.py")
        st.stop()

    df = pd.read_parquet(data_path)
    return df


@st.cache_data(ttl=3600)
def load_state_thresholds() -> Dict[str, float]:
    """
    Load state threshold lookup table.

    Returns:
        Dictionary mapping state abbreviation to threshold amount
        Example: {'CA': 32476, 'NY': 30793, ...}
    """
    base_dir = Path(__file__).parent.parent.parent
    threshold_path = base_dir / "data" / "raw" / "ep_thresholds" / "state_thresholds_2024.csv"

    df = pd.read_csv(threshold_path)

    # Create state abbreviation mapping
    state_abbr_map = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
        'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
        'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
        'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
        'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
        'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'United States (National)': 'US'
    }

    df['STABBR'] = df['State'].map(state_abbr_map)
    return df.set_index('STABBR')['Threshold'].to_dict()


@st.cache_data(ttl=3600)
def get_risk_summary() -> Dict[str, Any]:
    """
    Get cached risk summary statistics.

    Returns:
        Dictionary with summary metrics:
        - total_institutions: Total count
        - at_risk_count: High + Critical risk count
        - critical_count: Critical risk only count
        - avg_margin: Average earnings margin percentage
        - risk_distribution: Dictionary of risk level counts
    """
    df = load_ep_data()
    df_valid = df[df['risk_level'] != 'No Data'].copy()

    summary = {
        'total_institutions': len(df_valid),
        'at_risk_count': len(df_valid[df_valid['risk_level'].isin(['High Risk', 'Critical Risk'])]),
        'critical_count': len(df_valid[df_valid['risk_level'] == 'Critical Risk']),
        'avg_margin': df_valid['earnings_margin_pct'].mean(),
        'risk_distribution': df_valid['risk_level'].value_counts().to_dict()
    }

    return summary


def get_institution_by_unitid(unitid: int) -> Optional[pd.Series]:
    """
    Look up a single institution by UnitID.

    Args:
        unitid: IPEDS Unit ID

    Returns:
        Series with institution data, or None if not found
    """
    df = load_ep_data()
    result = df[df['UnitID'] == unitid]

    if result.empty:
        return None

    return result.iloc[0]


def get_institution_by_name(name: str) -> Optional[pd.Series]:
    """
    Look up a single institution by exact name match.

    Args:
        name: Institution name (case-insensitive)

    Returns:
        Series with institution data, or None if not found
    """
    df = load_ep_data()
    result = df[df['institution'].str.lower() == name.lower()]

    if result.empty:
        return None

    return result.iloc[0]


def search_institutions(query: str, limit: int = 10) -> pd.DataFrame:
    """
    Search for institutions by partial name match.

    Args:
        query: Search term (case-insensitive)
        limit: Maximum number of results to return

    Returns:
        DataFrame of matching institutions
    """
    df = load_ep_data()

    # Case-insensitive partial match
    mask = df['institution'].str.contains(query, case=False, na=False)
    results = df[mask].head(limit)

    return results


def filter_by_risk_level(risk_levels: list[str]) -> pd.DataFrame:
    """
    Filter institutions by risk level(s).

    Args:
        risk_levels: List of risk levels to include
            Options: 'Low Risk', 'Moderate Risk', 'High Risk', 'Critical Risk', 'No Data'

    Returns:
        Filtered DataFrame
    """
    df = load_ep_data()
    return df[df['risk_level'].isin(risk_levels)]


def filter_by_sector(sectors: list[str]) -> pd.DataFrame:
    """
    Filter institutions by sector(s).

    Args:
        sectors: List of sector names to include
            Options: 'Public 4-year', 'Private nonprofit 4-year', 'For-profit 4-year',
                    'Public 2-year', 'Private nonprofit 2-year', 'For-profit 2-year'

    Returns:
        Filtered DataFrame
    """
    df = load_ep_data()
    return df[df['sector_name'].isin(sectors)]


def filter_by_state(states: list[str]) -> pd.DataFrame:
    """
    Filter institutions by state(s).

    Args:
        states: List of state abbreviations (e.g., ['CA', 'NY', 'TX'])

    Returns:
        Filtered DataFrame
    """
    df = load_ep_data()
    return df[df['STABBR'].isin(states)]


def get_peer_institutions(
    institution: pd.Series,
    n_peers: int = 5,
    same_state: bool = True,
    same_sector: bool = True
) -> pd.DataFrame:
    """
    Find peer institutions similar to the given institution.

    Peers are defined as institutions in the same state and sector,
    ranked by enrollment similarity.

    Args:
        institution: Institution Series (from get_institution_by_unitid or similar)
        n_peers: Number of peer institutions to return
        same_state: If True, only return institutions in same state
        same_sector: If True, only return institutions in same sector

    Returns:
        DataFrame of peer institutions, sorted by similarity
    """
    df = load_ep_data()

    # Exclude the institution itself
    peers = df[df['UnitID'] != institution['UnitID']].copy()

    # Filter by state if requested
    if same_state and pd.notna(institution['STABBR']):
        peers = peers[peers['STABBR'] == institution['STABBR']]

    # Filter by sector if requested
    if same_sector and pd.notna(institution['sector_name']):
        peers = peers[peers['sector_name'] == institution['sector_name']]

    # Remove institutions with no data
    peers = peers[peers['risk_level'] != 'No Data']

    if peers.empty:
        return pd.DataFrame()

    # Sort by enrollment similarity if enrollment is available
    if pd.notna(institution['enrollment']) and 'enrollment' in peers.columns:
        peers['enrollment_diff'] = abs(peers['enrollment'] - institution['enrollment'])
        peers = peers.nsmallest(n_peers, 'enrollment_diff')
        peers = peers.drop(columns=['enrollment_diff'])
    else:
        # If no enrollment data, just return first n_peers
        peers = peers.head(n_peers)

    # Sort by median earnings (descending) for display
    peers = peers.sort_values('median_earnings', ascending=False, na_position='last')

    return peers


def get_state_summary(state_abbr: str) -> Dict[str, Any]:
    """
    Get summary statistics for a specific state.

    Args:
        state_abbr: State abbreviation (e.g., 'CA')

    Returns:
        Dictionary with state-level statistics:
        - state_threshold: State's EP threshold
        - total_institutions: Count of institutions in state
        - risk_distribution: Dictionary of risk level counts
        - median_earnings: Median institutional earnings in state
        - avg_margin: Average earnings margin in state
    """
    df = load_ep_data()
    state_df = df[df['STABBR'] == state_abbr]

    if state_df.empty:
        return None

    # Get state threshold
    thresholds = load_state_thresholds()
    state_threshold = thresholds.get(state_abbr, None)

    # Calculate statistics
    state_df_valid = state_df[state_df['risk_level'] != 'No Data']

    summary = {
        'state_threshold': state_threshold,
        'total_institutions': len(state_df),
        'risk_distribution': state_df['risk_level'].value_counts().to_dict(),
        'median_earnings': state_df_valid['median_earnings'].median() if not state_df_valid.empty else None,
        'avg_margin': state_df_valid['earnings_margin_pct'].mean() if not state_df_valid.empty else None
    }

    return summary


def get_sector_summary(sector_name: str) -> Dict[str, Any]:
    """
    Get summary statistics for a specific sector.

    Args:
        sector_name: Sector name (e.g., 'Public 4-year')

    Returns:
        Dictionary with sector-level statistics
    """
    df = load_ep_data()
    sector_df = df[df['sector_name'] == sector_name]

    if sector_df.empty:
        return None

    sector_df_valid = sector_df[sector_df['risk_level'] != 'No Data']

    summary = {
        'total_institutions': len(sector_df),
        'risk_distribution': sector_df['risk_level'].value_counts().to_dict(),
        'median_earnings': sector_df_valid['median_earnings'].median() if not sector_df_valid.empty else None,
        'avg_margin': sector_df_valid['earnings_margin_pct'].mean() if not sector_df_valid.empty else None,
        'at_risk_pct': (len(sector_df_valid[sector_df_valid['risk_level'].isin(['High Risk', 'Critical Risk'])]) /
                        len(sector_df_valid) * 100) if not sector_df_valid.empty else None
    }

    return summary


@st.cache_data(ttl=3600)
def get_national_summary() -> Dict[str, Any]:
    """
    Get national summary statistics for comparison.

    Returns:
        Dictionary with national statistics:
        - national_threshold: National EP threshold
        - total_institutions: Count of all institutions
        - risk_distribution: Dictionary of risk level counts
        - median_earnings: National median institutional earnings
        - avg_margin: National average earnings margin
        - at_risk_pct: Percentage at risk nationally
    """
    df = load_ep_data()
    df_valid = df[df['risk_level'] != 'No Data']

    # Get national threshold
    thresholds = load_state_thresholds()
    national_threshold = thresholds.get('US', None)

    at_risk_count = len(df_valid[df_valid['risk_level'].isin(['High Risk', 'Critical Risk'])])
    at_risk_pct = (at_risk_count / len(df_valid) * 100) if not df_valid.empty else None

    summary = {
        'national_threshold': national_threshold,
        'total_institutions': len(df_valid),
        'risk_distribution': df_valid['risk_level'].value_counts().to_dict(),
        'median_earnings': df_valid['median_earnings'].median(),
        'avg_margin': df_valid['earnings_margin_pct'].mean(),
        'at_risk_pct': at_risk_pct
    }

    return summary


def get_all_sectors() -> list[str]:
    """
    Get list of all unique sectors in the data.

    Returns:
        List of sector names
    """
    df = load_ep_data()
    sectors = df['sector_name'].dropna().unique().tolist()
    return sorted(sectors)


def get_all_states() -> list[str]:
    """
    Get list of all unique states in the data.

    Returns:
        List of state abbreviations, sorted alphabetically
    """
    df = load_ep_data()
    states = df['STABBR'].dropna().unique().tolist()
    return sorted(states)
