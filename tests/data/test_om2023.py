"""Verification tests pinning IPEDS Outcome Measures 2023 figures.

The Substack accountability series (Part II) uses Outcome Measures to close
the gap between the students the federal money followed (all entering
undergraduates) and the students the standard Graduation Rate Survey counts
(first-time, full-time only). OM2023 follows every entering degree/
certificate-seeking undergraduate from the 2015-16 cohort for eight years
and counts any award (certificate, associate, bachelor's).

Raw file: data/raw/ipeds/om2023.csv (NCES,
https://nces.ed.gov/ipeds/datacenter/data/OM2023.zip).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OM_PATH = PROJECT_ROOT / "data" / "raw" / "ipeds" / "om2023.csv"

PHOENIX_UNITID = 484613
NORTHRIDGE_UNITID = 110608

# OMCHRT cohort codes.
TOTAL_ENTERING = 50
FULL_TIME_FIRST_TIME = 10
FULL_TIME_NON_FIRST_TIME = 30


@pytest.fixture(scope="module")
def om() -> pd.DataFrame:
    return pd.read_csv(
        OM_PATH,
        usecols=["UNITID", "OMCHRT", "OMACHRT", "OMAWDP4", "OMAWDP6", "OMAWDP8"],
    )


def _row(om: pd.DataFrame, unitid: int, cohort: int) -> pd.Series:
    match = om[(om["UNITID"] == unitid) & (om["OMCHRT"] == cohort)]
    assert len(match) == 1
    return match.iloc[0]


def test_phoenix_total_entering_cohort(om: pd.DataFrame) -> None:
    """Essay: 40,746 entering undergrads of every kind; 26% earned any
    award within eight years (19% / 25% at four / six years)."""
    total = _row(om, PHOENIX_UNITID, TOTAL_ENTERING)
    assert int(total["OMACHRT"]) == 40_746
    assert (total["OMAWDP4"], total["OMAWDP6"], total["OMAWDP8"]) == (19, 25, 26)


def test_phoenix_cohort_composition(om: pd.DataFrame) -> None:
    """Essay: the total cohort is nearly five times the first-time,
    full-time cohort the standard rate sees; the difference is returning
    (non-first-time) students, who finish at 29% in eight years."""
    first_time = _row(om, PHOENIX_UNITID, FULL_TIME_FIRST_TIME)
    returning = _row(om, PHOENIX_UNITID, FULL_TIME_NON_FIRST_TIME)

    assert int(first_time["OMACHRT"]) == 8_951
    assert 40_746 / 8_951 == pytest.approx(4.6, abs=0.1)
    assert int(returning["OMACHRT"]) == 31_795
    assert returning["OMAWDP8"] == 29


def test_northridge_total_entering_cohort(om: pd.DataFrame) -> None:
    """Footnote: Northridge 71% at eight years (68% at six)."""
    total = _row(om, NORTHRIDGE_UNITID, TOTAL_ENTERING)
    assert int(total["OMACHRT"]) == 12_216
    assert (total["OMAWDP4"], total["OMAWDP6"], total["OMAWDP8"]) == (48, 68, 71)


# Major online adult-serving universities cited in the Part IIa
# online-modality footnote: (UnitID, name, total entering cohort, 8-year
# any-award rate). Ordered by 8-year rate; Phoenix (26%) trails every one
# of them, above only American Public University System (25%).
ONLINE_PEERS = [
    (433387, "Western Governors University", 30_315, 48),
    (104717, "Grand Canyon University", 25_628, 46),
    (232557, "Liberty University", 18_973, 42),
    (119605, "National University", 4_741, 41),
    (183026, "Southern New Hampshire University", 28_197, 36),
    (163204, "University of Maryland Global Campus", 15_087, 32),
    (125231, "Walden University", 5_015, 32),
    (413413, "Capella University", 6_795, 28),
    (449339, "American Public University System", 26_157, 25),
]


def test_online_peer_award_rates(om: pd.DataFrame) -> None:
    """Footnote: even against the other giants of online adult education —
    the same flexibility, the same working adults — Phoenix's 26% sits at
    the bottom of the pack, above only APUS."""
    phoenix = _row(om, PHOENIX_UNITID, TOTAL_ENTERING)
    for unitid, name, cohort, awdp8 in ONLINE_PEERS:
        peer = _row(om, unitid, TOTAL_ENTERING)
        assert int(peer["OMACHRT"]) == cohort, name
        assert peer["OMAWDP8"] == awdp8, name
        if unitid != 449339:  # APUS is the one peer below Phoenix
            assert peer["OMAWDP8"] > phoenix["OMAWDP8"], name


def test_om_agrees_with_processed_gradrates_file() -> None:
    """The dashboard's gradrates.csv carries the six-year OM rate; it must
    stay consistent with the raw OM2023 file."""
    gradrates = pd.read_csv(
        PROJECT_ROOT / "data" / "raw" / "ipeds" / "2023" / "gradrates.csv"
    )
    phoenix = gradrates[gradrates["UnitID"] == PHOENIX_UNITID]
    assert int(phoenix["TOTAL_COHORT_2015"].iloc[0]) == 40_746
    assert int(phoenix["PCT_AWARD_6YRS"].iloc[0]) == 25
