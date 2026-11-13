from ortools.math_opt.python import mathopt

from outages import Project, build

# A cooperative's feeder upgrades, not the lesson's portfolio.
FEEDERS = [
    Project("F1", (2027, 2028), must_do=True),
    Project("F2", (2027, 2028, 2029)),
    Project("F3", (2027, 2028)),
    Project("F4", (2028, 2029)),
    Project("F5", (2027,)),
    Project("F6", (2029,)),
    Project("F7", (2029,)),
    Project("F8", (2027,)),
]
CREWS = {2027: 2, 2028: 2, 2029: 1}
SHARED_OUTAGES = [("F2", "F4"), ("F5", "F6")]


def allowed(schedule: dict[str, list[int]]) -> bool:
    """Fix every start variable to the schedule and ask whether the model accepts it."""
    model, x = build(FEEDERS, CREWS, SHARED_OUTAGES)
    for (pid, t), var in x.items():
        value = 1.0 if t in schedule.get(pid, []) else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


FULL = {"F1": [2027], "F3": [2027], "F2": [2028], "F4": [2028], "F7": [2029]}


def test_a_schedule_within_the_crew_caps_is_allowed_and_one_over_a_cap_refused():
    assert allowed(FULL) is True
    assert allowed({"F1": [2027], "F2": [2028], "F4": [2028], "F3": [2028]}) is False


def test_a_coordinated_pair_is_funded_together_or_not_at_all():
    assert allowed(FULL) is True
    assert allowed({"F1": [2027], "F2": [2028]}) is False


def test_a_coordinated_pair_starts_in_the_same_year():
    assert allowed(FULL) is True
    assert allowed({"F1": [2027], "F3": [2027], "F2": [2028], "F4": [2029]}) is False


def test_a_pair_with_no_common_year_is_never_funded():
    assert allowed({"F1": [2027]}) is True
    assert allowed({"F1": [2027], "F5": [2027], "F6": [2029]}) is False


def test_a_year_may_start_fewer_projects_than_its_cap():
    assert allowed({"F1": [2028]}) is True
    assert allowed({"F1": [2027], "F2": [2029], "F4": [2029], "F7": [2029]}) is False


def test_a_must_do_counts_against_its_years_cap():
    assert allowed(FULL) is True
    assert allowed({"F1": [2027], "F3": [2027], "F8": [2027]}) is False
