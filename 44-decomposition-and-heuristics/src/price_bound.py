"""Any nonnegative budget prices give an upper bound: L(lam) at a few prices, by enumeration and by MathOpt."""

from ortools.math_opt.python import mathopt

from gridcap import generate

from capital import EXACT, build, solve_highs
from lagrange import components, lagrangian

small = generate("small")
optimum = solve_highs(build(small).model, EXACT).objective_value()
groups = components(small)
print(f"{len(small.projects)} projects fall into {len(groups)} independent groups once the budget rows go;"
      f" the largest has {max(len(g) for g in groups)} projects")
medium_groups = components(generate("medium"))
print(f"medium: 400 projects, {len(medium_groups)} groups, the largest {max(len(g) for g in medium_groups)} projects")


def relaxed_by_solver(lam: dict[int, float]) -> float:
    """The same L(lam) from MathOpt: the model without budget rows, the priced spend in the objective."""
    cap = build(small, budget_rows=False)
    priced = sum(lam[y] * (small.budget[y] - cap.spend[y]) for y in small.years)
    cap.model.maximize(cap.model.objective.as_linear_expression() + priced)
    return solve_highs(cap.model, EXACT).objective_value()


for name, lam in (("0 everywhere", {y: 0.0 for y in small.years}),
                  ("0.3 everywhere", {y: 0.3 for y in small.years}),
                  ("0.6 everywhere", {y: 0.6 for y in small.years}),
                  ("1.0 everywhere", {y: 1.0 for y in small.years}),
                  ("0.6, 0.6, 0.5, 0.5, 0.3", dict(zip(small.years, (0.6, 0.6, 0.5, 0.5, 0.3))))):
    bound, plan = lagrangian(small, lam)
    print(f"lam {name:24}  L(lam) {bound:9,.1f}  solver {relaxed_by_solver(lam):9,.1f}"
          f"  projects started {len(plan):2}  above the optimum by {bound - optimum:7,.1f}")
print(f"MILP optimum {optimum:,.1f}")
