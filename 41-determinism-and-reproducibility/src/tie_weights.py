"""Lesson 10.2.3: tie-break weights from hash(), from sha256, and from the sorted rank.

Objective: count + eps * sum(w[i, t] * x[i, t]), eps = 1 / (sum of w + 1), so the weights can never
outweigh a project. Each run is a fresh process with its own hash seed and the projects in a set's
order. GridCap is a fictional utility's portfolio.
"""

import hashlib
import json
import subprocess
import sys

from ortools.math_opt.python import mathopt

from gridcap import generate
from repeat import child_env
from plan_model import build, digest, schedule, solve_highs


def weights(keys: list[tuple[str, int]], kind: str) -> dict:
    n = len(keys)
    if kind == "hash()":                      # salted per process: a different weight every run
        return {k: hash(f"{k[0]}:{k[1]}") % n + 1 for k in keys}
    if kind == "sha256":                      # the same bytes give the same digest in every process
        return {k: int(hashlib.sha256(f"{k[0]}:{k[1]}".encode()).hexdigest(), 16) % n + 1 for k in keys}
    return {k: r + 1 for r, k in enumerate(sorted(keys))}      # "rank": 1, 2, ..., n


def run(kind: str) -> dict:
    small = generate("small")
    plan = build(small, order=list(set(small.project_ids)), objective="count")
    w = weights(list(plan.x), kind)
    eps = 1 / (sum(w.values()) + 1)
    plan.model.maximize(sum(plan.x.values()) + eps * sum(w[k] * v for k, v in plan.x.items()))
    result = solve_highs(plan.model, mathopt.SolveParameters(relative_gap_tolerance=0.0))
    starts = schedule(plan, result)
    return {"projects": len(starts), "weight": sum(w[k] for k in starts.items()), "plan": digest(starts)}


if __name__ == "__main__" and len(sys.argv) > 1:          # one run, in a fresh process
    print(json.dumps(run(sys.argv[1])))
elif __name__ == "__main__":
    for kind in ["hash()", "sha256", "rank"]:
        runs = []
        for seed in ["1", "2", "3", "4"]:
            env = child_env(seed)
            runs.append(json.loads(subprocess.run([sys.executable, __file__, kind], env=env, capture_output=True,
                                                  text=True, check=True).stdout))
        print(f"{kind:<7} plans {[r['plan'] for r in runs]}")
        print(f"{'':<7} projects {sorted({r['projects'] for r in runs})}, "
              f"tie-break weight of the plan {[r['weight'] for r in runs]}")
