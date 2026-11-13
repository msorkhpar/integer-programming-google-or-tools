"""SCIP's emphasis settings, its "focus": find plans fast, or prove optimality fast, on every regional plan."""

from ortools.math_opt.solvers.gscip import gscip_pb2

from runs import scip
from settings_bench import report, run_all

G = gscip_pb2.GScipParameters
SETTINGS = {
    "default": None,
    "emphasis FEASIBILITY": G(emphasis=G.FEASIBILITY),
    "emphasis OPTIMALITY": G(emphasis=G.OPTIMALITY),
}

runs = run_all(lambda pf, seed, g: scip(pf, seed, gscip=g), SETTINGS, seeds=(1, 2, 3))
print("SCIP, one thread")
report(runs, shift=100, unit="LP iterations")
