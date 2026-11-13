"""The module 41 examples: the model's two questions, tie-breaks, canonical manifests and the harness."""

import pytest
from ortools.math_opt.python import mathopt

from gridcap import generate
from harness import NotDeterministic, check, diff
from lexicographic import two_pass_cpsat, two_pass_highs
from manifest import canonical, sha256
from pinned import check_pins
from plan_model import build, digest, schedule, solve_highs
from solve_once import run
from tie_weights import weights

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
HIGHS = {"size": "small", "objective": "npv", "solver": "highs", "params": {"relative_gap_tolerance": 0.0}}
CPSAT = {"size": "small", "objective": "npv", "solver": "cpsat", "params": {"num_workers": 1, "random_seed": 7}}
SET_ORDER = {"size": "small", "objective": "count", "order": "set", "solver": "highs",
             "params": {"relative_gap_tolerance": 0.0}}


@pytest.fixture(scope="module")
def small():
    return generate("small")


def test_the_two_questions_on_gridcap_small(small):
    for objective, value in [("npv", 24260), ("count", 33)]:
        plan = build(small, objective=objective)
        assert round(solve_highs(plan.model, EXACT).objective_value()) == value


def test_the_build_order_does_not_change_the_model_value(small):
    ids = list(small.project_ids)
    values = {round(solve_highs(build(small, order, "count").model, EXACT).objective_value())
              for order in (None, ids[::-1], sorted(ids, key=lambda i: i[::-1]))}
    assert values == {33}


def test_the_plan_digest_ignores_insertion_order():
    assert digest({"P001": 2028, "P003": 2031}) == digest({"P003": 2031, "P001": 2028})
    assert digest({"P001": 2028}) != digest({"P001": 2029})


def test_two_passes_give_one_plan_on_both_solvers(small):
    order = sorted(small.project_ids, reverse=True)
    highs, cpsat = two_pass_highs(small, order), two_pass_cpsat(small, order)
    assert (highs["count"], highs["npv"], highs["another plan"]) == (33, 20082, "INFEASIBLE")
    assert cpsat["plan"] == highs["plan"]


def test_rank_and_digest_weights_do_not_depend_on_the_input_order():
    keys = [("P002", 2027), ("P001", 2028), ("P001", 2027)]
    for kind in ("rank", "sha256"):
        assert weights(keys, kind) == weights(keys[::-1], kind)
    assert sorted(weights(keys, "rank").values()) == [1, 2, 3]


def test_canonical_bytes_ignore_key_order():
    assert canonical({"b": 1, "a": [2, 3]}) == canonical({"a": [2, 3], "b": 1}) == b'{"a":[2,3],"b":1}'
    assert sha256({"a": 1}) != sha256({"a": 2})


def test_the_manifest_keeps_the_clock_out():
    record = run(HIGHS)
    assert set(record) == {"manifest", "clock"}
    assert "wall_seconds" not in canonical(record["manifest"]).decode()
    assert record["manifest"]["result"]["plan_digest"] == "092777a3fdd1"


def test_pins_report_only_mismatches():
    assert check_pins({}) == []
    assert check_pins({"ortools": "0.0"})[0].startswith("ortools: pinned 0.0, found ")


def test_diff_names_nested_paths_and_missing_keys():
    a = {"result": {"objective": 1.0, "plan": [["P1", 2027]]}, "inputs": {"size": "small"}}
    b = {"result": {"objective": 2.0, "plan": [["P1", 2027]], "bound": 3.0}, "inputs": {"size": "small"}}
    assert diff(a, b) == ["result.bound", "result.objective"]
    assert diff(a, a) == []


def test_the_harness_passes_on_highs_and_cpsat():
    for config in (HIGHS, CPSAT):
        manifest, manifest_digest = check(config, runs=3)
        assert manifest["result"]["status"] == "OPTIMAL" and len(manifest_digest) == 64


def test_the_harness_fails_on_a_model_built_from_a_set():
    with pytest.raises(NotDeterministic, match="result.plan"):
        check(SET_ORDER, runs=3)
