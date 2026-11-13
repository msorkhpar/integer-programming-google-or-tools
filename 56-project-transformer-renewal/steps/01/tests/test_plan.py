from itertools import combinations
import random

from renewal.fleet import Transformer, risk
from renewal.plan import feasible, plan
from renewal.request import Request


def unit(tid, cost, pof, cof, condition=50):
    return Transformer(tid, "S0001", "north", "small", 50, cost, cof, condition, pof)


def test_the_plan_takes_the_riskiest_units_not_the_worst_scored():
    fleet = [unit("A", 600, 0.02, 1000, condition=95),
             unit("B", 300, 0.10, 3000, condition=60),
             unit("C", 300, 0.10, 2500, condition=55)]
    assert set(plan(fleet, Request(budget=600)).replace) == {"B", "C"}


def test_the_plan_uses_money_a_ranking_leaves_on_the_table():
    fleet = [unit("A", 500, 0.05, 2000, condition=90),
             unit("B", 700, 0.05, 2000, condition=80),
             unit("C", 400, 0.05, 2000, condition=70)]
    assert sorted(plan(fleet, Request(budget=1000)).replace) == ["A", "C"]


def test_the_plan_is_the_best_subset_within_the_budget():
    rng = random.Random(3)
    fleet = [unit(f"U{i}", rng.randrange(200, 900, 10), rng.uniform(0.01, 0.2), rng.randrange(500, 5000, 10))
             for i in range(8)]
    budget = 2000
    best = max(sum(risk(t) for t in subset)
               for k in range(len(fleet) + 1) for subset in combinations(fleet, k)
               if sum(t.cost for t in subset) <= budget)
    assert abs(plan(fleet, Request(budget)).value - best) < 1e-6


def test_the_budget_allows_a_plan_at_the_limit_and_refuses_one_above_it():
    fleet = [unit("A", 500, 0.05, 2000), unit("B", 500, 0.05, 2000), unit("C", 10, 0.05, 2000)]
    assert feasible(fleet, Request(budget=1000), {"A": 2027, "B": 2027})
    assert not feasible(fleet, Request(budget=1000), {"A": 2027, "B": 2027, "C": 2027})
