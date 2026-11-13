"""One lexicographic question, three implementations, on GridCap small: do they agree?"""

from ortools.math_opt.python import mathopt
from gurobipy import GRB

from gridcap import generate
from gurobi_model import build as build_grb, chosen, quiet_env
from in_order import add_auxiliary, solve_in_order
from lex_model import build, score
from lexicographic import Level, solve_levels

small = generate("small")
env = quiet_env()


def mathopt_in_order(npv_rel: float, npv_abs: float) -> dict[str, int]:
    sm = build(small)
    sm.model.maximize(sm.objective("npv"))
    add_auxiliary(sm.model, sm.objective("risk"), priority=1, is_maximize=True, name="risk")
    params = mathopt.ModelSolveParameters(objective_parameters={sm.model.objective: mathopt.ObjectiveParameters(
        objective_degradation_relative_tolerance=npv_rel, objective_degradation_absolute_tolerance=npv_abs)})
    _, values = solve_in_order(sm.model, params)
    return {pid: t for (pid, t), v in sm.x.items() if values[v.name] > 0.5}


def gurobi_native(npv_rel: float, npv_abs: float) -> dict[str, int]:
    gm = build_grb(env, small)
    gm.model.ModelSense = GRB.MAXIMIZE
    gm.model.setObjectiveN(gm.objective["npv"], index=0, priority=2, reltol=npv_rel, abstol=npv_abs, name="npv")
    gm.model.setObjectiveN(gm.objective["risk"], index=1, priority=1, name="risk")
    gm.model.Params.MIPGap = 0.0
    gm.model.optimize()
    return chosen(gm)


def manual(npv_rel: float, npv_abs: float) -> dict[str, int]:
    sm = build(small)
    return solve_levels(sm, [Level("npv", rel_tol=npv_rel, abs_tol=npv_abs), Level("risk")]).plan


sm = build(small)
print("question            implementation        NPV      risk  same plan")
for question, tol in (("NPV exact, risk", (0.0, 0.0)), ("NPV 1%, risk", (0.01, 0.0)),
                      ("NPV $100k, risk", (0.0, 100.0)), ("NPV 5%, risk", (0.05, 0.0))):
    plans = {"MathOpt in order": mathopt_in_order(*tol), "gurobipy setObjectiveN": gurobi_native(*tol),
             "manual two-pass": manual(*tol)}
    reference = plans["gurobipy setObjectiveN"]
    for name, plan in plans.items():
        print(f"{question:19} {name:22} {score(sm, plan, 'npv'):6,.0f} {score(sm, plan, 'risk'):9,.1f}  "
              f"{'yes' if plan == reference else 'no'}")
