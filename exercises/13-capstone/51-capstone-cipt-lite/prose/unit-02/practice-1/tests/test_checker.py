from checker import broken

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
BASE = {"J1": 2027, "J2": 2028, "J3": 2027, "J6": 2029}


def test_each_rule_names_its_row_and_an_allowed_plan_breaks_none():
    assert broken(SNAPSHOT, BASE) == []
    assert broken(SNAPSHOT, {"J3": 2027, "J6": 2028}) == ["must_J1"]
    assert broken(SNAPSHOT, {"J1": 2027, "J3": 2027, "J4": 2028}) == ["alt_G1"]
    assert broken(SNAPSHOT, {"J1": 2028, "J4": 2027, "J5": 2027}) == ["region_South_2027"]
    assert broken(SNAPSHOT, {"J1": 2029}) == ["window_J1"]


def test_a_lag_counts_years_between_the_starts():
    assert broken(SNAPSHOT, {"J1": 2028, "J2": 2029}) == []
    assert broken(SNAPSHOT, {"J1": 2028, "J2": 2028}) == ["after_J2_2028"]


def test_a_child_without_its_parent_breaks_its_row():
    assert broken(SNAPSHOT, {"J1": 2027, "J2": 2029}) == []
    assert broken(SNAPSHOT, {"J2": 2029}) == ["after_J2_2029", "must_J1"]


def test_money_lands_in_every_year_of_work():
    assert broken(SNAPSHOT, {"J1": 2028, "J5": 2028, "J6": 2029}) == []
    assert broken(SNAPSHOT, {"J1": 2028, "J5": 2028, "J6": 2029, "J3": 2029}) == ["budget_2029"]


def test_spend_equal_to_the_budget_is_allowed():
    assert broken(SNAPSHOT, {"J1": 2027, "J6": 2028, "J5": 2028}) == []
    assert broken(SNAPSHOT, {"J1": 2027, "J6": 2028, "J5": 2028, "J7": 2028}) == ["budget_2028"]


def test_crews_work_every_year_of_a_project():
    assert broken(SNAPSHOT, {"J1": 2027, "J2": 2028, "J7": 2029}) == []
    assert broken(SNAPSHOT, {"J1": 2027, "J2": 2028, "J7": 2028}) == ["crews_lines_2028"]


def test_a_floor_counts_each_projects_whole_cost():
    higher = {**SNAPSHOT, "floor": {"North": 250, "South": 0}}
    assert broken(higher, {"J1": 2027, "J6": 2029}) == []
    assert broken(higher, {"J1": 2027, "J7": 2027}) == ["floor_North"]


def test_a_region_or_program_without_a_limit_is_unlimited():
    north_only = {**SNAPSHOT, "region_budget": {"North": SNAPSHOT["region_budget"]["North"]},
                  "crews": {"lines": SNAPSHOT["crews"]["lines"]}}
    plan = {"J1": 2028, "J4": 2027, "J5": 2027}
    assert broken(SNAPSHOT, plan) == ["region_South_2027"]
    assert broken(north_only, plan) == []
