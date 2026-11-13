from ortools.math_opt.python import mathopt

from cash import Project, build

# A water authority's capital programme, not the lessons' portfolio.
PROJECTS = [
    Project("N1", "N", (2027, 2028, 2029), (60,)),
    Project("N2", "N", (2028, 2029), (40, 40)),
    Project("S1", "S", (2027, 2028), (120,)),
    Project("S2", "S", (2027, 2028, 2029), (90,)),
    Project("S3", "S", (2027, 2028, 2029), (50,)),
    Project("S4", "S", (2029,), (100,)),
]
BUDGETS = {2027: 100, 2028: 100, 2029: 100}
CARRY_SHARE = 0.5
FLOORS = {"N": 60}


def allowed(plan: dict[str, int], floors: dict[str, int] = FLOORS) -> bool:
    """Fix every start variable to the plan (project -> start year); the carries stay free."""
    model, x = build(PROJECTS, BUDGETS, CARRY_SHARE, floors)
    for (pid, t), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(pid) == t else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_unspent_money_can_be_spent_the_next_year_but_a_first_year_overspend_is_refused():
    assert allowed({"N1": 2027, "S1": 2028}) is True
    assert allowed({"N1": 2027, "S1": 2027}) is False


def test_a_year_carries_out_at_most_its_share():
    assert allowed({"N1": 2027, "S1": 2028}) is True
    assert allowed({"N1": 2029, "S4": 2029}) is False


def test_a_region_below_its_floor_is_refused():
    assert allowed({"N1": 2027, "S1": 2028}) is True
    assert allowed({"S1": 2028}) is False


def test_money_carried_forward_is_spent_only_once():
    assert allowed({"N1": 2028, "S2": 2028, "S3": 2029}) is True
    assert allowed({"N1": 2028, "S2": 2028, "S3": 2029, "S4": 2029}) is False


def test_the_floor_counts_only_spend_inside_the_plan():
    assert allowed({"N1": 2027, "S1": 2028}) is True
    assert allowed({"N2": 2029, "S1": 2028}) is False


def test_a_floor_for_a_region_that_can_spend_nothing_allows_no_plan():
    assert allowed({"N1": 2027, "S1": 2028}) is True
    assert allowed({"N1": 2027, "S1": 2028}, {"N": 60, "E": 30}) is False
