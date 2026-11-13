import json
import os
import subprocess
import sys
from itertools import combinations
from pathlib import Path

from weights import separating_weights

HERE = Path(__file__).resolve().parent
IDS = ["S-14", "S-02", "S-09", "S-21", "S-05"]


def test_every_selection_of_a_few_items_gets_its_own_total():
    w = separating_weights(IDS)
    assert set(w) == set(IDS) and all(isinstance(v, int) and v > 0 for v in w.values())
    totals = [sum(w[i] for i in c) for k in range(len(IDS) + 1) for c in combinations(IDS, k)]
    assert len(set(totals)) == len(totals) == 32
    assert max(w.values()) <= 16


def test_the_weights_do_not_depend_on_the_order_of_the_input():
    assert separating_weights(list(reversed(IDS))) == separating_weights(IDS)
    assert len(set(separating_weights(IDS).values())) == len(IDS)


def in_fresh_process(seed: str) -> dict:
    code = f"import json; from weights import separating_weights; print(json.dumps(separating_weights({IDS!r})))"
    env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(HERE)}
    out = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_the_weights_are_the_same_in_every_process():
    assert in_fresh_process("1") == in_fresh_process("2") == in_fresh_process("3")
    assert len(set(in_fresh_process("1").values())) == len(IDS)
