import copy
import re

from snapshot import snapshot

PLAN = {"id": "W-1", "name": "base", "owner": "analyst-a", "created": "2027-01-04T08:00Z",
        "demand": {"north": 41, "south": 37, "east": 12},
        "budget": {2027: 900, 2028: 950, 2029: 990},
        "settings": {"solver": "HIGHS", "gap": 0.0}}


def changed(**edits):
    plan = copy.deepcopy(PLAN)
    for key, value in edits.items():
        plan[key] = value
    return plan


def test_metadata_does_not_change_the_snapshot():
    renamed = changed(id="W-7", name="reviewed", owner="analyst-b", created="2027-02-01T10:00Z")
    assert snapshot(renamed) == snapshot(PLAN)
    assert snapshot(changed(budget={2027: 900, 2028: 950, 2029: 991})) != snapshot(PLAN)


def test_the_order_entries_were_added_does_not_matter():
    reordered = changed(demand={"east": 12, "south": 37, "north": 41}, budget={2029: 990, 2027: 900, 2028: 950})
    assert snapshot(reordered) == snapshot(PLAN)
    assert snapshot(changed(demand={"north": 41, "south": 38, "east": 12})) != snapshot(PLAN)


def test_solver_settings_are_inputs():
    assert snapshot(changed(settings={"solver": "HIGHS", "gap": 0.01})) != snapshot(PLAN)
    assert snapshot(copy.deepcopy(PLAN)) == snapshot(PLAN)


def test_the_snapshot_is_a_sha256_hex_digest():
    digest = snapshot(PLAN)
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert digest != snapshot(changed(demand={"north": 0, "south": 0, "east": 0}))
