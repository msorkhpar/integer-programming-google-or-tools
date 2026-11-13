"""Hand-built exports for the tests: small enough to solve by hand, never GridCap."""

from __future__ import annotations

import pytest


def row(pid, cost_profile=(100,), npv=100, earliest=2027, latest=None, must_do=False, parent=None,
        lag=0, alt_group=None, bundle=None, asset=None):
    """One project row of the planning export, with every column the export carries."""
    latest = earliest if latest is None else latest
    if isinstance(npv, int):
        npv = {t: npv for t in range(earliest, latest + 1)}
    return {
        "id": pid, "name": f"project {pid}", "program": "distribution", "region": "Ridge",
        "cost_profile": list(cost_profile), "earliest_start": earliest, "latest_start": latest,
        "must_do": must_do, "parent": parent, "parent_lag": lag, "alt_group": alt_group,
        "bundle": bundle, "npv": {str(t): v for t, v in npv.items()},
        "asset": asset or {"id": f"A-{pid}", "age": 10, "weibull_beta": 2.0, "weibull_eta": 30.0,
                           "cof": 1000},
    }


def export(rows, years=(2027,), budget=None, capital_budget=None, **settings):
    """A whole export: the rows, the yearly budgets, the one envelope, and any planner settings."""
    if budget is None:
        # One year and one envelope: the year's budget is the envelope (the first request's shape).
        budget = {years[0]: capital_budget} if capital_budget is not None and len(years) == 1 \
            else {y: 10_000 for y in years}
    return {
        "name": "test", "years": list(years),
        "capital_budget": sum(budget.values()) if capital_budget is None else capital_budget,
        "budget": {str(y): v for y, v in budget.items()},
        "projects": rows, **settings,
    }


@pytest.fixture
def make():
    """The two builders, for tests that want them as a fixture."""
    return row, export
