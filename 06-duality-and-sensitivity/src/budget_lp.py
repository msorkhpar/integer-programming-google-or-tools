"""The module's running model: GridCap's yearly budget split across its three programs, as an LP.

GridCap is a fictional utility. The vegetation floor below is this module's own assumption (a
rate-case commitment invented for the lessons); it is not part of the GridCap data.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS, Portfolio

VEG_FLOOR = 900       # $k of vegetation work the plan must fund over its years (this module's assumption)


def value_per_k(portfolio: Portfolio) -> dict[str, float]:
    """NPV per $k a program returns in the plan's first year: its projects' NPV over their capex."""
    out = {}
    for g in PROGRAMS:
        projects = [p for p in portfolio.projects if p.program == g]
        out[g] = round(sum(p.value for p in projects) / sum(p.capex for p in projects), 2)
    return out


def work_per_crew_month(portfolio: Portfolio) -> dict[str, int]:
    """$k of work one crew-month delivers in a program: its projects' capex over their crew-months."""
    out = {}
    for g in PROGRAMS:
        projects = [p for p in portfolio.projects if p.program == g]
        out[g] = int(round(sum(p.capex for p in projects) / sum(p.crew_months for p in projects), -1))
    return out


def discount(portfolio: Portfolio, year: int) -> float:
    """What $1k of NPV earned in `year` is worth in the plan's first year."""
    return 1 / (1 + portfolio.discount_rate) ** (year - portfolio.years[0])


@dataclass
class BudgetLP:
    model: mathopt.Model
    spend: dict          # (program, year) -> variable, $k
    carry: dict          # year -> variable, $k carried out of that year (none for the last year)
    cash: dict           # year -> constraint
    crew: dict           # (program, year) -> constraint
    floor: mathopt.LinearConstraint | None


def build(portfolio: Portfolio, budget: dict[int, int] | None = None, floor: int | None = VEG_FLOOR) -> BudgetLP:
    budget = dict(portfolio.budget) if budget is None else budget
    years = portfolio.years
    v, k = value_per_k(portfolio), work_per_crew_month(portfolio)
    model = mathopt.Model(name="budget-lp")
    spend = {(g, y): model.add_variable(lb=0, name=f"spend_{g}_{y}") for g in PROGRAMS for y in years}
    carry = {y: model.add_variable(lb=0, name=f"carry_{y}") for y in years[:-1]}
    cash, crew = {}, {}
    for i, y in enumerate(years):
        carried_in = carry[years[i - 1]] if i else 0
        carried_out = carry.get(y, 0)
        cash[y] = model.add_linear_constraint(
            sum(spend[g, y] for g in PROGRAMS) + carried_out - carried_in <= budget[y], name=f"cash_{y}")
        for g in PROGRAMS:
            crew[g, y] = model.add_linear_constraint(spend[g, y] <= k[g] * portfolio.crews[g, y],
                                                     name=f"crew_{g}_{y}")
    veg_floor = None
    if floor is not None:
        veg_floor = model.add_linear_constraint(sum(spend["vegetation", y] for y in years) >= floor,
                                                name="veg_floor")
    model.maximize(sum(v[g] * discount(portfolio, y) * spend[g, y] for g in PROGRAMS for y in years))
    return BudgetLP(model, spend, carry, cash, crew, veg_floor)


def solve_glop(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve an LP with GLOP, OR-Tools' simplex solver, and insist on an optimal answer."""
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"{model.name}: {result.termination.reason.name}")
    return result


def clean(number: float, digits: int = 4) -> float:
    """Round for printing, and turn the solver's -0.0 into 0.0."""
    return round(number, digits) + 0.0
