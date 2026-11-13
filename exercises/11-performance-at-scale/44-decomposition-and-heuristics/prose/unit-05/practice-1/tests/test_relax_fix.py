import itertools

import pytest

from relax_fix import relax_and_fix


def spend_ok(projects, budgets, plan):
    spend = {y: 0 for y in budgets}
    for n, t in plan.items():
        for k, c in enumerate(projects[n]["cost"]):
            spend[t + k] = spend.get(t + k, 0) + c
    return all(spend[y] <= budgets.get(y, 0) + 1e-9 for y in spend)


def best(projects, budgets):
    names = list(projects)
    top = 0
    for combo in itertools.product(*[[None, *projects[n]["value"]] for n in names]):
        plan = {n: t for n, t in zip(names, combo) if t is not None}
        if spend_ok(projects, budgets, plan):
            top = max(top, sum(projects[n]["value"][t] for n, t in plan.items()))
    return top


def worth(projects, plan):
    return sum(projects[n]["value"][t] for n, t in plan.items())


def test_one_window_over_every_year_is_the_whole_plan():
    projects = {
        "main line": {"value": {2027: 10, 2028: 12}, "cost": [4, 4]},
        "valves": {"value": {2027: 8}, "cost": [3]},
        "pump house": {"value": {2028: 9, 2029: 7}, "cost": [5]},
    }
    budgets = {2027: 20, 2028: 20, 2029: 20}
    plan = relax_and_fix(projects, budgets, 3, 1)
    assert spend_ok(projects, budgets, plan)
    assert worth(projects, plan) == best(projects, budgets)


def test_relaxed_later_years_steer_the_early_choice():
    projects = {
        "main line": {"value": {2027: 10}, "cost": [10, 10]},
        "valves": {"value": {2027: 8}, "cost": [10]},
        "reservoir": {"value": {2028: 15}, "cost": [10]},
    }
    budgets = {2027: 10, 2028: 10}
    plan = relax_and_fix(projects, budgets, 1, 1)
    assert plan == {"valves": 2027, "reservoir": 2028}


def test_the_years_kept_are_whole_decisions():
    projects = {"north main": {"value": {2027: 5}, "cost": [6]}, "south main": {"value": {2027: 5}, "cost": [6]}}
    budgets = {2027: 10}
    plan = relax_and_fix(projects, budgets, 1, 1)
    assert spend_ok(projects, budgets, plan)
    assert len(plan) == 1
