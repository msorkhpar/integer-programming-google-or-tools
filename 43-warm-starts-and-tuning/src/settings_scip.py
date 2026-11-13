"""SCIP's presolve, cuts and heuristics switched off, one at a time, against its defaults on every regional plan."""

from ortools.math_opt.solvers.gscip import gscip_pb2

from runs import scip
from settings_bench import report, run_all

G = gscip_pb2.GScipParameters
SETTINGS = {
    "default": None,
    "presolve OFF": G(presolve=G.OFF),
    "separating (cuts) OFF": G(separating=G.OFF),
    "heuristics OFF": G(heuristics=G.OFF),
}

runs = run_all(lambda pf, seed, g: scip(pf, seed, gscip=g), SETTINGS, seeds=(1, 2, 3))
print("SCIP, one thread")
report(runs, shift=100, unit="LP iterations")
