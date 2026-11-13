from ortools.math_opt.python import mathopt

from testing import Project, build

# A transmission company's works for 2027 to 2031, not the lesson's portfolio.
YEARS = (2027, 2028, 2029, 2030, 2031)
PROJECTS = [
    Project("SUB-N", (2027, 2028, 2029, 2030)),
    Project("TEST-N", YEARS),
    Project("SUB-S", (2028, 2029, 2030)),
    Project("TEST-S", (2029, 2030, 2031)),
]
TESTING = {"TEST-N": ("SUB-N", 2), "TEST-S": ("SUB-S", 1)}


def allowed(plan: set[tuple[str, int]]) -> bool:
    """Fix every start variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, YEARS, TESTING)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_built_station_is_tested_in_time():
    assert allowed({("SUB-N", 2027), ("TEST-N", 2028)}) is True
    assert allowed({("SUB-N", 2027)}) is False


def test_testing_needs_its_station():
    assert allowed(set()) is True
    assert allowed({("TEST-N", 2029)}) is False
    assert allowed({("SUB-N", 2029), ("TEST-N", 2028)}) is False


def test_testing_in_the_build_year_is_allowed():
    assert allowed({("SUB-S", 2029), ("TEST-S", 2029)}) is True
    assert allowed({("SUB-S", 2029)}) is False


def test_testing_on_the_deadline_is_allowed():
    assert allowed({("SUB-N", 2027), ("TEST-N", 2029)}) is True
    assert allowed({("SUB-N", 2027), ("TEST-N", 2030)}) is False


def test_a_deadline_after_the_plan_needs_no_testing():
    assert allowed({("SUB-N", 2030)}) is True
    assert allowed({("SUB-N", 2029)}) is False
