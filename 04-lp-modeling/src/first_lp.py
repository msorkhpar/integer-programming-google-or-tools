"""Your first LP: split GridCap's 2027 budget across its three programs, solved with GLOP."""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import CREW, FLOOR, SHARE, VALUE, activity, build, small

YEAR = 2027


def show_data() -> None:
    print(f"{'program':13} {'value/$':>8} {'crew-mo per $1M':>16} {'crews':>6} {'crews allow $k':>15}")
    for k in PROGRAMS:
        crews = small.crews[k, YEAR]
        print(f"{k:13} {VALUE[k]:8.3f} {CREW[k]:16.2f} {crews:6} {crews * 1000 / CREW[k]:15,.1f}")
    print(f"budget {small.budget[YEAR]:,}  vegetation floor {FLOOR['vegetation']}  share cap {SHARE:.0%}")


def report(split, result) -> None:
    print("status", result.termination.reason.name)
    for k, var in split.s.items():
        print(f"  s_{k:13} = {result.variable_values(var):9,.1f}")
    print(f"  NPV  {result.objective_value():,.1f}")
    for name, row in split.rows.items():
        lo, hi = row.lower_bound, row.upper_bound
        bound = f"<= {hi:,.1f}" if hi < float("inf") else f">= {lo:,.1f}"
        print(f"  {name:22} {activity(row, result):10,.1f}  {bound}")


if __name__ == "__main__":
    show_data()
    split = build(YEAR)
    result = mathopt.solve(split.model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise SystemExit(result.termination.reason.name)
    report(split, result)
