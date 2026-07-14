"""Verification tests pinning University of Phoenix College Scorecard debt figures.

The Substack accountability series (Part IIa, "Debt Without the Degree") cites
the median federal loan debt of Phoenix *completers* (~$31,553) to show that
the ~$5,400-per-head figure used in the non-completer debt floor is far below
what actual borrowers carry. Scorecard's non-completer median ($9,178, among
borrowers) corroborates the same point from the other side.

Raw file: data/raw/college_scorecard/uop_debt_scorecard.json
(College Scorecard API, fetched 2026-07-13; URL in the file's _provenance).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCORECARD_PATH = (
    PROJECT_ROOT / "data" / "raw" / "college_scorecard" / "uop_debt_scorecard.json"
)

PHOENIX_UNITID = 484613


@pytest.fixture(scope="module")
def phoenix() -> dict:
    with open(SCORECARD_PATH) as f:
        payload = json.load(f)
    results = payload["results"]
    assert len(results) == 1
    return results[0]


def test_is_phoenix(phoenix: dict) -> None:
    assert phoenix["id"] == PHOENIX_UNITID
    assert phoenix["school.name"] == "University of Phoenix-Arizona"


def test_completer_median_debt(phoenix: dict) -> None:
    """The ~$31,500 graduate median debt cited in the essay's debt footnote."""
    assert phoenix["latest.aid.median_debt.completers.overall"] == 31553


def test_noncompleter_median_debt(phoenix: dict) -> None:
    """Median among non-completer borrowers — well above the ~$5,400/head
    floor the essay uses across *all* non-completers, so the floor is
    conservative even against Scorecard's own non-completer figure."""
    assert phoenix["latest.aid.median_debt.noncompleters"] == 9178


def test_federal_loan_rate(phoenix: dict) -> None:
    """The 'federal loan rate ~50-62%/yr' claim: latest year is 62.5%."""
    assert phoenix["latest.aid.federal_loan_rate"] == pytest.approx(0.625)
