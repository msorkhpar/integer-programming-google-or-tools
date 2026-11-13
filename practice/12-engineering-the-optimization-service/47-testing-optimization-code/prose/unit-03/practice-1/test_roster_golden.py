from roster_golden import compare

GOLDEN = {"status": "OPTIMAL", "cost": 1200.0,
          "assign": {"j1": "red", "j2": "blue", "j3": "red"},
          "overtime": {"red": 2.5, "blue": 0.0}}


def changed(**fields):
    return {**GOLDEN, **fields}


def test_a_matching_record_has_no_lines_and_a_changed_one_names_each_change():
    assert compare(GOLDEN, changed()) == []
    new = changed(cost=1250.0, assign={"j1": "red", "j2": "red", "j3": "red"})
    assert compare(GOLDEN, new) == ["cost: 1200.00 -> 1250.00", "assign: j2 blue -> red"]


def test_cost_within_a_dollar_is_the_same():
    assert compare(GOLDEN, changed(cost=1200.0000004)) == []
    assert compare(GOLDEN, changed(cost=1201.5)) == ["cost: 1200.00 -> 1201.50"]


def test_a_job_only_in_the_new_record_is_reported():
    assert compare(GOLDEN, changed(assign={"j1": "red", "j2": "blue"})) == ["assign: j3 red -> none"]
    new = changed(assign={**GOLDEN["assign"], "j4": "blue"})
    assert compare(GOLDEN, new) == ["assign: j4 none -> blue"]


def test_overtime_near_zero_is_compared_in_hours():
    assert compare(GOLDEN, changed(overtime={"red": 2.5, "blue": 0.004})) == []
    assert compare(GOLDEN, changed(overtime={"red": 2.5, "blue": 0.5})) == ["overtime blue: 0.00 -> 0.50"]


def test_a_changed_status_is_the_only_line():
    new = changed(status="INFEASIBLE", cost=0.0, assign={}, overtime={})
    assert compare(GOLDEN, new) == ["status: OPTIMAL -> INFEASIBLE"]
