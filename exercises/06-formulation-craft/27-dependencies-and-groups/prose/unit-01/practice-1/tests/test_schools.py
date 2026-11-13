from ortools.math_opt.python import mathopt

from schools import Project, build

# A district's works for 2027 to 2030, not the lesson's portfolio.
PROJECTS = [
    Project("FIRE-N", (2027, 2028, 2029)),       # fire alarms, North school
    Project("FIRE-S", (2028, 2029, 2030)),       # fire alarms, South school
    Project("RAMP-N", (2027, 2028, 2029, 2030)),
    Project("LIFT-N", (2028, 2029, 2030)),
    Project("DOOR-N", (2027, 2028, 2029, 2030)),
    Project("RAMP-S", (2029, 2030)),
    Project("GYM-S", (2027, 2028, 2029, 2030)),
]
REQUIRED = {"FIRE-N": 2028, "FIRE-S": 2030}
ACCESS = {"North": ["RAMP-N", "LIFT-N", "DOOR-N"], "South": ["RAMP-S"]}
TARGETS = {"North": (2, 2028), "South": (1, 2030)}

GOOD = {("FIRE-N", 2028), ("FIRE-S", 2029), ("RAMP-N", 2027), ("DOOR-N", 2028), ("RAMP-S", 2030)}


def allowed(plan: set[tuple[str, int]]) -> bool:
    """Fix every start variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, REQUIRED, ACCESS, TARGETS)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_every_required_project_is_done():
    assert allowed(GOOD) is True
    assert allowed(GOOD - {("FIRE-S", 2029)}) is False


def test_each_school_meets_its_access_target():
    assert allowed(GOOD - {("DOOR-N", 2028)} | {("LIFT-N", 2028)}) is True
    assert allowed(GOOD - {("DOOR-N", 2028)}) is False


def test_a_required_project_after_its_deadline_is_refused():
    assert allowed(GOOD - {("FIRE-N", 2028)} | {("FIRE-N", 2027)}) is True
    assert allowed(GOOD - {("FIRE-N", 2028)} | {("FIRE-N", 2029)}) is False


def test_access_work_after_the_target_year_does_not_count():
    assert allowed(GOOD | {("LIFT-N", 2030)}) is True
    assert allowed(GOOD - {("DOOR-N", 2028)} | {("DOOR-N", 2029)}) is False


def test_no_project_starts_twice():
    assert allowed(GOOD | {("GYM-S", 2028)}) is True
    assert allowed(GOOD | {("GYM-S", 2028), ("GYM-S", 2030)}) is False
