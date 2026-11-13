from gas_plan import diff_scenarios

SPRING = {"name": "spring", "plan": [
    {"id": "PR-11", "start": "2028-Q1"},
    {"id": "PR-12", "start": "2028-Q3"},
    {"id": "PR-15", "start": "2029-Q2"},
    {"id": "PR-20", "start": "2028-Q4"},
]}
SUMMER = {"name": "summer", "plan": [
    {"id": "PR-31", "start": "2028-Q2"},
    {"id": "PR-20", "start": "2029-Q1"},
    {"id": "PR-15", "start": "2028-Q4"},
    {"id": "PR-12", "start": "2028-Q3"},
]}


def shift(diff: dict, pid: str):
    return next((s for s in diff["shifts"] if s["id"] == pid), None)


def test_adds_and_drops_are_matched_by_project_not_by_position():
    d = diff_scenarios(SPRING, SUMMER)
    assert (d["adds"], d["drops"]) == (["PR-31"], ["PR-11"])


def test_a_project_with_the_same_start_is_not_a_shift():
    assert [s["id"] for s in diff_scenarios(SPRING, SUMMER)["shifts"]] == ["PR-15", "PR-20"]


def test_a_shift_across_new_year_counts_one_quarter():
    assert shift(diff_scenarios(SPRING, SUMMER), "PR-20") == {
        "id": "PR-20", "from": "2028-Q4", "to": "2029-Q1", "quarters": 1}


def test_an_earlier_start_is_a_negative_shift():
    assert (shift(diff_scenarios(SPRING, SUMMER), "PR-15") or {}).get("quarters") == -2
