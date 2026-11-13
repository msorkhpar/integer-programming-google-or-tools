"""Work fronts on GridCap small, written aggregated and disaggregated: same plans, different LP bounds."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from strong_model import EXACT, build, fronts_of, gap_closed, lp_bound, size, solve_highs

small = generate("small")
results = {}
for form in ("aggregated", "disaggregated"):
    lp_model = build(small, integer=False, fronts=form)
    lp = lp_bound(lp_model.model)
    milp_model = build(small, fronts=form)
    milp = solve_highs(milp_model.model, EXACT)
    variables, rows = size(milp_model.model)
    results[form] = (lp.objective_value(), milp.objective_value())
    mobilized = sorted(f"{r} {g}" for (r, g), y in milp_model.front.items() if milp.variable_values(y) > 0.5)
    print(f"{form:13} variables {variables}  rows {rows}  LP bound {lp.objective_value():,.2f}  "
          f"MILP {milp.objective_value():,.0f}")
    print(f"{'':13} LP fronts: " + ", ".join(f"{r[:5]} {g[:5]} {abs(lp.variable_values(y)):.2f}"
                                             for (r, g), y in sorted(lp_model.front.items())))
    members = fronts_of(small)["Ridge", "transmission"]
    starts = {i: sum(lp.variable_values(lp_model.x[i, t]) for t in small.project(i).starts()) for i in members}
    print(f"{'':13} Ridge transmission: front {lp.variable_values(lp_model.front['Ridge', 'transmission']):.2f}, "
          + ", ".join(f"{i} started {v:.2f}" for i, v in starts.items()))
print(f"fronts mobilized in the best plan: {len(mobilized)} of {len(milp_model.front)}")
weak, strong = results["aggregated"][0], results["disaggregated"][0]
print(f"gap closed by the disaggregated form: {gap_closed(weak, strong, results['disaggregated'][1]):.1%}")
