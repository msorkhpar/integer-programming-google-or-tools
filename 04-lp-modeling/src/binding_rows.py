"""Loosen a row that has room and nothing moves; loosen a row with no room and the answer does."""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import build, small

YEAR = 2027
crews = {k: small.crews[k, YEAR] for k in PROGRAMS}


def npv(split) -> str:
    result = mathopt.solve(split.model, mathopt.SolverType.GLOP)
    amounts = {k: round(result.variable_values(v), 1) for k, v in split.s.items()}
    return f"NPV {result.objective_value():8,.1f}  {amounts}"


if __name__ == "__main__":
    print(f"{'as built':34}", npv(build(YEAR)))
    print(f"{'budget +200 (room 230.3)':34}", npv(build(YEAR, budget=small.budget[YEAR] + 200)))
    print(f"{'no vegetation floor (room 12.0)':34}", npv(build(YEAR, floor={})))
    print(f"{'distribution crews +1 (room 0)':34}", npv(build(YEAR, crews={**crews, "distribution": 10})))
    print(f"{'vegetation crews +1 (room 0)':34}", npv(build(YEAR, crews={**crews, "vegetation": 3})))
