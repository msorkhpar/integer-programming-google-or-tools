import os
import re
import subprocess
import sys
from pathlib import Path

from scenario import snapshot_digest

HERE = Path(__file__).resolve().parent
INPUTS = {"budget": {"2027": 4200, "2028": 3900, "2029": 4100},
          "force_in": {"T-07", "T-11", "T-02", "T-19", "T-05", "T-13"},
          "settings": {"gap": 0.0, "solver": "highs", "seed": 3}}


def test_equal_inputs_share_a_digest_and_an_edit_changes_it():
    assert re.fullmatch(r"[0-9a-f]{64}", snapshot_digest(INPUTS))
    assert snapshot_digest(INPUTS) == snapshot_digest(dict(INPUTS))
    edited = {**INPUTS, "budget": {**INPUTS["budget"], "2028": 3800}}
    assert snapshot_digest(edited) != snapshot_digest(INPUTS)


def test_the_order_dicts_were_built_in_does_not_matter():
    rebuilt = {"settings": {"seed": 3, "solver": "highs", "gap": 0.0},
               "force_in": set(INPUTS["force_in"]),
               "budget": {"2029": 4100, "2028": 3900, "2027": 4200}}
    assert snapshot_digest(rebuilt) == snapshot_digest(INPUTS)
    assert snapshot_digest({**rebuilt, "force_in": {"T-07"}}) != snapshot_digest(INPUTS)


def in_fresh_process(seed: str) -> str:
    code = f"from scenario import snapshot_digest; print(snapshot_digest({INPUTS!r}))"
    env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(HERE)}
    return subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_a_set_of_ids_digests_the_same_in_every_process():
    assert in_fresh_process("1") == in_fresh_process("2") == in_fresh_process("3")
    assert in_fresh_process("1") != snapshot_digest({**INPUTS, "force_in": set()})
