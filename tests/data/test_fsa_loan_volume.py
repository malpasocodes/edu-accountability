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

# National context figures (all schools, 2013-2022) — cited in the essay.
NATIONAL_DECADE_LOANS = 928_266_080_852
NATIONAL_DECADE_LOANS_UNDERGRAD = 558_546_771_192  # incl. Parent PLUS; 60.2%
NATIONAL_DECADE_PELL = 253_396_137_190

PENN_STATE_OPEID = "00332900"
PENN_STATE_DECADE_LOANS_UNDERGRAD = 4_430_838_491  # runner-up to Phoenix


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


def test_wide_unitid_file_matches_pinned_figures() -> None:
    """The dashboard's UnitID-keyed wide file must agree with the tidy dataset."""
    wide_path = PROJECT_ROOT / "data" / "processed" / "loan_totals_cod.csv"
    if not wide_path.exists():
        pytest.skip(
            "loan_totals_cod.csv missing — run "
            "`python -m src.data.build_fsa_loan_volume`"
        )
    wide = pd.read_csv(wide_path)

    assert wide["UnitID"].is_unique  # no OPEID double-mapping duplicates dollars
    year_cols = [f"YR{year}" for year in DECADE_YEARS]
    assert all(col in wide.columns for col in year_cols)

    phoenix = wide[wide["UnitID"] == 484613]
    assert len(phoenix) == 1
    assert int(phoenix[year_cols].sum(axis=1).iloc[0]) == PHOENIX_DECADE_LOANS

    # Mapping keeps 95.2% of the $928.3B COD total (unmatched OPEIDs are
    # mostly schools that closed since 2013 and have no IPEDS 2023 row).
    assert int(wide[year_cols].sum().sum()) == 883_326_699_805


def test_national_undergrad_loan_share(dl_volume: pd.DataFrame) -> None:
    """Nationally ~60% of loan dollars are undergraduate-directed (falling)."""
    by_type = dl_volume.groupby("loan_type", observed=True)["disbursed_usd"].sum()
    undergrad = int(by_type[by_type.index.isin(UNDERGRAD_LOAN_TYPES)].sum())
    total = int(by_type.sum())

    assert total == NATIONAL_DECADE_LOANS
    assert undergrad == NATIONAL_DECADE_LOANS_UNDERGRAD
    assert undergrad / total == pytest.approx(0.602, abs=0.005)

    # The share declines across the decade: 66% (2013) -> 52.5% (2022).
    y2022 = dl_volume[dl_volume["year"] == 2022]
    by_type_2022 = y2022.groupby("loan_type", observed=True)["disbursed_usd"].sum()
    ug_2022 = by_type_2022[by_type_2022.index.isin(UNDERGRAD_LOAN_TYPES)].sum()
    assert ug_2022 / by_type_2022.sum() == pytest.approx(0.525, abs=0.005)


def test_phoenix_is_largest_undergrad_loan_recipient(
    dl_volume: pd.DataFrame,
) -> None:
    """Essay: counting only undergraduate-directed loan dollars, Phoenix
    still out-drew every other institution — nearly twice the runner-up
    (Penn State)."""
    undergrad_totals = (
        dl_volume[dl_volume["loan_type"].isin(UNDERGRAD_LOAN_TYPES)]
        .groupby("opeid", observed=True)["disbursed_usd"]
        .sum()
        .sort_values(ascending=False)
    )
    assert undergrad_totals.index[0] == PHOENIX_OPEID
    assert int(undergrad_totals.iloc[0]) == PHOENIX_DECADE_LOANS_UNDERGRAD
    assert undergrad_totals.index[1] == PENN_STATE_OPEID
    assert int(undergrad_totals.iloc[1]) == PENN_STATE_DECADE_LOANS_UNDERGRAD
    assert undergrad_totals.iloc[0] / undergrad_totals.iloc[1] == pytest.approx(
        1.82, abs=0.01
    )


def test_national_pell_and_combined_undergrad_share() -> None:
    """Pell (all-undergraduate) plus loans: ~69% of the national federal aid
    pool — and ~77% of Phoenix's — was directed to undergraduates."""
    pell = pd.read_csv(PELL_PATH)
    year_cols = [f"YR{year}" for year in DECADE_YEARS]
    national_pell = int(
        pell[year_cols].apply(pd.to_numeric, errors="coerce").sum().sum()
    )
    assert national_pell == NATIONAL_DECADE_PELL

    national_share = (NATIONAL_DECADE_LOANS_UNDERGRAD + national_pell) / (
        NATIONAL_DECADE_LOANS + national_pell
    )
    assert national_share == pytest.approx(0.687, abs=0.005)

    # The essay's "77 cents of every dollar" (Phoenix, loans + Pell).
    phoenix_share = (PHOENIX_DECADE_LOANS_UNDERGRAD + PHOENIX_DECADE_PELL) / (
        PHOENIX_DECADE_LOANS + PHOENIX_DECADE_PELL
    )
    assert phoenix_share == pytest.approx(0.770, abs=0.005)


def test_phoenix_decade_pell_total() -> None:
    pell = pd.read_csv(PELL_PATH)
    row = pell[pell["UnitID"] == 484613]
    total = int(row[[f"YR{year}" for year in DECADE_YEARS]].sum(axis=1).iloc[0])
    assert total == PHOENIX_DECADE_PELL
    # Combined loans + Pell — the essay's headline figure (~$13.2B).
    assert PHOENIX_DECADE_LOANS + total == 13_207_960_414
