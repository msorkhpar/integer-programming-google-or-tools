import math

from renewal.fleet import generate_fleet
from renewal.model import build, candidates
from renewal.reference import build_reference
from renewal.request import Request
from renewal.risk import risk_removed, risk_table

EVERY_RULE = Request(budget=3000, years=4, window=8, min_age=30, outage_cost=300, outages=2,
                     crew_weeks=10, lead_times=True, spares={"medium": 1, "large": 1})


def rows(model):
    """Each row by name: its bounds and its terms by variable name."""
    found = {c.name: (c.lower_bound, c.upper_bound, {}) for c in model.linear_constraints()}
    for entry in model.linear_constraint_matrix_entries():
        found[entry.linear_constraint.name][2][entry.variable.name] = entry.coefficient
    return found


def objective(model):
    return {term.variable.name: term.coefficient for term in model.objective.linear_terms()}


def test_the_fast_builder_makes_the_reference_model():
    fleet = generate_fleet(80, seed=11)
    fast, slow = build(fleet, EVERY_RULE).model, build_reference(fleet, EVERY_RULE).model
    assert [v.name for v in fast.variables()] == [v.name for v in slow.variables()]
    assert rows(fast) == rows(slow)
    a, b = objective(fast), objective(slow)
    assert a.keys() == b.keys()
    assert all(math.isclose(a[name], b[name], rel_tol=1e-9, abs_tol=1e-9) for name in a)


def test_the_risk_table_matches_the_coefficient_function():
    units = candidates(generate_fleet(60, seed=4), EVERY_RULE)
    table = risk_table(units, EVERY_RULE)
    for i, t in enumerate(units):
        for j, y in enumerate(EVERY_RULE.plan_years()):
            assert math.isclose(table[i, j], risk_removed(t, y, EVERY_RULE), rel_tol=1e-9, abs_tol=1e-9)


def test_a_scaled_request_grows_every_limit_with_the_fleet():
    big = EVERY_RULE.scaled(10)
    assert (big.budget, big.outages, big.crew_weeks) == (30000, 20, 100)
    assert big.spares == {"medium": 10, "large": 10}
    assert (big.years, big.window, big.outage_cost) == (4, 8, 300)
