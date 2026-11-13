"""Change one number, re-solve, and see which rows hold the answer in place."""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import activity, build, small

YEAR = 2027


def full_rows(split, result, tol: float = 1e-6) -> list[str]:
    """Rows whose left-hand side sits on their bound: the rules the answer is pressed against."""
    names = []
    for name, row in split.rows.items():
        a = activity(row, result)
        if abs(a - row.upper_bound) <= tol or abs(a - row.lower_bound) <= tol:
            names.append(name)
    return names


def solve(crews: dict[str, int]) -> None:
    split = build(YEAR, crews=crews)
    result = mathopt.solve(split.model, mathopt.SolverType.GLOP)
    amounts = {k: round(result.variable_values(v), 1) for k, v in split.s.items()}
    print(f"distribution crews {crews['distribution']:2}: NPV {result.objective_value():,.1f}  {amounts}")
    print("   full rows:", ", ".join(full_rows(split, result)))


if __name__ == "__main__":
    crews = {k: small.crews[k, YEAR] for k in PROGRAMS}
    solve(crews)
    solve({**crews, "distribution": 12})
