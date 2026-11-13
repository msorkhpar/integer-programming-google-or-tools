"""Gurobi's four knobs (Presolve, Cuts, Heuristics, MIPFocus) against its defaults on every regional plan."""

from dataclasses import replace

from grb_runs import gurobi, quiet_env
from settings_bench import report, run_all

SETTINGS = {
    "default": {},
    "Presolve=0 (off)": {"Presolve": 0},
    "Presolve=2 (aggr.)": {"Presolve": 2},
    "Cuts=0 (off)": {"Cuts": 0},
    "Cuts=2 (aggr.)": {"Cuts": 2},
    "Heuristics=0": {"Heuristics": 0.0},
    "Heuristics=0.5": {"Heuristics": 0.5},
    "MIPFocus=1 (plans)": {"MIPFocus": 1},
    "MIPFocus=2 (proof)": {"MIPFocus": 2},
    "MIPFocus=3 (bound)": {"MIPFocus": 3},
}

env = quiet_env()
runs = run_all(lambda pf, seed, s: gurobi(env, pf, seed, **s), SETTINGS, seeds=(1, 2, 3))
milli = {k: replace(r, work=r.work * 1000, events=tuple((w * 1000, o) for w, o in r.events)) for k, r in runs.items()}
print("Gurobi, one thread")
report(milli, shift=10, unit="thousandths of a work unit")
