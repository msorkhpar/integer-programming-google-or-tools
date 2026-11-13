import os
import re
import subprocess
import sys
from pathlib import Path

from fingerprint import fingerprint

HERE = Path(__file__).resolve().parent
PLAN = {"M03": 2027, "M07": 2028, "M12": 2027, "M20": 2030}


def test_equal_plans_share_an_id_and_a_changed_year_changes_it():
    assert re.fullmatch(r"[0-9a-f]{16}", fingerprint(PLAN))
    assert fingerprint(dict(PLAN)) == fingerprint(PLAN)
    assert fingerprint({**PLAN, "M07": 2029}) != fingerprint(PLAN)


def test_the_order_the_plan_was_built_in_does_not_matter():
    backwards = dict(reversed(list(PLAN.items())))
    assert fingerprint(backwards) == fingerprint(PLAN)
    assert fingerprint({**backwards, "M20": 2031}) != fingerprint(PLAN)


def in_fresh_process(seed: str) -> str:
    code = f"from fingerprint import fingerprint; print(fingerprint({PLAN!r}))"
    env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(HERE)}
    return subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_the_id_is_the_same_in_every_process():
    assert in_fresh_process("1") == in_fresh_process("2") == fingerprint(PLAN)
    assert fingerprint({"M03": 2027}) != fingerprint(PLAN)


def test_ids_and_years_cannot_run_together():
    assert fingerprint({"M1": 12}) != fingerprint({"M11": 2})
    assert fingerprint({"M1": 12}) == fingerprint({"M1": 12})
