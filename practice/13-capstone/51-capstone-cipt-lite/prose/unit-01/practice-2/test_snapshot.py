import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from snapshot import Edited, Store, canonical, digest

# A fictional utility's practice snapshot, as milestone 1's reader builds it. Money in $k.
SNAPSHOT = {
    "years": [2027, 2028, 2029], "rate": 0.05,
    "budget": {2027: 400, 2028: 400, 2029: 380},
    "region_budget": {"North": {2027: 250, 2028: 250, 2029: 250}, "South": {2027: 200, 2028: 200, 2029: 200}},
    "crews": {"lines": {2027: 3, 2028: 3, 2029: 3}, "poles": {2027: 2, 2028: 2, 2029: 2}},
    "floor": {"North": 100, "South": 0},
    "projects": {
        "J1": {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027, "latest": 2028,
               "must": True, "parent": None, "lag": 0, "group": None, "crews": 2, "npv": {2027: 90, 2028: 80}},
        "J2": {"program": "poles", "region": "South", "cost": [120], "earliest": 2027, "latest": 2029,
               "must": False, "parent": None, "lag": 0, "group": "G1", "crews": 1,
               "npv": {2027: 40, 2028: 36, 2029: 31}},
        "J3": {"program": "lines", "region": "North", "cost": [150], "earliest": 2028, "latest": 2029,
               "must": False, "parent": "J1", "lag": 1, "group": None, "crews": 2, "npv": {2028: 55, 2029: 50}},
    },
}
#: The digest the planning team pinned for SNAPSHOT, from the documented byte form.
PINNED = "683bc11dd4c1d3405c79a2ea58f36a2ba226a0de37b85c9d5fbdf79f4792f794"


def refused(call, error) -> bool:
    """Did `call()` raise `error`?"""
    try:
        call()
    except error:
        return True
    return False


def reordered(snap: dict) -> dict:
    """The same content with every dictionary's keys in reverse order."""
    if isinstance(snap, dict):
        return {k: reordered(snap[k]) for k in reversed(list(snap))}
    if isinstance(snap, list):
        return [reordered(v) for v in snap]
    return snap


def changed(**edits) -> dict:
    doc = copy.deepcopy(SNAPSHOT)
    for path, value in edits.items():
        *keys, last = path.split("__")
        node = doc
        for k in keys:
            node = node[int(k) if k.isdigit() else k]
        node[int(last) if last.isdigit() else last] = value
    return doc


def test_the_same_content_in_another_order_has_the_same_digest_and_a_real_change_a_new_one():
    first = digest(SNAPSHOT)
    assert len(first) == 64 and all(c in "0123456789abcdef" for c in first)
    assert digest(reordered(SNAPSHOT)) == first
    assert digest(changed(projects__J2__cost=[130])) != first
    assert digest(changed(budget__2029=390)) != first


def test_a_rate_equal_to_six_decimals_is_the_same_rate():
    assert digest(changed(rate=0.0500000001)) == digest(SNAPSHOT)
    assert digest(changed(rate=0.050001)) != digest(SNAPSHOT)


def test_a_cost_profile_keeps_its_order():
    assert digest(changed(projects__J1__cost=[100, 200])) != digest(SNAPSHOT)


def test_nan_is_refused():
    assert refused(lambda: canonical(changed(rate=float("nan"))), ValueError)


def test_the_digest_is_the_documented_one():
    assert canonical({"b": [2, 1], "a": "é", "c": 0.1 + 0.2}) == b'{"a":"\\u00e9","b":[2,1],"c":0.3}'
    assert digest(SNAPSHOT) == PINNED


def test_two_fresh_processes_give_the_same_digest():
    here = Path(__file__).resolve().parent
    code = "import json, sys; from snapshot import digest; print(digest(json.loads(sys.argv[1])))"
    doc = json.dumps(SNAPSHOT)
    found = set()
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(here)}
        found.add(subprocess.run([sys.executable, "-c", code, doc], env=env, capture_output=True, text=True,
                                 cwd=here).stdout.strip())
    loaded = digest(json.loads(doc))
    assert found == {loaded} and loaded


def test_the_store_keeps_one_file_per_content_and_reads_it_back(tmp_path):
    store = Store(tmp_path / "snapshots")
    key = store.put(SNAPSHOT)
    assert key == digest(SNAPSHOT)
    assert store.put(reordered(SNAPSHOT)) == key
    assert [p.name for p in (tmp_path / "snapshots").iterdir()] == [f"{key}.json"]
    assert canonical(store.get(key)) == canonical(SNAPSHOT)


def edit_in_place(tmp_path, key: str) -> None:
    path = tmp_path / "snapshots" / f"{key}.json"
    assert key and path.is_file(), "put wrote no <digest>.json"
    path.write_bytes(path.read_bytes().replace(b'"2029":380', b'"2029":480'))


def test_an_edited_file_is_refused(tmp_path):
    store = Store(tmp_path / "snapshots")
    key = store.put(SNAPSHOT)
    edit_in_place(tmp_path, key)
    assert refused(lambda: store.get(key), Edited)


def test_a_stored_file_is_never_rewritten(tmp_path):
    store = Store(tmp_path / "snapshots")
    key = store.put(SNAPSHOT)
    edit_in_place(tmp_path, key)
    assert store.put(SNAPSHOT) == key
    assert refused(lambda: store.get(key), Edited)
