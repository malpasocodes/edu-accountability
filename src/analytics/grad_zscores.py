"""Utilities for computing graduation-rate z-scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

CANONICAL_VALUE_COLUMN = "grad_rate_150"

HEADCOUNT_THRESHOLDS: List[Dict[str, object]] = [
    {"label": "All institutions", "min_headcount": 0},
    {"label": "More than 1,000 full-time undergrads", "min_headcount": 1000},
    {"label": "More than 5,000 full-time undergrads", "min_headcount": 5000},
    {"label": "More than 10,000 full-time undergrads", "min_headcount": 10000},
]

HEADCOUNT_THRESHOLD_MAP: Dict[str, Dict[str, object]] = {
    cfg["label"]: cfg for cfg in HEADCOUNT_THRESHOLDS
}


@dataclass(frozen=True)
class PeerStats:
    """Summary statistics for a peer group."""

    year: int
    threshold_label: str
    min_headcount: int
    peer_count: int
    mean: float
    std: float
    median: float
    mad: float
    winsorized: bool


@dataclass(frozen=True)
class AnchorSummary:
    """Z-score context for a single institution."""

    unitid: int
    instnm: str
    year: int
    grad_rate: float | None
    headcount: float | None
    z_score: float | None
    z_score_robust: float | None
    percentile: float | None
    in_peer_group: bool
    headcount_source: str | None


def _winsorize_series(
    values: pd.Series, lower_pct: float = 1.0, upper_pct: float = 99.0
) -> Tuple[pd.Series, float, float]:
    """Winsorize a numeric series and return the clipped data and bounds."""

    clean = values.dropna()
    if clean.empty:
        return values.copy(), np.nan, np.nan

    lower = np.nanpercentile(clean, lower_pct)
    upper = np.nanpercentile(clean, upper_pct)
    clipped = values.clip(lower, upper)
    return clipped, lower, upper


def _prepare_year_frame(
    grad_long: pd.DataFrame,
    headcount_df: Optional[pd.DataFrame],
    year: int,
    fallback_series: Optional[pd.Series] = None,
) -> pd.DataFrame:
    """Subset canonical graduation data for a single year with headcounts."""

    if CANONICAL_VALUE_COLUMN not in grad_long.columns:
        raise KeyError(f"Canonical dataframe missing '{CANONICAL_VALUE_COLUMN}'.")

    year_df = grad_long[grad_long["year"] == year].copy()
    year_df = year_df.dropna(subset=[CANONICAL_VALUE_COLUMN])

    if headcount_df is not None and not headcount_df.empty:
        headcount_subset = headcount_df.copy()
        if "unitid" not in headcount_subset.columns:
            raise KeyError("Headcount dataframe requires a 'unitid' column.")

        headcount_subset["ft_ug_headcount"] = pd.to_numeric(
            headcount_subset.get("ft_ug_headcount"), errors="coerce"
        )

        merge_cols = ["unitid", "year", "ft_ug_headcount", "headcount_source"]
        fallback_col = "fallback_headcount" if "fallback_headcount" in headcount_subset.columns else None
        if fallback_col:
            merge_cols.append(fallback_col)

        merged = year_df.merge(
            headcount_subset[merge_cols],
            on=["unitid", "year"],
            how="left",
        )
    else:
        merged = year_df.copy()
        merged["ft_ug_headcount"] = np.nan
        merged["headcount_source"] = "missing"

    if "headcount_source" not in merged.columns:
        merged["headcount_source"] = np.where(
            merged["ft_ug_headcount"].notna(), "FT_UG_12M", "missing"
        )

    if fallback_series is not None:
        fallback_values = merged["unitid"].map(fallback_series)
        missing_mask = merged["ft_ug_headcount"].isna()
        merged.loc[missing_mask, "ft_ug_headcount"] = fallback_values[missing_mask]
        merged.loc[missing_mask, "headcount_source"] = np.where(
            fallback_values[missing_mask].notna(),
            "ENR_UG_FALL",
            merged.loc[missing_mask, "headcount_source"],
        )

    merged["ft_ug_headcount"] = merged["ft_ug_headcount"].fillna(0)
    return merged


def _percentile_from_distribution(
    distribution: Iterable[float], value: float | None
) -> float | None:
    """Estimate percentile placement for a value relative to a distribution."""

    if value is None or np.isnan(value):
        return None

    values = np.asarray([v for v in distribution if not np.isnan(v)], dtype=float)
    if values.size == 0:
        return None

    position = np.searchsorted(np.sort(values), value, side="right")
    percentile = (position / values.size) * 100
    return float(percentile)


def compute_peer_distribution(
    grad_long: pd.DataFrame,
    headcount_df: Optional[pd.DataFrame],
    *,
    year: int,
    threshold_label: str,
    winsorize: bool = False,
    fallback_series: Optional[pd.Series] = None,
) -> Tuple[pd.DataFrame, PeerStats, Tuple[float, float]]:
    """Return the peer dataframe and summary stats for a cohort year."""

    threshold_config = HEADCOUNT_THRESHOLD_MAP.get(threshold_label)
    if threshold_config is None:
        raise KeyError(f"Unknown threshold '{threshold_label}'.")

    min_headcount = int(threshold_config["min_headcount"])
    year_df = _prepare_year_frame(grad_long, headcount_df, year, fallback_series)
    peer_df = year_df[year_df["ft_ug_headcount"] >= min_headcount].copy()

    if peer_df.empty:
        raise ValueError("No peers available after applying the headcount filter.")

    calc_values, lower_bound, upper_bound = (
        _winsorize_series(peer_df[CANONICAL_VALUE_COLUMN])
        if winsorize
        else (peer_df[CANONICAL_VALUE_COLUMN], np.nan, np.nan)
    )
    peer_df["_calc_value"] = calc_values

    mean = float(peer_df["_calc_value"].mean())
    std = float(peer_df["_calc_value"].std(ddof=0))
    median = float(peer_df["_calc_value"].median())
    mad = float((peer_df["_calc_value"] - median).abs().median())

    if std == 0:
        peer_df["z_score"] = np.nan
    else:
        peer_df["z_score"] = (peer_df["_calc_value"] - mean) / std

    if mad == 0:
        peer_df["z_score_robust"] = np.nan
    else:
        peer_df["z_score_robust"] = 0.6745 * (
            peer_df["_calc_value"] - median
        ) / mad

    peer_df["percentile"] = (
        peer_df[CANONICAL_VALUE_COLUMN]
        .rank(method="average", pct=True)
        .astype(float)
        * 100
    )

    peer_df = peer_df.drop(columns=["_calc_value"])
    stats = PeerStats(
        year=year,
        threshold_label=threshold_label,
        min_headcount=min_headcount,
        peer_count=int(len(peer_df)),
        mean=mean,
        std=std,
        median=median,
        mad=mad,
        winsorized=winsorize,
    )
    return peer_df, stats, (lower_bound, upper_bound)


def summarize_anchor(
    grad_long: pd.DataFrame,
    headcount_df: Optional[pd.DataFrame],
    headcount_fallback: Optional[pd.Series] = None,
    *,
    unitid: int,
    year: int,
    threshold_label: str,
    robust: bool = False,
    winsorize: bool = False,
) -> Tuple[AnchorSummary, PeerStats, pd.DataFrame]:
    """Summarize z-score context for a single anchor institution."""

    year_df = _prepare_year_frame(grad_long, headcount_df, year, headcount_fallback)
    anchor_row = year_df[year_df["unitid"] == unitid].head(1)
    if anchor_row.empty:
        raise ValueError(f"UnitID {unitid} missing from canonical grad data.")

    peer_df, stats, bounds = compute_peer_distribution(
        grad_long,
        headcount_df,
        year=year,
        threshold_label=threshold_label,
        winsorize=winsorize,
        fallback_series=headcount_fallback,
    )
    min_headcount = stats.min_headcount
    anchor_in_peer_group = bool(
        anchor_row["ft_ug_headcount"].iloc[0] >= min_headcount
    )

    anchor_value = float(anchor_row[CANONICAL_VALUE_COLUMN].iloc[0])
    calc_value = anchor_value
    if winsorize and not np.isnan(bounds[0]) and not np.isnan(bounds[1]):
        calc_value = float(np.clip(calc_value, bounds[0], bounds[1]))

    z_score = (
        (calc_value - stats.mean) / stats.std if stats.std > 0 else np.nan
    )
    z_score_robust = (
        0.6745 * (calc_value - stats.median) / stats.mad
        if stats.mad > 0
        else np.nan
    )

    anchor_percentile = _percentile_from_distribution(
        peer_df[CANONICAL_VALUE_COLUMN], anchor_value
    )

    headcount_source = (
        str(anchor_row["headcount_source"].iloc[0])
        if "headcount_source" in anchor_row.columns
        else None
    )

    summary = AnchorSummary(
        unitid=int(unitid),
        instnm=str(anchor_row["instnm"].iloc[0]),
        year=year,
        grad_rate=anchor_value,
        headcount=float(anchor_row["ft_ug_headcount"].iloc[0])
        if pd.notna(anchor_row["ft_ug_headcount"].iloc[0])
        else None,
        z_score=float(z_score) if not np.isnan(z_score) else None,
        z_score_robust=float(z_score_robust)
        if not np.isnan(z_score_robust)
        else None,
        percentile=anchor_percentile,
        in_peer_group=anchor_in_peer_group,
        headcount_source=headcount_source,
    )

    if not robust:
        peer_df["z_score_active"] = peer_df["z_score"]
    else:
        peer_df["z_score_active"] = peer_df["z_score_robust"]

    return summary, stats, peer_df
