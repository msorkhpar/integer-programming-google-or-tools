"""GridCap small's selection model as an LP relaxation (GLOP) and as a MILP (HiGHS)."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import best_plan, build

small = generate("small")


def fractional(result: mathopt.SolveResult, x: dict) -> dict[str, float]:
    """The variables the LP left strictly between 0 and 1."""
    return {pid: round(result.variable_values(v), 3) for pid, v in x.items()
            if 1e-6 < result.variable_values(v) < 1 - 1e-6}


if __name__ == "__main__":
    lp = build(small, integer=False)
    result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    whole = [pid for pid, v in lp.x.items() if result.variable_values(v) > 1 - 1e-6]
    print(f"LP relaxation: {result.termination.reason.name}, value {result.objective_value():,.2f}")
    print(f"  {len(whole)} projects at 1, fractional: {fractional(result, lp.x)}")
    p = small.project("P022")
    print(f"  P022: {p.name}, capex {p.capex:,}, NPV {p.value:,}")
    value, plan = best_plan(small)
    print(f"MILP: OPTIMAL, value {value:,.2f}, {len(plan)} projects funded")
