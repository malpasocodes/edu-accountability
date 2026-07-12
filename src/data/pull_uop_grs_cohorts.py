"""Pull University of Phoenix two-decade Graduation Rate Survey (GRS) cohorts.

One-time reconstruction of Phoenix's first-time-full-time GRS cohorts for
ENTRY years 2003-2017, summed across all of the university's IPEDS UnitIDs.

Why this is not a single UnitID: before ~2010 Phoenix reported under dozens
of separate campus UnitIDs (dominated by "University of Phoenix-Online Campus",
372213); it later consolidated into UnitID 484613. So 484613 alone only has
cohorts from 2008 on. The 2003-2007 cohorts must be summed across the ~74
pre-consolidation campus IDs. (This is the graduation-record analogue of the
aid dollars being split across old OPE IDs.)

Method gate: 484613 alone, cohorts 2009-2017, must reproduce the published
one-decade figure (287,463 cohort / 45,552 completers / 241,911 non-completers
/ 15.8%) before any two-decade number is trusted.

Source: Urban Institute Education Data API (IPEDS GRS, 150% / six-year rate for
4-year institutions). Grand-total rows = subcohort/race/sex all == 99.

Writes: data/processed/uop_grs_cohorts_2003_2017.csv (pinned in
tests/data/test_uop_grs_cohorts.py). Run: python -m src.data.pull_uop_grs_cohorts
"""

from __future__ import annotations

import csv
import json
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API = "https://educationdata.urban.org/api/v1/college-university/ipeds"
OUT = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "uop_grs_cohorts_2003_2017.csv"
)

# Pre-consolidation "University of Phoenix-*" UnitIDs (2007 IPEDS directory) +
# the consolidated ID 484613. Online Campus (372213) dominates the peak years.
UOP_UNITIDS = {
    105516,
    372213,
    372222,
    380465,
    382063,
    405979,
    405988,
    405997,
    406006,
    406015,
    416962,
    419509,
    420042,
    421009,
    421018,
    432223,
    432232,
    432241,
    434946,
    434955,
    434964,
    434973,
    434982,
    434991,
    438382,
    438416,
    438610,
    438629,
    439279,
    439297,
    440420,
    440439,
    440448,
    440457,
    440466,
    442143,
    442152,
    442161,
    442170,
    442189,
    443456,
    443465,
    443474,
    443544,
    443872,
    443881,
    443890,
    443906,
    443915,
    443924,
    445300,
    445319,
    445391,
    445717,
    446701,
    446710,
    446729,
    446738,
    446747,
    446756,
    446765,
    447652,
    447661,
    448521,
    448530,
    448549,
    448558,
    448567,
    448822,
    448831,
    450456,
    450474,
    450483,
    450492,
    484613,
}


def _get(url: str) -> dict:
    last = None
    for attempt in range(8):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001 - transient API errors are expected
            last = exc
            time.sleep(0.4 * (attempt + 1))
    return {"_err": str(last)}


def _grand_totals(year: int, unitid: int):
    d = _get(f"{API}/grad-rates/{year}/?unitid={unitid}")
    if "_err" in d:
        return ("ERR", (year, unitid))
    rows = [
        r
        for r in d["results"]
        if r.get("subcohort") == 99
        and r.get("race") == 99
        and r.get("sex") == 99
        and r.get("institution_level") == 4
        and (r.get("cohort_adj_150pct") or 0) > 0
    ]
    return ("OK", (year, unitid), rows)


def pull() -> None:
    # survey year = cohort entry year + 5 in this dataset; 2008-2022 covers 2003-2017
    tasks = [(y, u) for y in range(2008, 2023) for u in UOP_UNITIDS]
    results, failures, rounds = {}, set(tasks), 0
    while failures and rounds < 10:
        rounds += 1
        todo, failures = list(failures), set()
        with ThreadPoolExecutor(max_workers=8) as ex:
            for res in ex.map(lambda a: _grand_totals(*a), todo):
                if res[0] == "ERR":
                    failures.add(res[1])
                else:
                    results[res[1]] = res[2]
    if failures:
        raise RuntimeError(f"{len(failures)} requests failed after retries; aborting")

    allc = defaultdict(lambda: [0, 0, set()])  # cohort -> [adj, completers, unitids]
    alone = defaultdict(lambda: [0, 0])  # 484613-only
    seen = set()
    for (_, u), rows in results.items():
        for r in rows:
            cy, key = r["cohort_year"], (u, r["cohort_year"])
            if key in seen:
                continue
            seen.add(key)
            adj, compl = r["cohort_adj_150pct"], r["completers_150pct"]
            allc[cy][0] += adj
            allc[cy][1] += compl
            allc[cy][2].add(u)
            if u == 484613:
                alone[cy][0] += adj
                alone[cy][1] += compl

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "cohort_year",
                "adj_cohort_all",
                "completers_all",
                "non_completers_all",
                "grad_rate_all",
                "n_unitids",
                "adj_cohort_484613",
                "completers_484613",
            ]
        )
        for cy in sorted(allc):
            a, c, uids = allc[cy]
            a6, c6 = alone.get(cy, [0, 0])
            w.writerow([cy, a, c, a - c, round(c / a, 4), len(uids), a6, c6])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    pull()
