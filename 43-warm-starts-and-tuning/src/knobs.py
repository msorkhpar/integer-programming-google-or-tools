"""Which of MathOpt's common knobs does each solver take, and does a knob it takes change anything?"""

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from plan_model import build, instance_set
from quiet import muted
from runs import highs

plains = instance_set()[3]
pm = build(plains)
SOLVERS = {"HiGHS": mathopt.SolverType.HIGHS, "SCIP": mathopt.SolverType.GSCIP, "CP-SAT": mathopt.SolverType.CP_SAT}

print(f"{'':<8} {'presolve':<10} {'cuts':<10} {'heuristics':<10}   (each tried at OFF and HIGH)")
reasons = {}
for label, kind in SOLVERS.items():
    cells = []
    for knob in ("presolve", "cuts", "heuristics"):
        refused = None
        for level in (mathopt.Emphasis.OFF, mathopt.Emphasis.HIGH):
            try:
                # One HiGHS thread in every HiGHS solve: the first solve fixes the count (lesson 4.2.4).
                one = {"highs": highs_pb2.HighsOptionsProto(int_options={"threads": 1})} if label == "HiGHS" else {}
                with muted():
                    mathopt.solve(pm.model, kind, params=mathopt.SolveParameters(
                        **{knob: level}, **one, relative_gap_tolerance=0.01))
            except Exception as error:                      # OR-Tools 9.15: the reason is on __context__
                refused = str(error.__context__ or error).split(" [")[0]
        cells.append("refused" if refused else "taken")
        if refused:
            reasons[f"{label} {knob}"] = refused
    print(f"{label:<8} " + " ".join(f"{c:<10}" for c in cells))
for where, why in reasons.items():
    print(f"  {where}: {why[:90]}")

valley = instance_set()[1]
print("\nHiGHS on the Valley plan, seed 1: LP iterations to prove optimality")
for label, kwargs in (("default", {}),
                      ("common heuristics=OFF", {"heuristics": mathopt.Emphasis.OFF}),
                      ("common heuristics=VERY_HIGH", {"heuristics": mathopt.Emphasis.VERY_HIGH}),
                      ("mip_heuristic_effort=0.3", {"options": {"mip_heuristic_effort": 0.3}}),
                      ("mip_heuristic_effort=0.8", {"options": {"mip_heuristic_effort": 0.8}})):
    r = highs(valley, 1, **kwargs)
    print(f"  {label:<28} {r.work:>8,.0f}")
