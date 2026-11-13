"""Solve each variant four ways. A sound model gives one answer; a badly scaled one may not."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from loan_model import EXACT, HUGE_M, MIXED, NO_PRESOLVE, TIGHT, build, solve

small = generate("small")
WAYS = (("HiGHS", mathopt.SolverType.HIGHS, EXACT), ("HiGHS no presolve", mathopt.SolverType.HIGHS, NO_PRESOLVE),
        ("SCIP", mathopt.SolverType.GSCIP, EXACT), ("SCIP no presolve", mathopt.SolverType.GSCIP, NO_PRESOLVE))

print(f"{'objective in $k':38}" + "".join(f"{name:>19}" for name, _, _ in WAYS))
for units in (TIGHT, HUGE_M, MIXED):
    answers = []
    for _, solver, params in WAYS:
        lm = build(small, units)
        result, _ = solve(lm.model, solver, params)
        answers.append(lm.in_k(result.objective_value()))
    flag = "agree" if max(answers) - min(answers) < 0.01 else "DISAGREE"
    print(f"{units.name:38}" + "".join(f"{a:>19,.1f}" for a in answers) + f"  {flag}")
