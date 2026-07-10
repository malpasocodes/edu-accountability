"""Verification tests pinning the FSA Direct Loan volume dataset.

These assertions freeze the figures cited in the Substack accountability
series (Part II) against the processed dataset built by
``src.data.build_fsa_loan_volume`` from FSA's official Title IV volume
reports (COD system). If the raw workbooks, the parser, or the processed
files drift, these tests fail before the published numbers do.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "fsa_dl_volume.parquet"
PELL_PATH = PROJECT_ROOT / "data" / "raw" / "fsa" / "pelltotals.csv"

PHOENIX_OPEID = "02098800"
WALDEN_OPEID = "02504200"
DECADE_YEARS = list(range(2013, 2023))  # award years 2012-13 .. 2021-22

UNDERGRAD_LOAN_TYPES = {"subsidized", "unsub_undergrad", "parent_plus"}
GRADUATE_LOAN_TYPES = {"unsub_grad", "grad_plus"}

# Pinned figures (whole dollars) — cited in the essay.
PHOENIX_DECADE_LOANS = 11_108_326_427
PHOENIX_DECADE_LOANS_UNDERGRAD = 8_076_997_621
PHOENIX_DECADE_LOANS_GRADUATE = 3_031_328_806
PHOENIX_DECADE_PELL = 2_099_633_987
WALDEN_DECADE_LOANS = 7_988_029_201


@pytest.fixture(scope="module")
def dl_volume() -> pd.DataFrame:
    if not PARQUET_PATH.exists():
        pytest.skip(
            "fsa_dl_volume.parquet missing — run "
            "`python -m src.data.build_fsa_loan_volume`"
        )
    return pd.read_parquet(PARQUET_PATH)


@pytest.fixture(scope="module")
def phoenix(dl_volume: pd.DataFrame) -> pd.DataFrame:
    return dl_volume[dl_volume["opeid"] == PHOENIX_OPEID]


def test_covers_the_decade_with_all_loan_types(dl_volume: pd.DataFrame) -> None:
    assert sorted(dl_volume["year"].dropna().unique()) == DECADE_YEARS
    assert set(dl_volume["loan_type"].unique()) == (
        UNDERGRAD_LOAN_TYPES | GRADUATE_LOAN_TYPES
    )


def test_phoenix_decade_loan_total(phoenix: pd.DataFrame) -> None:
    assert int(phoenix["disbursed_usd"].sum()) == PHOENIX_DECADE_LOANS


def test_phoenix_undergrad_graduate_split(phoenix: pd.DataFrame) -> None:
    by_type = phoenix.groupby("loan_type", observed=True)["disbursed_usd"].sum()
    undergrad = int(by_type[by_type.index.isin(UNDERGRAD_LOAN_TYPES)].sum())
    graduate = int(by_type[by_type.index.isin(GRADUATE_LOAN_TYPES)].sum())

    assert undergrad == PHOENIX_DECADE_LOANS_UNDERGRAD
    assert graduate == PHOENIX_DECADE_LOANS_GRADUATE
    # "Roughly three of every four loan dollars were undergraduate borrowing."
    assert undergrad / (undergrad + graduate) == pytest.approx(0.727, abs=0.005)


def test_phoenix_is_largest_loan_recipient(dl_volume: pd.DataFrame) -> None:
    decade_totals = (
        dl_volume.groupby("opeid")["disbursed_usd"].sum().sort_values(ascending=False)
    )
    assert decade_totals.index[0] == PHOENIX_OPEID
    assert decade_totals.index[1] == WALDEN_OPEID
    assert int(decade_totals.iloc[1]) == WALDEN_DECADE_LOANS


def test_phoenix_decade_pell_total() -> None:
    pell = pd.read_csv(PELL_PATH)
    row = pell[pell["UnitID"] == 484613]
    total = int(row[[f"YR{year}" for year in DECADE_YEARS]].sum(axis=1).iloc[0])
    assert total == PHOENIX_DECADE_PELL
    # Combined loans + Pell — the essay's headline figure (~$13.2B).
    assert PHOENIX_DECADE_LOANS + total == 13_207_960_414
