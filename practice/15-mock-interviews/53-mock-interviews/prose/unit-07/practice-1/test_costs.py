from itertools import combinations

import pytest

from costs import Project, decision_costs

# A rail operator's track renewals, not the lessons' portfolio.
TRACKS = [
    Project("A", 60, 30),
    Project("B", 50, 20),
    Project("C", 40, 20),
    Project("D", 10, 10, must_do=True),
]
BUDGET = 60


def brute_force_best(projects, budget, forced):
    """The best value over every plan that keeps the budget, the must-dos and the forcing; None if none does."""
    best = None
    ids = [p.pid for p in projects]
    for k in range(len(ids) + 1):
        for chosen in combinations(ids, k):
            plan = set(chosen)
            if any(p.must_do and p.pid not in plan for p in projects):
                continue
            if any((pid in plan) != want for pid, want in forced.items()):
                continue
            if sum(p.cost for p in projects if p.pid in plan) > budget:
                continue
            value = sum(p.value for p in projects if p.pid in plan)
            best = value if best is None else max(best, value)
    return best


def test_a_funded_project_costs_what_the_plan_loses_without_it():
    assert decision_costs(TRACKS, BUDGET)["A"] == pytest.approx(20.0)


def test_an_unfunded_project_costs_what_forcing_it_in_displaces():
    reordered = [TRACKS[2], TRACKS[0], TRACKS[1], TRACKS[3]]
    assert decision_costs(reordered, BUDGET)["C"] == pytest.approx(10.0)


def test_every_decision_is_priced_against_the_same_rules():
    costs = decision_costs(TRACKS, BUDGET)
    best = brute_force_best(TRACKS, BUDGET, {})
    for pid in ("A", "B", "C"):
        funded = brute_force_best(TRACKS, BUDGET, {}) == brute_force_best(TRACKS, BUDGET, {pid: True})
        forced = brute_force_best(TRACKS, BUDGET, {pid: not funded})
        assert costs[pid] == pytest.approx(best - forced)


def test_a_reversal_the_rules_refuse_has_no_cost():
    assert decision_costs(TRACKS, BUDGET)["D"] is None
