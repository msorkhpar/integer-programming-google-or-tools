"""Three GridCap small projects that need the same Coast substation outage, ordered two ways."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from outage_model import build

small = generate("small")
jobs = ("P011", "P016", "P021")
durations = {pid: small.project(pid).crew_months for pid in jobs}   # months of one crew's work
horizon = 12
print("months of work:", durations, " horizon", horizon)

for form in ("big_m", "hull"):
    lp = build(durations, horizon, form, integer=False)
    relaxed = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    milp = build(durations, horizon, form)
    best = mathopt.solve(milp.model, mathopt.SolverType.HIGHS)
    starts = {j: round(best.variable_values(v), 1) + 0.0 for j, v in milp.start.items()}
    print(f"{form:6} variables {milp.model.get_num_variables():2}  rows {milp.model.get_num_linear_constraints():2}"
          f"  LP bound {relaxed.objective_value():5.2f}  MILP {best.objective_value():5.1f}  starts {starts}")
    print(f"       LP: starts {[round(relaxed.variable_values(v), 2) for v in lp.start.values()]}"
          f"  first {[round(relaxed.variable_values(v), 2) for v in lp.first.values()]}")
