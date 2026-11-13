from ortools.math_opt.python import mathopt

from overrides import Project, build

# A port authority's dredging projects, not the lessons' portfolio.
PROJECTS = [
    Project("P1", (2027, 2028, 2029)),
    Project("P2", (2027, 2028)),
    Project("P3", (2028, 2029, 2030)),
    Project("P4", (2027, 2028, 2029, 2030)),
    Project("P5", (2027, 2028)),
]
OVERRIDES = [("start_in", "P1", 2028), ("never", "P2"), ("not_before", "P3", 2029), ("fund", "P4")]


def allowed(plan: dict[str, int]) -> bool:
    """Fix the plan (project -> start year) on top of the overrides and ask whether the model accepts it."""
    model, x = build(PROJECTS, OVERRIDES)
    for (pid, t), var in x.items():
        value = 1.0 if plan.get(pid) == t else 0.0
        if value < var.lower_bound or value > var.upper_bound:
            return False                        # the override's bounds already exclude this value
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def refused(overrides: list[tuple]) -> bool:
    """Build the model with these overrides and say whether apply_overrides refused them."""
    try:
        build(PROJECTS, overrides)
    except ValueError:
        return True
    return False


def test_a_start_override_fixes_the_year():
    assert allowed({"P1": 2028, "P4": 2027}) is True
    assert allowed({"P1": 2027, "P4": 2027}) is False


def test_a_never_override_keeps_the_project_out():
    assert allowed({"P1": 2028, "P4": 2027}) is True
    assert allowed({"P1": 2028, "P4": 2027, "P2": 2027}) is False


def test_a_not_before_override_refuses_earlier_years():
    assert allowed({"P1": 2028, "P4": 2027, "P3": 2030}) is True
    assert allowed({"P1": 2028, "P4": 2027, "P3": 2028}) is False


def test_a_fund_override_refuses_a_plan_without_the_project():
    assert allowed({"P1": 2028, "P4": 2027, "P5": 2027}) is True
    assert allowed({"P1": 2028, "P5": 2027}) is False


def test_a_start_override_also_funds_the_project():
    assert allowed({"P1": 2028, "P4": 2029}) is True
    assert allowed({"P4": 2029}) is False


def test_not_before_allows_the_year_itself():
    assert allowed({"P1": 2028, "P4": 2027, "P3": 2029}) is True
    assert allowed({"P1": 2028, "P4": 2027, "P3": 2028}) is False


def test_fund_allows_any_year_in_the_window():
    assert allowed({"P1": 2028, "P4": 2030}) is True
    assert allowed({"P1": 2028}) is False


def test_a_start_year_outside_the_window_is_refused():
    assert refused(OVERRIDES) is False
    assert refused(OVERRIDES + [("start_in", "P5", 2030)]) is True


def test_contradicting_overrides_are_refused():
    assert refused(OVERRIDES + [("start_in", "P5", 2028)]) is False
    assert refused(OVERRIDES + [("never", "P1")]) is True
