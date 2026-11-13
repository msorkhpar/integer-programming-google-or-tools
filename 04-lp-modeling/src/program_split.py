"""The program-split LP: how much of a year's budget each GridCap program gets (fictional data).

Every number comes from GridCap's small portfolio, which is invented for this course. A program's
rates are averages over its projects: NPV per $k spent, and crew-months per $1,000k of work.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS, generate

small = generate("small")
FLOOR = {"vegetation": 300}     # $k a fictional regulator requires on tree trimming each year
SHARE = 0.5                     # no program gets more than half of what the year spends


def program_rates(portfolio) -> tuple[dict[str, float], dict[str, float]]:
    """(value per $k, crew-months per $1,000k) for each program, averaged over its projects."""
    value, crew = {}, {}
    for k in PROGRAMS:
        projects = [p for p in portfolio.projects if p.program == k]
        capex = sum(p.capex for p in projects)
        value[k] = round(sum(p.value for p in projects) / capex, 3)
        crew[k] = round(1000 * sum(p.crew_months for p in projects) / capex, 2)
    return value, crew


VALUE, CREW = program_rates(small)


@dataclass
class Split:
    model: mathopt.Model
    s: dict[str, mathopt.Variable]                  # s[k]: $k spent on program k this year
    rows: dict[str, mathopt.LinearConstraint]


def build(year: int, crews: dict[str, int] | None = None, budget: int | None = None,
          share: float | None = SHARE, floor: dict[str, int] | None = None) -> Split:
    """The one-year split. Arguments left as None take GridCap's numbers for `year`."""
    crews = crews or {k: small.crews[k, year] for k in PROGRAMS}
    budget = small.budget[year] if budget is None else budget
    floor = FLOOR if floor is None else floor
    model = mathopt.Model(name=f"program split {year}")
    s = {k: model.add_variable(lb=0, name=f"s_{k}") for k in PROGRAMS}
    rows = {"budget": model.add_linear_constraint(sum(s.values()) <= budget, name="budget")}
    for k in PROGRAMS:
        rows[f"crew_{k}"] = model.add_linear_constraint(CREW[k] / 1000 * s[k] <= crews[k], name=f"crew_{k}")
    for k, amount in floor.items():
        rows[f"floor_{k}"] = model.add_linear_constraint(s[k] >= amount, name=f"floor_{k}")
    if share is not None:
        total = sum(s.values())
        for k in PROGRAMS:
            rows[f"share_{k}"] = model.add_linear_constraint(s[k] <= share * total, name=f"share_{k}")
    model.maximize(sum(VALUE[k] * s[k] for k in PROGRAMS))
    return Split(model, s, rows)


def activity(row: mathopt.LinearConstraint, result: mathopt.SolveResult) -> float:
    """The row's left-hand side, a . x, at the solution."""
    values = result.variable_values()
    return sum(term.coefficient * values[term.variable] for term in row.terms())
