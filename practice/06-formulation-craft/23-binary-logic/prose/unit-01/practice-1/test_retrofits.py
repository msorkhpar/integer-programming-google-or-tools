from ortools.math_opt.python import mathopt

from retrofits import Retrofit, build

# A city's streetlight blocks, not the lesson's portfolio.
BLOCKS = ([Retrofit(f"N{k}", "North", 30 + k) for k in range(1, 7)]
          + [Retrofit(f"S{k}", "South", 40 + k) for k in range(1, 4)]
          + [Retrofit(f"E{k}", "East", 25 + k) for k in range(1, 3)]
          + [Retrofit(f"W{k}", "West", 20 + k) for k in range(1, 3)])
YARDS = {"North": 6, "South": 2, "East": 2}          # West has no yard limit
SHARE = 0.4
BUDGET = 10_000                                       # never binding in these tests


def allowed(plan: set[str]) -> bool:
    """Fix every retrofit's variable to the plan and ask whether the model accepts it."""
    model, x = build(BLOCKS, BUDGET, YARDS, SHARE)
    for rid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if rid in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_plan_within_every_yard_cap_is_allowed_and_one_over_a_cap_refused():
    assert allowed({"N1", "N2", "S1", "S2", "E1", "W1"}) is True
    assert allowed({"N1", "N2", "N3", "S1", "S2", "S3", "E1", "W1"}) is False


def test_a_ward_taking_too_large_a_share_is_refused():
    assert allowed({"N1", "N2", "S1", "S2", "E1", "W1"}) is True
    assert allowed({"N1", "N2", "N3", "N4", "N5", "N6", "S1", "E1", "W1"}) is False


def test_the_share_is_of_the_funded_retrofits_not_of_the_candidates():
    assert allowed({"N1", "N2", "S1", "S2", "E1"}) is True
    assert allowed({"N1", "N2", "N3", "S1"}) is False


def test_a_ward_with_no_yard_cap_still_has_a_share_limit():
    assert allowed({"N1", "N2", "S1", "E1", "W1", "W2"}) is True
    assert allowed({"N1", "W1", "W2"}) is False
