"""The crew rule as a MathOpt indicator constraint: HiGHS refuses it, SCIP solves it."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_model import build, hired, m_by_solving, quiet_solve

small = generate("small")
exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)

cm = build(small, None, form="indicator")
print("indicator constraints in the model:", cm.model.get_num_indicator_constraints())
try:
    quiet_solve(cm.model, mathopt.SolverType.HIGHS, params=exact)
except Exception as error:                      # 9.15 raises AttributeError; the reason is in __context__
    print("HiGHS:", type(error).__name__, "| reason:", error.__context__)

runs = {"SCIP, indicator": (cm, mathopt.SolverType.GSCIP),
        "SCIP, tight big-M": (build(small, m_by_solving(small, integer=True)), mathopt.SolverType.GSCIP),
        "HiGHS, tight big-M": (build(small, m_by_solving(small, integer=True)), mathopt.SolverType.HIGHS)}
for name, (model, solver) in runs.items():
    result = quiet_solve(model.model, solver, params=exact)
    print(f"{name:19} {result.termination.reason.name}  objective {result.objective_value():,.1f}"
          f"  hired {hired(model, result)}")

relaxed = build(small, None, integer=False, form="indicator")     # every variable continuous in [0, 1]
try:
    quiet_solve(relaxed.model, mathopt.SolverType.GLOP)
except Exception as error:
    print("GLOP, relaxed indicator model:", error.__context__)
