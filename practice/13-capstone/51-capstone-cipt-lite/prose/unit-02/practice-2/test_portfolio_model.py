import copy

from portfolio_model import allows, best

# A fictional utility's practice portfolio (invented test data). Money in $k.
SNAPSHOT = {
    "years": [2027, 2028, 2029], "rate": 0.05,
    "budget": {2027: 300, 2028: 250, 2029: 300},
    "region_budget": {"North": {2027: 300, 2028: 300, 2029: 300}, "South": {2027: 200, 2028: 200, 2029: 200}},
    "crews": {"lines": {2027: 3, 2028: 3, 2029: 3}, "poles": {2027: 3, 2028: 3, 2029: 3}},
    "floor": {"North": 100, "South": 0},
    "projects": {
        "J1": {"program": "lines", "region": "North", "cost": [120, 60], "earliest": 2027, "latest": 2028,
               "must": True, "parent": None, "lag": 0, "group": None, "crews": 2, "npv": {2027: 70, 2028: 60}},
        "J2": {"program": "lines", "region": "North", "cost": [100], "earliest": 2028, "latest": 2029,
               "must": False, "parent": "J1", "lag": 1, "group": None, "crews": 1, "npv": {2028: 50, 2029: 45}},
        "J3": {"program": "poles", "region": "South", "cost": [90], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": "G1", "crews": 1,
               "npv": {2027: 40, 2028: 38, 2029: 35}},
        "J4": {"program": "poles", "region": "South", "cost": [140], "earliest": 2027, "latest": 2028,
               "must": False, "parent": None, "lag": 0, "group": "G1", "crews": 2, "npv": {2027: 65, 2028: 55}},
        "J5": {"program": "poles", "region": "South", "cost": [80, 80], "earliest": 2027, "latest": 2028,
               "must": False, "parent": None, "lag": 0, "group": None, "crews": 1, "npv": {2027: 30, 2028: 28}},
        "J6": {"program": "poles", "region": "North", "cost": [110], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": None, "crews": 1,
               "npv": {2027: 45, 2028: 44, 2029: 40}},
        "J7": {"program": "lines", "region": "North", "cost": [50], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": None, "crews": 1,
               "npv": {2027: 20, 2028: 19, 2029: 18}},
    },
}


def variant(**changes) -> dict:
    """SNAPSHOT with some top-level entries replaced, and some projects' fields."""
    doc = copy.deepcopy(SNAPSHOT)
    for key, value in changes.items():
        if key in doc["projects"]:
            doc["projects"][key].update(value)
        else:
            doc[key] = value
    return doc


# Every limit ten times larger, and every project allowed only its earliest start: no limit binds,
# so the best plan funds every project the must-do, alternative and parent rules let it fund.
LOOSE = variant(budget={y: 3000 for y in SNAPSHOT["years"]},
                region_budget={r: {y: 3000 for y in SNAPSHOT["years"]} for r in ("North", "South")},
                crews={g: {y: 30 for y in SNAPSHOT["years"]} for g in ("lines", "poles")},
                **{j: {"latest": p["earliest"]} for j, p in SNAPSHOT["projects"].items()})
LOOSE_BEST = 280.0
TIGHT_BEST = 271.0
TOLERANCE = 1e-6
BASE = {"J1": 2028, "J2": 2029, "J3": 2027, "J6": 2027}


def worth(snap: dict, plan: dict) -> int:
    return sum(snap["projects"][j]["npv"][t] for j, t in plan.items())


def test_the_best_plan_with_loose_limits_is_worth_the_reference():
    value, plan = best(LOOSE)
    assert abs(value - LOOSE_BEST) <= TOLERANCE
    assert worth(LOOSE, plan) == LOOSE_BEST


def test_an_allowed_plan_passes_and_each_broken_rule_refuses_its_plan():
    assert allows(SNAPSHOT, BASE)
    assert not allows(SNAPSHOT, {"J3": 2027, "J6": 2028})              # must_J1
    assert not allows(SNAPSHOT, {"J1": 2027, "J3": 2027, "J4": 2028})  # alt_G1
    assert not allows(SNAPSHOT, {"J1": 2028, "J4": 2027, "J5": 2027})  # region_South_2027
    assert not allows(SNAPSHOT, {"J1": 2029})                          # no variable: outside J1's window


def test_a_lag_counts_years_between_the_starts():
    assert allows(SNAPSHOT, {"J1": 2028, "J2": 2029})
    assert not allows(SNAPSHOT, {"J1": 2028, "J2": 2028})


def test_a_parent_may_start_earlier_than_the_lag_requires():
    assert allows(SNAPSHOT, {"J1": 2027, "J2": 2029})
    assert not allows(SNAPSHOT, {"J1": 2028, "J2": 2028})


def test_money_lands_in_every_year_of_work():
    assert allows(SNAPSHOT, {"J1": 2028, "J5": 2028, "J6": 2029})
    assert not allows(SNAPSHOT, {"J1": 2028, "J5": 2028, "J6": 2029, "J3": 2029})


def test_crews_work_every_year_of_a_project():
    assert allows(SNAPSHOT, {"J1": 2027, "J2": 2028, "J7": 2029})
    assert not allows(SNAPSHOT, {"J1": 2027, "J2": 2028, "J7": 2028})


def test_a_floor_counts_each_projects_whole_cost():
    higher = variant(floor={"North": 250, "South": 0})
    assert allows(higher, {"J1": 2027, "J6": 2029})
    assert not allows(higher, {"J1": 2027, "J7": 2027})


def test_the_best_plan_with_every_limit_binding_is_worth_the_reference():
    value, plan = best(SNAPSHOT)
    assert abs(value - TIGHT_BEST) <= TOLERANCE
    assert worth(SNAPSHOT, plan) == TIGHT_BEST
