from itertools import combinations

from fleet import replacement_plan

COSTS = {"B01": 230, "B02": 235, "B03": 240, "B04": 245, "B05": 250, "B06": 200, "B07": 205, "B08": 210}
BUDGET = 1000


def cheapest_of_the_largest(costs, budget):
    for k in range(len(costs), -1, -1):
        fits = [sorted(c) for c in combinations(costs, k) if sum(costs[b] for b in c) <= budget]
        if fits:
            return min(fits, key=lambda c: sum(costs[b] for b in c))


def test_the_plan_fits_the_budget_and_names_buses_in_order():
    plan = replacement_plan(COSTS, BUDGET)
    assert plan == sorted(plan) and set(plan) <= set(COSTS)
    assert sum(COSTS[b] for b in plan) <= BUDGET


def test_no_plan_replaces_more_buses():
    plan = replacement_plan(COSTS, BUDGET)
    assert len(plan) == len(cheapest_of_the_largest(COSTS, BUDGET)) == 4


def test_among_the_largest_plans_the_cheapest_wins():
    want = cheapest_of_the_largest(COSTS, BUDGET)
    assert replacement_plan(COSTS, BUDGET) == want
    backwards = dict(reversed(list(COSTS.items())))
    assert replacement_plan(backwards, BUDGET) == want
