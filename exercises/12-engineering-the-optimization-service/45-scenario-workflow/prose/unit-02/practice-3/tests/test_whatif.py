from whatif import Plan, Project, copy_with_overrides, diff, solve, what_if

MAINS = [
    Project("M-1", (300, 200), {2027: 900, 2028: 820, 2029: 700}),
    Project("M-2", (250,), {2027: 400, 2028: 380, 2029: 350}),
    Project("M-3", (350,), {2028: 560, 2029: 520}),
    Project("M-4", (200, 200), {2027: 380, 2028: 360}),
    Project("M-5", (150,), {2029: 210}),
]
BUDGET = {2027: 600, 2028: 600, 2029: 600}
THREE = {"M-1": ("start_in", 2029), "M-2": ("out", None), "M-5": ("out", None)}


def base() -> Plan:
    return Plan("W-1", dict(BUDGET), {"M-4": ("out", None)})


def test_the_copy_carries_the_three_overrides_and_solves_with_them():
    trial = copy_with_overrides(base(), "W-2", THREE)
    assert trial.overrides == {"M-4": ("out", None), **THREE} and trial.budget == BUDGET
    assert solve(trial, MAINS) == {"M-1": 2029, "M-3": 2028}


def test_three_overrides_give_the_expected_diff():
    assert solve(base(), MAINS) == {"M-1": 2027, "M-2": 2027, "M-3": 2028, "M-5": 2029}
    _, d = what_if(base(), "W-2", THREE, MAINS)
    assert d == {"selected": [], "deferred": ["M-2", "M-5"], "shifted": [("M-1", 2027, 2029)]}


def test_the_base_plan_keeps_its_own_overrides_and_budgets():
    b = base()
    trial, _ = what_if(b, "W-2", THREE, MAINS)
    assert b.overrides == {"M-4": ("out", None)} and b.budget == BUDGET
    assert trial.overrides == {"M-4": ("out", None), **THREE} and trial.parent_id == "W-1"


def test_a_project_that_changes_year_is_shifted_not_dropped_and_added():
    assert diff({"M-1": 2027, "M-3": 2028}, {"M-1": 2028, "M-3": 2028}) == {
        "selected": [], "deferred": [], "shifted": [("M-1", 2027, 2028)]}


def test_selected_means_new_in_the_second_plan():
    assert diff({"M-1": 2027}, {"M-1": 2027, "M-4": 2028}) == {
        "selected": ["M-4"], "deferred": [], "shifted": []}
