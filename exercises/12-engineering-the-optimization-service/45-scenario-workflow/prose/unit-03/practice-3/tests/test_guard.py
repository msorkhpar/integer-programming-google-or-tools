import copy

from guard import lock_refusal

GOOD = {"year": 2028, "state": "Reviewed", "inputs_hash": "a1", "run": {"inputs_hash": "a1", "status": "OPTIMAL"}}


def plans(**edits) -> dict:
    p = copy.deepcopy(GOOD)
    p.update(edits)
    return {"D-1": p, "D-2": {**copy.deepcopy(GOOD), "state": "Draft"}}


def test_a_reviewed_plan_with_a_current_optimal_run_may_lock():
    assert lock_refusal("D-1", plans()) is None
    assert lock_refusal("D-1", plans(state="Draft")) is not None


def test_a_run_on_older_inputs_does_not_count():
    assert lock_refusal("D-1", plans(inputs_hash="b7")) is not None
    assert lock_refusal("D-1", plans(run=None)) is not None
    assert lock_refusal("D-1", plans()) is None


def test_an_infeasible_run_is_not_a_program():
    assert lock_refusal("D-1", plans(run={"inputs_hash": "a1", "status": "INFEASIBLE"})) is not None
    assert lock_refusal("D-1", plans()) is None


def test_one_program_of_record_per_year():
    p = plans()
    p["D-3"] = {**copy.deepcopy(GOOD), "state": "Locked"}
    assert lock_refusal("D-1", p) is not None
    p["D-3"]["year"] = 2029
    assert lock_refusal("D-1", p) is None
