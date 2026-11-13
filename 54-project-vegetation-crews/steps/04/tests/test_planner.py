"""The yearly trim plan: a knapsack over the circuits (lesson 14.1.1)."""

from itertools import accumulate, combinations, permutations

from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import horizon, make_plan
from rules import DEFER_WEEKS, carried


def season(budget, *circuits, crews=9, months=1):
    """circuits are (id, cost, risk, [crew-weeks, [growth]]); crew-weeks default to 1, growth to 0."""
    rows = []
    for cid, cost, risk, *more in circuits:
        weeks, growth = more[0] if more else 1, more[1] if len(more) > 1 else 0
        rows.append({"id": cid, "region": "North", "miles": 10, "cost": cost, "risk": risk,
                     "weeks": weeks, "growth": growth})
    return season_from_dict({"budget": budget, "crews": crews, "months": months, "circuits": rows})


def test_the_plan_beats_ranking_by_risk_per_dollar():
    # By risk per $k, A (2.0) ranks first; A leaves no room for B and C, which together remove more.
    s = season(100, ("A", 60, 120), ("B", 50, 90), ("C", 50, 90))
    plan = make_plan(s)
    assert plan.status == "OPTIMAL"
    assert sorted(plan.trims) == ["B", "C"]
    assert (plan.cost, plan.risk_removed) == (100, 180)


def test_the_plan_never_spends_more_than_the_budget():
    s = season_from_dict(scenario("tiny"))
    plan = make_plan(s)
    assert plan.status == "OPTIMAL" and plan.trims
    assert plan.cost == sum(s.circuit(cid).cost for cid in plan.trims) <= s.budget


def test_the_plan_matches_every_subset_and_order_of_the_tiny_season():
    # One crew: a plan is a subset within the budget, done back to back in some order.
    raw = scenario("tiny")
    s, rows = season_from_dict(raw), raw["circuits"]
    assert s.crews == 1
    best = min(sum(carried(c, end) for c, end in zip(order, accumulate(c["weeks"] for c in order)))
               + sum(carried(c, horizon(s) + DEFER_WEEKS) for c in rows if c not in pick)
               for k in range(len(rows) + 1) for pick in combinations(rows, k)
               if sum(c["cost"] for c in pick) <= s.budget and sum(c["weeks"] for c in pick) <= horizon(s)
               for order in permutations(pick))
    assert make_plan(s).risk_carried == best


def test_a_zero_budget_is_an_answer_with_no_trims():
    plan = make_plan(season(0, ("A", 60, 120)))
    assert (plan.status, plan.trims) == ("OPTIMAL", {})
