"""NPV within 1%, then risk removed, then the least spend, stored as MathOpt prioritized objectives."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from in_order import add_auxiliary, solve_in_order
from lex_model import build, plan_of, quiet, score

small = generate("small")
sm = build(small)
model = sm.model
model.maximize(sm.objective("npv"))                                    # primary objective, priority 0
risk = add_auxiliary(model, sm.objective("risk"), priority=1, is_maximize=True, name="risk")
spend = add_auxiliary(model, sm.objective("spend"), priority=2, is_maximize=False, name="spend")
params = mathopt.ModelSolveParameters(objective_parameters={
    model.objective: mathopt.ObjectiveParameters(objective_degradation_relative_tolerance=0.01)})

for obj in (model.objective, risk, spend):
    sense = "max" if obj.is_maximize else "min"
    print(f"{obj.name or 'primary':8} priority {obj.priority}  {sense}  terms {len(list(obj.linear_terms()))}")

try:
    with quiet():
        mathopt.solve(model, mathopt.SolverType.HIGHS, model_params=params)
except Exception as error:                     # OR-Tools 9.15 hides the solver's reason on __context__
    print(f"HiGHS refuses: {error.__context__ or error}")

reached, values = solve_in_order(model, params)
print("in order:", {name: round(value, 1) for name, value in reached.items()})
plan = {pid: t for (pid, t), v in sm.x.items() if values[v.name] > 0.5}
print(f"plan: NPV ${score(sm, plan, 'npv'):,.0f}k  risk removed ${score(sm, plan, 'risk'):,.1f}k  "
      f"spend ${score(sm, plan, 'spend'):,.0f}k  projects {len(plan)}")
