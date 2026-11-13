from checks import checks, required

# A fictional utility's practice portfolio (money in $k). Fields the checks do not read are left out.
SNAPSHOT = {
    "years": [2027, 2028, 2029],
    "budget": {2027: 500, 2028: 500, 2029: 500},
    "crews": {"lines": {2027: 4, 2028: 4, 2029: 4}, "poles": {2027: 3, 2028: 3, 2029: 3}},
    "floor": {"North": 300, "South": 100},
    "projects": {
        "J1": {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027, "latest": 2028,
               "must": True, "group": None, "crews": 2},
        "J2": {"program": "poles", "region": "South", "cost": [150], "earliest": 2027, "latest": 2029,
               "must": True, "group": "G1", "crews": 1},
        "J3": {"program": "poles", "region": "South", "cost": [120], "earliest": 2028, "latest": 2029,
               "must": False, "group": "G1", "crews": 1},
        "J4": {"program": "lines", "region": "North", "cost": [250], "earliest": 2027, "latest": 2029,
               "must": False, "group": None, "crews": 3},
        "J5": {"program": "lines", "region": "North", "cost": [100, 100], "earliest": 2028, "latest": 2028,
               "must": False, "group": None, "crews": 2},
    },
}


def lock(**changes):
    return {"name": "budget-lock", **changes}


def test_a_clean_lock_passes_and_each_rule_fires_on_its_own_error():
    assert checks(SNAPSHOT, lock()) == []
    # J2 may start in 2027, 2028 or 2029, so no single year must carry it: this scenario has a plan.
    assert checks(SNAPSHOT, lock(budget={2027: 210, 2028: 200, 2029: 200})) == []
    assert checks(SNAPSHOT, lock(force_out=["J1"])) == [("no-start", "J1")]
    assert checks(SNAPSHOT, lock(budget={2027: 140, 2028: 140, 2029: 140})) == [
        ("alone-over-budget", "J1"), ("alone-over-budget", "J2")]
    assert checks(SNAPSHOT, lock(budget={2028: 90})) == [
        ("alone-over-budget", "J1"), ("required-over-budget", "2028")]
    assert checks(SNAPSHOT, lock(crews={"lines": {2027: 1, 2028: 1}})) == [("alone-over-crews", "J1")]
    assert checks(SNAPSHOT, lock(fix_start={"J3": 2029})) == [("required-alternatives", "G1")]
    assert checks({**SNAPSHOT, "floor": {"North": 800, "South": 100}}, lock()) == [("floor-out-of-reach", "North")]


def test_a_forced_project_is_required_too():
    assert checks(SNAPSHOT, lock(force_in=["J4"], crews={"lines": {2027: 2, 2028: 2, 2029: 2}})) == [
        ("alone-over-crews", "J4")]


def test_a_fixed_start_leaves_only_that_year():
    # J1 alone fits if it starts in 2027, not in 2028, where 2029's budget is too small for its second year.
    assert checks(SNAPSHOT, lock(budget={2029: 90})) == []
    assert checks(SNAPSHOT, lock(budget={2029: 90}, fix_start={"J1": 2028})) == [
        ("alone-over-budget", "J1"), ("required-over-budget", "2029")]


def test_crews_must_last_every_year_of_the_work():
    # J1 needs 2 lines crew-months in both years of its work; only its second year is short.
    assert checks(SNAPSHOT, lock(crews={"lines": {2028: 1, 2029: 1}})) == [("alone-over-crews", "J1")]


def test_a_project_taken_out_does_not_count_toward_its_regions_floor():
    north = {**SNAPSHOT, "floor": {"North": 400, "South": 100}}
    assert checks(north, lock(force_out=["J4"])) == []
    assert checks(north, lock(force_out=["J4", "J5"])) == [("floor-out-of-reach", "North")]


def test_required_keeps_projects_that_have_no_start_left():
    scenario = lock(force_out=["J1"], fix_start={"J4": 2031})
    assert required(SNAPSHOT, scenario) == {"J1": [2027, 2028], "J2": [2027, 2028, 2029], "J4": [2031]}
    assert checks(SNAPSHOT, scenario) == [("no-start", "J1"), ("no-start", "J4")]
