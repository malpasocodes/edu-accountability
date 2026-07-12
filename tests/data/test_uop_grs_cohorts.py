"""Pin the University of Phoenix two-decade GRS cohort reconstruction.

Freezes the figures cited in the Substack accountability series (Part IIa):
Phoenix's first-time-full-time Graduation Rate Survey cohorts for ENTRY years
2003-2017, summed across all of the university's IPEDS UnitIDs (the ~74
pre-consolidation campus IDs for 2003-2007 + consolidated UnitID 484613 for
2008-2017). Data pulled from the Urban Institute Education Data API on
2026-07-12 by ``src.data.pull_uop_grs_cohorts`` and committed to
``data/processed/uop_grs_cohorts_2003_2017.csv``.

The gate test reproduces the published one-decade figure (484613 alone,
2009-2017) exactly; the two-decade tests freeze the ~504,000 non-completer
count and the ~16-17% grad rate used in the essay.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "processed"
    / "uop_grs_cohorts_2003_2017.csv"
)


@pytest.fixture(scope="module")
def grs() -> pd.DataFrame:
    if not CSV_PATH.exists():
        pytest.skip(
            "uop_grs_cohorts_2003_2017.csv missing — run "
            "`python -m src.data.pull_uop_grs_cohorts`"
        )
    return pd.read_csv(CSV_PATH)


def test_covers_entry_cohorts_2003_2017(grs: pd.DataFrame) -> None:
    assert list(grs["cohort_year"]) == list(range(2003, 2018))


def test_484613_gate_reproduces_published_decade(grs: pd.DataFrame) -> None:
    """The method gate: 484613 alone, 2009-2017, must reproduce the published
    one-decade figure exactly (287,463 / 45,552 / 241,911 / 15.8%)."""
    recent = grs[grs["cohort_year"].between(2009, 2017)]
    adj = int(recent["adj_cohort_484613"].sum())
    compl = int(recent["completers_484613"].sum())
    assert adj == 287_463
    assert compl == 45_552
    assert adj - compl == 241_911
    assert compl / adj == pytest.approx(0.158, abs=0.002)


def test_pre_consolidation_cohorts_have_no_484613(grs: pd.DataFrame) -> None:
    """484613 (the consolidated ID) has no cohorts before 2008; the 2003-2007
    cohorts are summed across the pre-consolidation campus IDs."""
    early = grs[grs["cohort_year"] < 2008]
    assert (early["adj_cohort_484613"] == 0).all()
    assert (early["completers_484613"] == 0).all()
    assert int(early["n_unitids"].min()) >= 40  # dozens of campus IDs per cohort


def test_conservative_two_decade_non_completers(grs: pd.DataFrame) -> None:
    """Essay's ~504,000: 2003-2007 all-campus + 484613-only 2008-2017 (avoids any
    consolidation-era double-count)."""
    pre = grs[grs["cohort_year"].between(2003, 2007)]
    post = grs[grs["cohort_year"].between(2008, 2017)]
    adj = int(pre["adj_cohort_all"].sum() + post["adj_cohort_484613"].sum())
    compl = int(pre["completers_all"].sum() + post["completers_484613"].sum())
    assert adj == 604_667
    assert compl == 100_576
    assert adj - compl == 504_091
    assert compl / adj == pytest.approx(0.166, abs=0.003)


def test_all_campus_two_decade_totals(grs: pd.DataFrame) -> None:
    """The fuller all-campus count (includes branch campuses still reporting
    separately 2008-2013): ~516,000 non-completers."""
    adj = int(grs["adj_cohort_all"].sum())
    compl = int(grs["completers_all"].sum())
    assert adj == 618_435
    assert compl == 102_484
    assert adj - compl == 515_951
    assert compl / adj == pytest.approx(0.166, abs=0.003)


def test_peak_decade_rate_matches_recent_decade(grs: pd.DataFrame) -> None:
    """Peak decade (2003-2008) ~17.3% is essentially the recent decade's 15.8% —
    the failure is consistent, not worsening. Earliest cohorts (2003-04) lower."""
    peak = grs[grs["cohort_year"].between(2003, 2008)]
    adj = int(peak["adj_cohort_all"].sum())
    compl = int(peak["completers_all"].sum())
    assert adj == 320_690
    assert compl == 55_522
    assert compl / adj == pytest.approx(0.173, abs=0.003)
    # earliest classes are the worst
    d = grs.set_index("cohort_year")
    assert d.loc[2003, "grad_rate_all"] < 0.11
    assert d.loc[2004, "grad_rate_all"] < 0.13


def test_per_cohort_anchors(grs: pd.DataFrame) -> None:
    d = grs.set_index("cohort_year")
    assert int(d.loc[2003, "adj_cohort_all"]) == 21_007  # first peak cohort
    assert int(d.loc[2009, "adj_cohort_484613"]) == 110_606  # largest 484613 cohort
    assert int(d.loc[2017, "adj_cohort_all"]) == 5_427  # the collapse
