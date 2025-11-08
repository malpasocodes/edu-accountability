"""Tests for graduation z-score utilities."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.grad_zscores import (
    HEADCOUNT_THRESHOLDS,
    summarize_anchor,
)


def _build_grad_df() -> pd.DataFrame:
    """Helper to create a canonical-like dataframe."""

    data = {
        "unitid": [1, 2, 3, 4],
        "year": [2023, 2023, 2023, 2023],
        "instnm": ["Alpha", "Beta", "Gamma", "Delta"],
        "grad_rate_150": [50.0, 60.0, 70.0, 80.0],
        "control": ["Public"] * 4,
        "level": ["4-year"] * 4,
        "state": ["AA"] * 4,
        "sector": ["Public, 4-year or above"] * 4,
        "source_flag": ["DRVGR"] * 4,
        "is_revised": [False] * 4,
        "cohort_reference": ["2023 cohort"] * 4,
        "load_ts": pd.Timestamp("2025-01-01"),
    }
    return pd.DataFrame(data)


def _build_headcount_df() -> pd.DataFrame:
    """Helper for enrollment-based headcounts."""

    return pd.DataFrame(
        {
            "unitid": [1, 2, 3, 4],
            "year": [2023, 2023, 2023, 2023],
            "ft_ug_headcount": [800, 1500, 5500, 15000],
            "headcount_source": ["FT_UG_12M"] * 4,
        }
    )


def test_summarize_anchor_returns_metrics_for_peer_group():
    grad_df = _build_grad_df()
    headcount_df = _build_headcount_df()
    fallback = pd.Series({idx: val for idx, val in zip(headcount_df["unitid"], headcount_df["ft_ug_headcount"])})

    summary, stats, peers = summarize_anchor(
        grad_df,
        headcount_df,
        headcount_fallback=fallback,
        unitid=4,
        year=2023,
        threshold_label=HEADCOUNT_THRESHOLDS[1]["label"],
        robust=False,
        winsorize=False,
    )

    assert summary.unitid == 4
    assert pytest.approx(summary.grad_rate, rel=1e-5) == 80.0
    assert summary.in_peer_group is True
    assert stats.peer_count == 3  # filters out headcount below 1,000
    assert "z_score" in peers.columns
    assert peers["z_score"].notna().all()


def test_anchor_below_threshold_still_returns_zscore():
    grad_df = _build_grad_df()
    headcount_df = _build_headcount_df()
    fallback = pd.Series({idx: val for idx, val in zip(headcount_df["unitid"], headcount_df["ft_ug_headcount"])})

    summary, stats, _ = summarize_anchor(
        grad_df,
        headcount_df,
        headcount_fallback=fallback,
        unitid=1,
        year=2023,
        threshold_label=HEADCOUNT_THRESHOLDS[2]["label"],
        robust=True,
        winsorize=False,
    )

    assert summary.in_peer_group is False
    assert summary.z_score is not None
    assert stats.min_headcount == 5000


def test_winsorization_handles_extreme_values():
    grad_df = _build_grad_df()
    grad_df.loc[3, "grad_rate_150"] = 100.0  # extreme
    headcount_df = _build_headcount_df()
    fallback = pd.Series({idx: val for idx, val in zip(headcount_df["unitid"], headcount_df["ft_ug_headcount"])})

    summary, stats, _ = summarize_anchor(
        grad_df,
        headcount_df,
        headcount_fallback=fallback,
        unitid=4,
        year=2023,
        threshold_label=HEADCOUNT_THRESHOLDS[0]["label"],
        winsorize=True,
    )

    assert stats.winsorized is True
    assert summary.z_score is not None
