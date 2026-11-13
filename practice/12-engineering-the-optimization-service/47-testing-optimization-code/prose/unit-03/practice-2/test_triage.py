from triage import classify

GOLDEN = {"input": "9f2c", "status": "OPTIMAL", "cost": 980.0, "assign": {"j1": "red", "j2": "blue"}}


def changed(**fields):
    return {**GOLDEN, **fields}


def test_an_identical_record_is_same_and_new_data_is_input():
    assert classify(GOLDEN, changed()) == "same"
    assert classify(GOLDEN, changed(input="51ab", cost=1010.0)) == "input"


def test_a_cheaper_roster_is_better_and_a_dearer_one_worse():
    assert classify(GOLDEN, changed(cost=940.0, assign={"j1": "red", "j2": "red"})) == "better"
    assert classify(GOLDEN, changed(cost=1015.0, assign={"j1": "blue", "j2": "blue"})) == "worse"


def test_equal_cost_with_another_roster_is_a_tie():
    assert classify(GOLDEN, changed(cost=980.0000003, assign={"j1": "blue", "j2": "red"})) == "tie"
    assert classify(GOLDEN, changed(cost=980.0000003)) == "same"


def test_new_input_outranks_a_new_status():
    assert classify(GOLDEN, changed(input="51ab", status="INFEASIBLE")) == "input"
    assert classify(GOLDEN, changed(status="INFEASIBLE")) == "status"
