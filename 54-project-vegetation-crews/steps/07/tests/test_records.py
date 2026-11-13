"""The same plan every run: records, golden files and fresh processes (lesson 14.1.7).

To accept a new plan on purpose, write the golden file again and review its diff:
    python -m vegcrew small --record > tests/golden/small.json
"""

import json
import subprocess
import sys
from pathlib import Path

from vegcrew.data import Override, season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
from vegcrew.record import dumps, fingerprint, plan_record

GOLDEN = Path(__file__).parent / "golden"
ROOT = Path(__file__).parents[1]


def record_of(size):
    raw = scenario(size)
    return dumps(plan_record(raw, make_plan(season_from_dict(raw))))


def test_the_fingerprint_changes_with_the_input_and_nothing_else():
    raw = scenario("tiny")
    assert fingerprint(raw) == fingerprint(json.loads(json.dumps(raw))) != ""
    assert fingerprint(raw) != fingerprint(raw | {"budget": raw["budget"] + 1})
    assert fingerprint(raw) != fingerprint(raw, (Override("skip", "C01"),))


def test_the_record_names_its_input_solver_and_settings():
    record = json.loads(record_of("tiny"))
    assert record.get("input_sha256") == fingerprint(scenario("tiny"))
    settings = record.get("settings", {})
    assert settings.get("random_seed") == 7 and settings.get("num_workers", 0) <= 4
    assert str(record.get("ortools")).count(".") == 2


def test_the_tiny_plan_matches_its_golden_record():
    assert json.loads(record_of("tiny")) == json.loads((GOLDEN / "tiny.json").read_text())


def test_the_small_plan_matches_its_golden_record():
    assert json.loads(record_of("small")) == json.loads((GOLDEN / "small.json").read_text())


def test_two_fresh_processes_print_the_golden_record_byte_for_byte():
    runs = [subprocess.run([sys.executable, "-m", "vegcrew", "tiny", "--record"], cwd=ROOT,
                           capture_output=True, text=True) for _ in range(2)]
    assert [r.returncode for r in runs] == [0, 0]
    assert runs[0].stdout == runs[1].stdout == (GOLDEN / "tiny.json").read_text()
