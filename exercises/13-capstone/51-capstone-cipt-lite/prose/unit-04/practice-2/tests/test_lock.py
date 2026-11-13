import copy

from lock import build, conflict, feasible, message

# A fictional utility's practice portfolio (money in $k).
SNAPSHOT = {
    "years": [2027, 2028, 2029],
    "rate": 0.05,
    "budget": {2027: 600, 2028: 600, 2029: 600},
    "region_budget": {"North": {2027: 500, 2028: 500, 2029: 500}, "South": {2027: 400, 2028: 400, 2029: 400}},
    "crews": {"lines": {2027: 6, 2028: 6, 2029: 6}, "poles": {2027: 4, 2028: 4, 2029: 4}},
    "floor": {"North": 0, "South": 0},
    "projects": {
        "J1": {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027, "latest": 2028,
               "must": True, "parent": None, "lag": 0, "group": None, "crews": 2, "npv": {2027: 90, 2028: 80}},
        "J2": {"program": "lines", "region": "North", "cost": [150], "earliest": 2028, "latest": 2028,
               "must": True, "parent": None, "lag": 0, "group": None, "crews": 2, "npv": {2028: 60}},
        "J3": {"program": "poles", "region": "South", "cost": [250], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": "G1", "crews": 1, "npv": {2027: 70, 2028: 65, 2029: 60}},
        "J4": {"program": "poles", "region": "South", "cost": [120], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": "G1", "crews": 1, "npv": {2027: 30, 2028: 28, 2029: 26}},
        "J5": {"program": "lines", "region": "North", "cost": [100, 100], "earliest": 2028, "latest": 2028,
               "must": False, "parent": "J1", "lag": 0, "group": None, "crews": 1, "npv": {2028: 40}},
    },
}
LOCK = {"name": "lock-2028", "budget": {2029: 300}, "crews": {"lines": {2027: 4, 2028: 3}}}

EXPECTED = """\
Budget Lock 'lock-2028' has no plan. These 3 rules cannot all hold:
- Lines crews have 3 crew-months in 2028 (snapshot: 6).
- J1 (must-do) has to start in 2027 or 2028.
- J2 (must-do) has to start in 2028.
Every way to start J1, J2 runs out:
- J1 2027, J2 2028: lines crews in 2028 need 4, have 3.
- J1 2028, J2 2028: lines crews in 2028 need 4, have 3.
Smallest change, checked by a solve: lines crews in 2028 at 4 instead of 3."""


def test_the_budget_lock_scenario_yields_the_expected_message():
    assert message(SNAPSHOT, LOCK) == EXPECTED


def test_families_are_filtered_before_their_rows():
    rows, solves = conflict(build(SNAPSHOT, LOCK))
    assert rows == ["crews_lines_2028", "must_J1", "must_J2"]
    assert solves == 13


def test_the_filter_leaves_the_model_as_it_found_it():
    b = build(SNAPSHOT, LOCK)
    assert conflict(b)[0] == ["crews_lines_2028", "must_J1", "must_J2"]
    assert b.rows["budget_2029"].upper_bound == 300 and b.rows["crews_lines_2027"].upper_bound == 4
    assert not feasible(b)


def test_a_forced_project_is_a_limit_the_filter_can_name():
    poles_cut = {"name": "poles-cut", "force_in": ["J4"], "crews": {"poles": {2027: 0, 2028: 0, 2029: 0}}}
    assert message(SNAPSHOT, poles_cut) == """\
Budget Lock 'poles-cut' has no plan. These 4 rules cannot all hold:
- Poles crews have 0 crew-months in 2027 (snapshot: 4).
- Poles crews have 0 crew-months in 2028 (snapshot: 4).
- Poles crews have 0 crew-months in 2029 (snapshot: 4).
- J4 was forced into the plan.
Every way to start J4 runs out:
- J4 2027: poles crews in 2027 need 1, have 0.
- J4 2028: poles crews in 2028 need 1, have 0.
- J4 2029: poles crews in 2029 need 1, have 0.
Smallest change, checked by a solve: poles crews in 2027 at 1 instead of 0."""


def test_the_change_offered_is_the_smallest_that_works():
    money = {"name": "money-lock", "budget": {2027: 150, 2028: 250}}
    assert message(SNAPSHOT, money).splitlines()[-3:] == [
        "- J1 2027, J2 2028: the 2027 budget needs $200k, has $150k.",
        "- J1 2028, J2 2028: the 2028 budget needs $350k, has $250k.",
        "Smallest change, checked by a solve: the 2027 budget at $200k instead of $150k."]


def test_a_fixed_start_takes_part_in_the_arithmetic():
    fixed = {"name": "fixed", "fix_start": {"J1": 2028}, "crews": {"lines": {2028: 3}}}
    assert message(SNAPSHOT, fixed).splitlines()[3:6] == [
        "- J1 is fixed by this scenario to start in 2028.",
        "Every way to start J2, J1 runs out:",
        "- J2 2028, J1 2028: lines crews in 2028 need 4, have 3."]


def big(figure_2027):
    """SNAPSHOT with J1's first year at $1,200k, budgets above $1,000k and regions out of the way."""
    snap = copy.deepcopy(SNAPSHOT)
    snap["budget"] = {2027: figure_2027, 2028: 1300, 2029: 1300}
    snap["region_budget"] = {r: {y: 5000 for y in snap["years"]} for r in ("North", "South")}
    snap["projects"]["J1"]["cost"] = [1200, 100]
    return snap


BIG_LOCK = {"name": "big-lock", "budget": {2027: 1195}}


def test_amounts_of_a_thousand_or_more_carry_a_thousands_separator():
    assert message(big(1205), BIG_LOCK).splitlines()[-3:] == [
        "- J1 2027, J2 2028: the 2027 budget needs $1,200k, has $1,195k.",
        "- J1 2028, J2 2028: the 2028 budget needs $1,350k, has $1,300k.",
        "Smallest change, checked by a solve: the 2027 budget at $1,205k instead of $1,195k."]


def test_the_raises_never_pass_the_snapshot_figure():
    # From $1,195k in $10k steps, the next step, $1,205k, is past the snapshot's $1,203k: no change is offered.
    assert message(big(1203), BIG_LOCK).splitlines()[-1:] == ["No single number of the scenario ends it."]
