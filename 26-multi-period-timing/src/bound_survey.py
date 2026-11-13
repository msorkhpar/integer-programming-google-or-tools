"""Compare the two precedence forms' LP bounds on many GridCap small scenarios."""

from dataclasses import replace

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build


def lp_bound(portfolio, form: str) -> float | None:
    result = mathopt.solve(build(portfolio, integer=False, precedence=form).model, mathopt.SolverType.GLOP)
    return result.objective_value() if result.termination.reason == mathopt.TerminationReason.OPTIMAL else None


def scenarios():
    for seed in range(1, 41):
        base = generate("small", seed)
        for cut in (1.0, 0.5, 0.0):                 # share of the first two years' budgets kept
            yield replace(base, budget={y: int(v * cut) if y in base.years[:2] else v for y, v in base.budget.items()})


if __name__ == "__main__":
    solved = tighter = looser = 0
    for pf in scenarios():
        agg, cum = lp_bound(pf, "aggregated"), lp_bound(pf, "cumulative")
        if agg is None or cum is None:
            continue
        solved += 1
        tighter += cum < agg - 1e-6
        looser += cum > agg + 1e-6
    print(f"{solved} feasible scenarios: cumulative tighter in {tighter}, looser in {looser}")
