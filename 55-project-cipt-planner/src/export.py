"""The planning export the CIPT planner reads, made from a GridCap portfolio.

GridCap is a fictional utility generated for this course; no number here describes a real one.
The export has every column the planning system keeps, from the first version of the planner on:
each version reads the columns it uses and ignores the rest (lesson 14.2.1). GridCap has no
bundles, so the planners' bundles are passed in and written to the `bundle` column.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from gridcap import Portfolio, generate

#: Bundles the planners declare on GridCap: members are funded together or not at all (lesson 14.2.3).
BUNDLES = {
    "tiny": {"P005": "B1", "P008": "B1"},
    "small": {"P011": "B1", "P012": "B1"},
}


def export_of(portfolio: Portfolio, bundles: dict[str, str] | None = None) -> dict:
    """The export's dictionary form: one row per project, with its asset's health columns."""
    bundles = BUNDLES.get(portfolio.name.split()[-1], {}) if bundles is None else bundles
    rows = []
    for p in portfolio.projects:
        a = portfolio.asset(p.asset_id)
        rows.append({
            "id": p.project_id, "name": p.name, "program": p.program, "region": p.region,
            "cost_profile": list(p.cost_profile), "earliest_start": p.earliest_start,
            "latest_start": p.latest_start, "must_do": p.must_do, "parent": p.parent,
            "parent_lag": p.parent_lag, "alt_group": p.alt_group, "bundle": bundles.get(p.project_id),
            "npv": {str(t): v for t, v in p.npv.items()},
            "asset": {"id": a.asset_id, "age": a.age, "weibull_beta": a.weibull_beta,
                      "weibull_eta": a.weibull_eta, "cof": a.cof},
        })
    return {
        "name": portfolio.name, "years": list(portfolio.years),
        "capital_budget": portfolio.capital_budget,
        "budget": {str(y): v for y, v in portfolio.budget.items()},
        "projects": rows,
    }


def gridcap_export(size: str) -> dict:
    return export_of(generate(size))


if __name__ == "__main__":
    # python3 export.py tiny > demo.json writes the demo export each snapshot ships in data/.
    json.dump(gridcap_export(sys.argv[1] if len(sys.argv) > 1 else "tiny"), sys.stdout, indent=1)
