"""Last month's plan as a solution hint: how to pass it, and how each solver's log says it used it."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, solve

small = generate("small")

# Last month: the plan as it was approved.
pm = build(small)
last = solve(pm.model, mathopt.SolverType.HIGHS)
approved = {v: round(last.variable_values(v)) for v in pm.x.values()}
print(f"last month    NPV {last.objective_value():,.0f}, {sum(approved.values())} projects started")

# This month: 2031 gets $200k more. Last month's plan still fits, so it is a good place to start.
pm.budget[2031].upper_bound += 200

complete = mathopt.SolutionHint(variable_values=approved)                         # every x, 0 or 1
partial = mathopt.SolutionHint(variable_values={v: 1.0 for v, a in approved.items() if a == 1})
wrong = mathopt.SolutionHint(variable_values={v: 1.0 for v in pm.x.values()})      # every start at once
print(f"hint sizes: complete {len(complete.variable_values)}, partial {len(partial.variable_values)},"
      f" wrong {len(wrong.variable_values)} of {pm.model.get_num_variables()} variables")

WORDS = {mathopt.SolverType.HIGHS: ("MIP start", "User-supplied", "user-supplied"),
         mathopt.SolverType.GSCIP: ("solution candidate storage",),
         mathopt.SolverType.CP_SAT: ("The solution hint",)}

for solver, words in WORDS.items():
    for name, hint in (("complete", complete), ("partial", partial), ("wrong", wrong)):
        log: list[str] = []
        result = solve(pm.model, solver, model_params=mathopt.ModelSolveParameters(solution_hints=[hint]),
                       msg_cb=mathopt.list_message_callback(log))
        said = sorted({line.strip() for line in log if any(w in line for w in words)})
        print(f"{solver.name:6} {name:8} NPV {result.objective_value():,.0f}  log: {said or 'nothing about it'}")
