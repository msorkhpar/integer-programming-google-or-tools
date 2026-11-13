from ortools.math_opt.python import mathopt

from counties import Project, build

# A fiber builder's projects, not the lesson's portfolio.
YEARS = (2027, 2028, 2029)
PROJECTS = [
    Project("A1", "Ash", (350, 200), (2027, 2028)),
    Project("A2", "Ash", (250,), (2027, 2028, 2029)),
    Project("A3", "Ash", (400,), (2028, 2029)),
    Project("A4", "Ash", (200, 300), (2027,)),
    Project("B1", "Birch", (500,), (2027, 2028, 2029)),
    Project("B2", "Birch", (150, 150), (2027, 2028)),
]
FLOOR = {"Ash": 600, "Birch": 300}
CAP = {"Ash": 1000}
YEARLY_CAP = {("Ash", 2028): 450}


def allowed(plan: set[tuple[str, int]]) -> bool:
    """Fix every start variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, YEARS, FLOOR, CAP, YEARLY_CAP)
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


GOOD = {("A1", 2027), ("A3", 2029), ("B1", 2027)}


def test_each_county_gets_its_minimum():
    assert allowed(GOOD) is True
    assert allowed({("A1", 2027), ("B1", 2027)}) is False
    assert allowed({("A1", 2027), ("A3", 2029)}) is False


def test_a_county_gets_no_more_than_its_cap():
    assert allowed({("A2", 2027), ("A3", 2029), ("B1", 2029)}) is True
    assert allowed(GOOD | {("A2", 2029)}) is False


def test_a_county_stays_within_its_yearly_cap():
    assert allowed({("A2", 2028), ("A3", 2029), ("B1", 2028)}) is True
    assert allowed({("A1", 2028), ("A2", 2028), ("B1", 2028)}) is False


def test_later_years_of_work_count_in_their_own_year():
    assert allowed({("A1", 2027), ("A2", 2028), ("B1", 2029)}) is True
    assert allowed({("A1", 2027), ("A3", 2028), ("B1", 2029)}) is False


def test_every_year_of_work_counts_toward_the_minimum():
    assert allowed({("A4", 2027), ("A2", 2029), ("B1", 2027)}) is True
    assert allowed({("A2", 2027), ("B2", 2027)}) is False
