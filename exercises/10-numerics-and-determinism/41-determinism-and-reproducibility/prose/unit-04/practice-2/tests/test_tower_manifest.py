import json

from tower_manifest import manifest_bytes

RECORD = {"inputs_digest": "9f2c1e", "solver": "highs", "params": {"random_seed": 3, "node_limit": 500},
          "versions": {"ortools": "9.15.6755", "python": "3.14.7"},
          "status": "OPTIMAL", "objective": 812.0, "plan": {"TW-12": 2027, "TW-04": 2028, "TW-09": 2027},
          "started_at": "2026-11-11T02:00:03", "wall_seconds": 41.7, "host": "batch-node-7"}
KEPT = {"inputs_digest", "solver", "params", "versions", "status", "objective", "plan"}


def test_the_manifest_keeps_the_run_and_a_new_objective_changes_it():
    manifest = json.loads(manifest_bytes(RECORD))
    assert KEPT <= set(manifest)
    assert manifest["plan"] == RECORD["plan"] and manifest["params"] == RECORD["params"]
    assert manifest_bytes({**RECORD, "objective": 809.0}) != manifest_bytes(RECORD)


def test_two_runs_that_differ_only_in_their_clock_match():
    later = {**RECORD, "started_at": "2026-11-12T02:00:05", "wall_seconds": 44.2}
    assert manifest_bytes(later) == manifest_bytes(RECORD)
    manifest = json.loads(manifest_bytes(RECORD))
    assert "wall_seconds" not in manifest and manifest.get("objective") == 812.0


def test_the_machine_that_ran_it_is_left_out():
    assert manifest_bytes({**RECORD, "host": "batch-node-2"}) == manifest_bytes(RECORD)
    assert b"batch-node" not in manifest_bytes(RECORD)
    assert json.loads(manifest_bytes(RECORD)).get("status") == "OPTIMAL"


def test_the_plan_is_written_in_one_order():
    reordered = {**RECORD, "plan": {"TW-09": 2027, "TW-04": 2028, "TW-12": 2027}}
    assert manifest_bytes(reordered) == manifest_bytes(RECORD)
    assert json.loads(manifest_bytes(reordered)).get("plan") == RECORD["plan"]
