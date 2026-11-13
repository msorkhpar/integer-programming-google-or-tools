from manifest_diff import diff_paths

RUN = {"inputs": {"snapshot": "a41f", "track": "north"},
       "result": {"status": "OPTIMAL", "objective": 41.0, "plan": [["S1", 3], ["S4", 1], ["S7", 2]]}}


def copy(m):
    return {"inputs": dict(m["inputs"]), "result": {**m["result"], "plan": [list(p) for p in m["result"]["plan"]]}}


def test_equal_manifests_and_one_changed_value():
    assert diff_paths(RUN, copy(RUN)) == []
    other = copy(RUN)
    other["result"]["objective"] = 39.0
    assert diff_paths(RUN, other) == ["result.objective"]


def test_a_field_only_one_run_wrote_is_a_difference():
    other = copy(RUN)
    other["result"]["bound"] = 44.0
    assert diff_paths(RUN, other) == ["result.bound"]
    assert diff_paths(other, RUN) == ["result.bound"]


def test_every_difference_is_reported_not_the_first():
    other = copy(RUN)
    other["result"]["objective"] = 39.0
    other["inputs"]["snapshot"] = "b220"
    other["result"]["status"] = "FEASIBLE"
    assert diff_paths(RUN, other) == ["inputs.snapshot", "result.objective", "result.status"]


def test_list_items_are_compared_one_by_one():
    other = copy(RUN)
    other["result"]["plan"][1] = ["S4", 2]
    assert diff_paths(RUN, other) == ["result.plan[1][1]"]
    shorter = copy(RUN)
    shorter["result"]["plan"] = shorter["result"]["plan"][:2]
    assert diff_paths(RUN, shorter) == ["result.plan"]


def test_a_change_of_kind_differs_but_int_and_float_are_compared_by_value():
    other = copy(RUN)
    other["inputs"]["track"] = ["north"]
    assert diff_paths(RUN, other) == ["inputs.track"]
    same = copy(RUN)
    same["result"]["objective"] = 41
    assert diff_paths(RUN, same) == []
