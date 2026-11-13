"""The first Benders iteration by hand: each year's LP for the first master plan, its prices, its cut."""

from ortools.math_opt.python import mathopt

from gridcap import generate

from capital import EXACT, build, schedule, solve_highs
from crew_costs import OVERTIME_SHARE, POOL, PROGRAMS, need_of, year_lp

small = generate("small")
master = build(small)                                  # iteration 1: no cuts yet
plan = schedule(master, solve_highs(master.model, EXACT))
need = need_of(small, plan)


def clean(v: float) -> float:
    return 0.0 if abs(v) < 1e-9 else v


for y in small.years:
    crews = {g: small.crews[g, y] for g in PROGRAMS}
    print(f"{y}  need " + "  ".join(f"{g[:5]} {need[g, y]:2}/{crews[g]:2}" for g in PROGRAMS))
    m, rows = year_lp(small, y, {g: need[g, y] for g in PROGRAMS}, phase_one=True)
    short = mathopt.solve(m, mathopt.SolverType.GLOP)
    infeasible = short.objective_value() > 1e-6
    if not infeasible:
        m, rows = year_lp(small, y, {g: need[g, y] for g in PROGRAMS})
    result = mathopt.solve(m, mathopt.SolverType.GLOP)
    duals = {name: clean(result.dual_values(row)) for name, row in rows.items()}
    bounds = {**{f"cover_{g}": need[g, y] for g in PROGRAMS}, **{f"own_{g}": crews[g] for g in PROGRAMS},
              **{f"over_{g}": OVERTIME_SHARE * crews[g] for g in PROGRAMS}, "pool": POOL}
    certificate = sum(duals[r] * bounds[r] for r in rows)
    kind = "shortfall" if infeasible else "crew cost"
    print(f"      {kind} {result.objective_value():6.2f}   sum of dual x bound {certificate:6.2f}")
    print("      nonzero duals: " + (", ".join(f"{r} {d:g}" for r, d in duals.items() if d) or "none"))
    if infeasible:
        terms = " + ".join(f"{duals[f'cover_{g}']:g} need_{g[:5]}(x)" for g in PROGRAMS if duals[f"cover_{g}"])
        rest = certificate - sum(duals[f"cover_{g}"] * need[g, y] for g in PROGRAMS)
        print(f"      feasibility cut: {terms} {rest:+g} <= 0")
    elif result.objective_value() > 1e-6:
        terms = " + ".join(f"{duals[f'cover_{g}']:g} need_{g[:5]}(x)" for g in PROGRAMS if duals[f"cover_{g}"])
        rest = certificate - sum(duals[f"cover_{g}"] * need[g, y] for g in PROGRAMS)
        print(f"      optimality cut: theta_{y} >= {terms} {rest:+g}")
