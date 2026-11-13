import hashlib
from run_harness import NotDeterministic, canonical, differences, harness, manifest

GOOD = {"objective": "npv"}
TIED = {"objective": "count", "order": "set"}       # most projects; many plans tie; projects in a set's order


def test_ten_fresh_runs_give_one_manifest():
    digest = harness(GOOD, runs=10)
    assert digest == hashlib.sha256(canonical(manifest(GOOD))).hexdigest()


def test_the_manifest_records_inputs_solver_versions_and_result_but_no_clock():
    m = manifest(GOOD)
    assert sorted(m) == ["inputs", "result", "solver", "versions"]
    assert m["result"]["status"] == "OPTIMAL" and m["result"]["objective"] == 243
    assert m["result"]["plan"] == [["J1", 2027], ["J2", 2028], ["J3", 2027], ["J4", 2027], ["J5", 2029],
                                   ["J6", 2029], ["J7", 2028]]
    assert len(m["inputs"]["snapshot"]) == 64 and m["solver"]["num_workers"] == 1
    assert "ortools" in m["versions"] and "python" in m["versions"]
    text = canonical(m).decode("ascii").lower()
    assert not any(word in text for word in ("time", "seconds", "host", "user", "/srv", "/path"))


def test_a_tie_broken_by_set_order_fails_the_harness():
    try:
        harness(TIED, runs=4)
        caught = ""
    except NotDeterministic as error:
        caught = str(error)
    assert "result.plan" in caught


def test_differences_names_every_changed_field_by_its_path():
    a = {"inputs": {"snapshot": "s1"}, "result": {"objective": 10, "plan": [["J1", 2027]], "branches": 3}}
    b = {"inputs": {"snapshot": "s1"}, "result": {"objective": 12, "plan": [["J2", 2027]], "branches": 3}}
    assert differences(a, b) == ["result.objective", "result.plan"]
    assert differences(a, a) == []


def test_canonical_bytes_do_not_depend_on_key_order():
    assert canonical({"b": 1, "a": {"d": 2, "c": 3}}) == canonical({"a": {"c": 3, "d": 2}, "b": 1}) \
        == b'{"a":{"c":3,"d":2},"b":1}'


def test_the_input_digest_covers_the_budgets_the_run_used():
    cut = manifest({"objective": "npv", "budget": {"2028": 200}})
    base = manifest(GOOD)
    assert cut.get("inputs", {}).get("snapshot") != base.get("inputs", {}).get("snapshot")
    assert cut.get("result", {}).get("objective", 243) < 243


def test_a_config_leaves_out_what_takes_its_default():
    m = manifest({})
    assert m.get("inputs", {}).get("objective") == "npv" and m.get("inputs", {}).get("order") == "sorted"
    assert m.get("solver", {}).get("random_seed") == 0
    assert manifest({"objective": "npv", "seed": 7}).get("solver", {}).get("random_seed") == 7
