"""HiGHS's own options for presolve, heuristics and restarts against its defaults on every regional plan."""

from runs import highs
from settings_bench import report, run_all

SETTINGS = {
    "default": {},
    "presolve=off": {"presolve": "off"},
    "heuristic effort 0.3": {"mip_heuristic_effort": 0.3},
    "no restarts": {"mip_allow_restart": False},
}

runs = run_all(lambda pf, seed, options: highs(pf, seed, options=options), SETTINGS, seeds=(1, 2, 3))
print("HiGHS, one thread")
report(runs, shift=100, unit="LP iterations")
