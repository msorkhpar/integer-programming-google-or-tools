import json
import os
import re
import subprocess
import sys
from pathlib import Path

from snapshots import snapshot_digest

# A transit agency's scenario, not the lessons' portfolio.
SNAPSHOT = {
    "scenario": "budget-cut",
    "budgets": {"2027": 900, "2028": 950},
    "projects": [
        {"pid": "T2", "cost": 300, "region": "North"},
        {"pid": "T1", "cost": 450, "region": "South"},
        {"pid": "T3", "cost": 200, "region": "North"},
    ],
    "must_do": ["T3", "T1"],
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def test_equal_content_gives_equal_digests_and_a_change_a_new_one():
    reordered = {"must_do": ["T3", "T1"], "projects": SNAPSHOT["projects"], "scenario": "budget-cut",
                 "budgets": {"2028": 950, "2027": 900}}
    assert snapshot_digest(reordered) == snapshot_digest(SNAPSHOT)
    cut = json.loads(json.dumps(SNAPSHOT))
    cut["budgets"]["2028"] = 949
    assert snapshot_digest(cut) != snapshot_digest(SNAPSHOT)


def test_an_added_project_changes_the_digest():
    grown = json.loads(json.dumps(SNAPSHOT))
    grown["projects"].append({"pid": "T4", "cost": 50, "region": "South"})
    assert snapshot_digest(grown) != snapshot_digest(SNAPSHOT)


def test_the_order_of_the_projects_does_not_matter():
    shuffled = dict(SNAPSHOT, projects=list(reversed(SNAPSHOT["projects"])))
    assert HEX64.match(snapshot_digest(SNAPSHOT))
    assert snapshot_digest(shuffled) == snapshot_digest(SNAPSHOT)


def test_the_order_of_the_must_do_list_does_not_matter():
    swapped = dict(SNAPSHOT, must_do=["T1", "T3"])
    assert HEX64.match(snapshot_digest(SNAPSHOT))
    assert snapshot_digest(swapped) == snapshot_digest(SNAPSHOT)


def test_the_digest_is_the_same_in_fresh_processes():
    code = "import json, sys; from snapshots import snapshot_digest; print(snapshot_digest(json.loads(sys.argv[1])))"
    digests = set()
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(Path(__file__).resolve().parent)}
        done = subprocess.run([sys.executable, "-c", code, json.dumps(SNAPSHOT)], env=env,
                              capture_output=True, text=True, check=True)
        digests.add(done.stdout.strip())
    assert len(digests) == 1
    assert HEX64.match(digests.pop())


def test_the_canonical_form_is_the_one_specified():
    small = {"scenario": "s", "budgets": {"2027": 1}, "projects": [{"pid": "A", "cost": 1}], "must_do": ["A"]}
    assert snapshot_digest(small) == "a626fde6b9319be0430a4986dde7673abfe4d066bd3a01dbd7fc684fc4c458f6"
