"""Two ways to write the parent rule: the same 0/1 plans, different LP bounds."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs


def bound_and_optimum(portfolio, form: str) -> tuple[float, float, dict[str, float]]:
    lp = build(portfolio, integer=False, parent_form=form)
    relaxed = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    shares = {pid: round(relaxed.variable_values(v), 3) for pid, v in lp.x.items()
              if 1e-6 < relaxed.variable_values(v) < 1 - 1e-6}
    optimum = solve_highs(build(portfolio, parent_form=form).model).objective_value()
    return relaxed.objective_value(), optimum, shares


if __name__ == "__main__":
    for size in ("tiny", "medium"):
        portfolio = generate(size)
        for form in ("tight", "loose"):
            bound, optimum, shares = bound_and_optimum(portfolio, form)
            print(f"{size:<6} {form:<5}  LP bound {bound:>11,.2f}  optimum {optimum:>9,.0f}  "
                  f"gap {(bound - optimum) / optimum:.3%}  fractional {shares}")
