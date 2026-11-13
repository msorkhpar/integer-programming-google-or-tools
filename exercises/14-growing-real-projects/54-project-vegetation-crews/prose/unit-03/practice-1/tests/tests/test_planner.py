"""The yearly trim plan: a knapsack over the circuits (lesson 14.1.1)."""

from itertools import combinations

from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan


def season(budget, *circuits, crews=9, months=1):
    """circuits are (id, cost, risk) or (id, cost, risk, crew-weeks); a crew-week defaults to 1."""
    return season_from_dict({"budget": budget, "crews": crews, "months": months, "circuits": [
        {"id": c[0], "region": "North", "miles": 10, "cost": c[1], "risk": c[2], "weeks": (c + (1,))[3]}
        for c in circuits]})


def test_the_plan_beats_ranking_by_risk_per_dollar():
    # By risk per $k, A (2.0) ranks first; A leaves no room for B and C, which together remove more.
    s = season(100, ("A", 60, 120), ("B", 50, 90), ("C", 50, 90))
    plan = make_plan(s)
    assert plan.status == "OPTIMAL"
    assert sorted(plan.trims) == ["B", "C"]
    assert (plan.cost, plan.risk_removed) == (100, 180)


def test_the_plan_never_spends_more_than_the_budget():
    s = season_from_dict(scenario("small"))
    plan = make_plan(s)
    assert plan.status == "OPTIMAL" and plan.trims
    assert plan.cost == sum(s.circuit(cid).cost for cid in plan.trims) <= s.budget


def test_the_plan_matches_every_subset_of_the_tiny_season():
    s = season_from_dict(scenario("tiny"))
    best = max(sum(c.risk for c in pick)
               for k in range(len(s.circuits) + 1) for pick in combinations(s.circuits, k)
               if sum(c.cost for c in pick) <= s.budget)
    assert make_plan(s).risk_removed == best


def test_a_zero_budget_is_an_answer_with_no_trims():
    plan = make_plan(season(0, ("A", 60, 120)))
    assert (plan.status, plan.trims) == ("OPTIMAL", {})
