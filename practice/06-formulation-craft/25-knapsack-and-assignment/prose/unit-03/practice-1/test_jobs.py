import itertools

from ortools.math_opt.python import mathopt

from jobs import Limit, build

# A substation programme's jobs, sharing a crane, outage hours and a budget; not the lesson's portfolio.


def lp_bound(values, limits) -> float:
    model, _ = build(values, limits, integer=False)
    return mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value()


def same_whole_plans(values, limits) -> bool:
    """The model allows a whole plan exactly when the plan fits every limit."""
    for plan in itertools.product((0, 1), repeat=len(values)):
        chosen = {j for j, take in zip(values, plan) if take}
        fits = all(sum(lim.use.get(j, 0) for j in chosen) <= lim.capacity for lim in limits)
        model, x = build(values, limits)
        for j, var in x.items():
            var.lower_bound = var.upper_bound = 1.0 if j in chosen else 0.0
        ok = mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL
        if ok != fits:
            return False
    return True


VALUES = {"A": 9, "B": 8, "C": 7, "D": 3, "E": 2}
CRANE = Limit("crane_days", {"A": 6, "B": 7, "C": 6, "D": 2, "E": 1}, 10)


def test_big_jobs_of_one_resource_get_one_row():
    # A, B and C each use more than half the crane: no two fit together. The LP may not take
    # A whole and a seventh of B on top of D and E.
    assert same_whole_plans(VALUES, [CRANE])
    assert lp_bound(VALUES, [CRANE]) <= 9 + 3 + 2 + 1e-6


def test_each_resource_gives_its_own_row():
    outage = Limit("outage_hours", {"A": 1, "B": 2, "C": 2, "D": 5, "E": 6}, 8)
    assert same_whole_plans(VALUES, [CRANE, outage])
    # D and E cannot share the outage hours; A, B and C cannot share the crane.
    assert lp_bound(VALUES, [CRANE, outage]) <= 9 + 3 + 1e-6


def test_two_jobs_of_exactly_half_may_share():
    half = Limit("crane_days", {"A": 5, "B": 5, "C": 6, "D": 2, "E": 1}, 10)
    budget = Limit("budget", {"A": 4, "B": 4, "C": 4, "D": 1, "E": 30}, 20)
    # A and B use 5 crane-days each: together exactly 10, so they may share the crane.
    assert same_whole_plans(VALUES, [half, budget])
    assert lp_bound(VALUES, [half, budget]) <= 17 + 1e-6


def test_a_job_too_big_on_its_own_is_never_funded():
    budget = Limit("budget", {"A": 30, "B": 4, "C": 4, "D": 1, "E": 1}, 20)
    assert same_whole_plans(VALUES, [budget])
    assert lp_bound(VALUES, [budget]) <= 8 + 7 + 3 + 2 + 1e-6
