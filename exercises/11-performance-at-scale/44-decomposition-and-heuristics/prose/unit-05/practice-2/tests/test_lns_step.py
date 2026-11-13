from lns_step import lns_step

PROJECTS = {
    "main line": {"value": {2027: 10, 2028: 14}, "cost": [10]},
    "valves": {"value": {2027: 8, 2028: 6}, "cost": [10]},
    "pump house": {"value": {2027: 7}, "cost": [5]},
    "meters": {"value": {2028: 4}, "cost": [5]},
}
BUDGETS = {2027: 15, 2028: 15}


def worth(plan):
    return sum(PROJECTS[n]["value"][t] for n, t in plan.items())


def test_freeing_every_project_finds_the_best_plan():
    plan = lns_step(PROJECTS, BUDGETS, {}, set(PROJECTS))
    # 2027: valves 8 + pump house 7; 2028: main line 14 + meters 4
    assert worth(plan) == 33
    assert plan == {"valves": 2027, "pump house": 2027, "main line": 2028, "meters": 2028}


def test_projects_outside_stay_as_they_were():
    start = {"main line": 2027}
    plan = lns_step(PROJECTS, BUDGETS, start, {"valves", "pump house"})
    assert plan.get("main line") == 2027
    assert "meters" not in plan
    assert plan == {"main line": 2027, "pump house": 2027, "valves": 2028}


def test_a_freed_project_may_move_to_another_year():
    start = {"main line": 2027, "pump house": 2027}
    plan = lns_step(PROJECTS, BUDGETS, start, {"main line", "valves"})
    assert plan.get("main line") == 2028
    assert plan.get("valves") == 2027
