"""A gap left in pass 1 becomes a tolerance nobody asked for: HiGHS by hand, and Gurobi."""

from gurobipy import GRB

from gridcap import generate
from gurobi_model import build as build_grb, quiet_env
from lex_model import build, plan_of, score, solve

small = generate("small")
sm = build(small)
npv, risk = sm.objective("npv"), sm.objective("risk")

print("manual two-pass, HiGHS, no tolerance on NPV")
for gap in (0.0, 0.05):
    sm.model.set_linear_objective(npv, is_maximize=True)
    first = solve(sm.model, gap)                                   # pass 1 stops within `gap`
    best, bound = first.objective_value(), first.termination.objective_bounds.dual_bound
    keep = sm.model.add_linear_constraint(npv >= best, name="keep_npv")
    sm.model.set_linear_objective(risk, is_maximize=True)
    plan = plan_of(sm, solve(sm.model))                            # pass 2 to a zero gap
    sm.model.delete_linear_constraint(keep)
    print(f"  pass-1 gap {gap:4.0%}: kept NPV >= {best:,.0f} (bound {bound:,.0f}) -> "
          f"NPV {score(sm, plan, 'npv'):,.0f}  risk removed {score(sm, plan, 'risk'):,.1f}")

print("gurobipy setObjectiveN, no tolerance on NPV (reltol 0)")
env = quiet_env()
default = build_grb(env, small).model
print(f"  (Gurobi's default MIPGap: {default.Params.MIPGap:g})")
for mip_gap in (0.0, 1e-4, 0.01, 0.02):
    gm = build_grb(env, small)
    gm.model.ModelSense = GRB.MAXIMIZE
    gm.model.setObjectiveN(gm.objective["npv"], index=0, priority=2, name="npv")
    gm.model.setObjectiveN(gm.objective["risk"], index=1, priority=1, name="risk")
    gm.model.Params.MIPGap = mip_gap
    gm.model.optimize()
    values = []
    for k in range(2):
        gm.model.Params.ObjNumber = k
        values.append(gm.model.ObjNVal)
    print(f"  MIPGap {mip_gap:<6g}: NPV {values[0]:,.0f}  risk removed {values[1]:,.1f}")
