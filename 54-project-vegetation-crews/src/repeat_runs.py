"""Lesson 14.1.7: the medium season planned three times by steps/06 (four racing workers, a 10-second
clock) and twice by steps/07 (interleaved workers, a seed, a limit on deterministic time), each run
in a fresh process. About a minute in all."""

import hashlib
import json
import subprocess
import sys

from snapshots import step_dir

OLD = """
import hashlib
from vegcrew.data import season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
plan = make_plan(season_from_dict(scenario("medium")))
trims = sorted((t.cid, t.crew, t.start) for t in plan.trims.values())
print(plan.status, plan.risk_carried, hashlib.sha256(repr(trims).encode()).hexdigest()[:12])
"""


def run(step: int, args: list[str]) -> str:
    done = subprocess.run([sys.executable, *args], cwd=step_dir(step), capture_output=True, text=True, check=True)
    return done.stdout


old = [run(6, ["-c", OLD]).split() for _ in range(3)]
print("steps/06, medium season, 3 runs:")
for status, risk, plan in old:
    print(f"  {status:<8} risk carried ${int(risk):,}k  plan {plan}")
print(f"same plan every run: {'yes' if len({p for _, _, p in old}) == 1 else 'no'}")

new = [run(7, ["-m", "vegcrew", "medium", "--record"]) for _ in range(2)]
record = json.loads(new[0])
print("steps/07, medium season, 2 runs:")
for text in new:
    r = json.loads(text)
    print(f"  {r['status']:<8} risk carried ${r['risk_carried']:,}k  record sha256 "
          f"{hashlib.sha256(text.encode()).hexdigest()[:12]}")
print(f"  records identical byte for byte: {'yes' if new[0] == new[1] else 'no'}")
