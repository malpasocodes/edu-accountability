"""Verification tests pinning the Pell ranking window and rate consistency.

The Substack accountability series (Part IIa) counts Pell dollars over the
documented decade — award years 2013-2022, the window covered by the COD
Direct Loan reports. These tests keep the processed Pell datasets on that
window, keep the Pell scatter's graduation rates in lockstep with the
value-grid GRS rates (so the dashboard cannot show two different Phoenix
rates again), and pin the essay's ranking claims against the raw Pell file.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PELL_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "fsa" / "pelltotals.csv"

SCATTER_PATHS = [
    PROCESSED_DIR / "pell_vs_grad_scatter.csv",
    PROCESSED_DIR / "pell_vs_grad_scatter_four_year.csv",
    PROCESSED_DIR / "pell_vs_grad_scatter_two_year.csv",
]
TOP_DOLLARS_PATHS = [
    PROCESSED_DIR / "pell_top_dollars.csv",
    PROCESSED_DIR / "pell_top_dollars_four_year.csv",
    PROCESSED_DIR / "pell_top_dollars_two_year.csv",
]
VALUE_GRID_PATH = PROCESSED_DIR / "tuition_vs_graduation.csv"

PHOENIX_UNITID = 484613
NORTHRIDGE_UNITID = 110608
DECADE_LABEL = "2013-2022"
DECADE_YEAR_COLUMNS = [f"YR{year}" for year in range(2013, 2023)]

# Pinned figures — cited in the essay.
PHOENIX_DECADE_PELL = 2_099_633_987
NORTHRIDGE_NATIONAL_PELL_RANK = 10  # "tenth-largest recipient of Pell Grants"


def _load(path: Path) -> pd.DataFrame:
    if not path.exists():
        pytest.skip(f"{path.name} missing — regenerate the processed Pell datasets")
    return pd.read_csv(path)


@pytest.mark.parametrize(
    "path", SCATTER_PATHS + TOP_DOLLARS_PATHS, ids=lambda p: p.name
)
def test_pell_rankings_cover_the_documented_decade(path: Path) -> None:
    frame = _load(path)
    assert set(frame["YearsCovered"].unique()) == {DECADE_LABEL}


def test_phoenix_scatter_rate_matches_value_grid() -> None:
    scatter = _load(PROCESSED_DIR / "pell_vs_grad_scatter_four_year.csv")
    value_grid = _load(VALUE_GRID_PATH)
    scatter_rate = scatter.loc[
        scatter["UnitID"] == PHOENIX_UNITID, "GraduationRate"
    ].iloc[0]
    grid_rate = value_grid.loc[
        value_grid["UnitID"] == PHOENIX_UNITID, "graduation_rate"
    ].iloc[0]
    assert scatter_rate == pytest.approx(grid_rate)


def test_phoenix_decade_pell_total_in_scatter() -> None:
    scatter = _load(PROCESSED_DIR / "pell_vs_grad_scatter_four_year.csv")
    phoenix = scatter[scatter["UnitID"] == PHOENIX_UNITID]
    assert int(phoenix["PellDollars"].iloc[0]) == PHOENIX_DECADE_PELL


def test_phoenix_ranks_first_in_pell_top_dollars() -> None:
    top = _load(PROCESSED_DIR / "pell_top_dollars.csv")
    assert int(top.loc[top["rank"] == 1, "UnitID"].iloc[0]) == PHOENIX_UNITID


def test_northridge_national_pell_rank_over_documented_decade() -> None:
    if not PELL_RAW_PATH.exists():
        pytest.skip("pelltotals.csv missing")
    pell = pd.read_csv(PELL_RAW_PATH)
    columns = [c for c in DECADE_YEAR_COLUMNS if c in pell.columns]
    totals = (
        pell.assign(total=pell[columns].sum(axis=1))
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )
    rank = totals.index[totals["UnitID"] == NORTHRIDGE_UNITID][0] + 1
    assert rank == NORTHRIDGE_NATIONAL_PELL_RANK
    assert int(totals.loc[0, "UnitID"]) == PHOENIX_UNITID
