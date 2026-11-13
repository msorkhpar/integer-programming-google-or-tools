from dataclasses import replace

from renewal.fleet import Transformer
from renewal.plan import plan
from renewal.request import Request, Scenario
from renewal.risk import evaluate, risk_removed

FAST = Scenario("fails younger", eta=0.85, weight=1)
SLOW = Scenario("fails older", eta=1.15, weight=3)


def unit(tid, kind="small", age=55, cof=2000, cost=300):
    return Transformer(tid, "S-" + tid, "north", kind, age, cost, cof, 50, 0.0)


def test_a_curve_that_fails_younger_makes_a_replacement_worth_more():
    request = Request(budget=0, years=1, window=10)
    base = risk_removed(unit("A"), 2027, request)
    assert risk_removed(unit("A"), 2027, request, Scenario("same")) == base
    assert risk_removed(unit("A"), 2027, request, FAST) > base > risk_removed(unit("A"), 2027, request, SLOW)


def test_the_expected_objective_is_the_weighted_mean_over_scenarios():
    fleet = [unit("A"), unit("B", "medium", age=45, cof=5000), unit("C", age=65)]
    request = Request(budget=600, years=2, window=10, scenarios=(FAST, SLOW))
    got = plan(fleet, request)
    mean = (1 * evaluate(fleet, request, got.replace, FAST) + 3 * evaluate(fleet, request, got.replace, SLOW)) / 4
    assert abs(got.value - mean) < 1e-6


def test_the_worst_case_plan_does_best_in_its_worst_scenario():
    fleet = [unit("A", age=68, cof=2000), unit("B", "large", age=40, cof=9000, cost=300)]
    request = Request(budget=300, years=1, window=15, scenarios=(FAST, SLOW))
    worst = plan(fleet, replace(request, objective="worst"))
    expected = plan(fleet, request)

    def lowest(p):
        return min(evaluate(fleet, request, p.replace, s) for s in (FAST, SLOW))

    assert abs(worst.value - lowest(worst)) < 1e-6
    assert lowest(worst) >= lowest(expected)
