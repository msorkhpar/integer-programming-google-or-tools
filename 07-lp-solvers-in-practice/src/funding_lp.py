"""The funding LP of module 07: what share of each GridCap project to fund, with carry-over.

GridCap is a fictional utility's portfolio. Every project starts as early as it may; the LP decides
what share of it to fund (0 to 1) and how much unspent money to carry from one year to the next.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class FundingLP:
    model: mathopt.Model
    f: dict[str, mathopt.Variable]                  # f[i]: share of project i funded, 0..1
    carry: dict[int, mathopt.Variable]              # carry[y]: money carried out of year y, >= 0
    cash: dict[int, mathopt.LinearConstraint]       # cash_y: spend + carry out <= budget + carry in
    must: dict[str, mathopt.LinearConstraint]       # must_i: f[i] == 1 for a must-do project


def spend_in(project, year: int) -> int:
    """What project i spends in `year` if it starts as early as it may (0 outside its work years)."""
    return project.spend(project.earliest_start).get(year, 0)


def build(portfolio: Portfolio) -> FundingLP:
    model = mathopt.Model(name="funding-lp")
    f = {p.project_id: model.add_variable(lb=0, ub=1, name=f"f_{p.project_id}") for p in portfolio.projects}
    carry = {y: model.add_variable(lb=0, name=f"carry_{y}") for y in portfolio.years}
    cash = {}
    for k, y in enumerate(portfolio.years):
        spend = sum(spend_in(p, y) * f[p.project_id] for p in portfolio.projects if spend_in(p, y))
        carried_in = carry[portfolio.years[k - 1]] if k else 0
        cash[y] = model.add_linear_constraint(spend + carry[y] - carried_in <= portfolio.budget[y], name=f"cash_{y}")
    must = {p.project_id: model.add_linear_constraint(f[p.project_id] == 1, name=f"must_{p.project_id}")
            for p in portfolio.projects if p.must_do}
    model.maximize(sum(p.value * f[p.project_id] for p in portfolio.projects))
    return FundingLP(model, f, carry, cash, must)


def in_between(lp: FundingLP, result: mathopt.SolveResult, tol: float = 1e-6) -> int:
    """How many variables sit strictly between their bounds: shares in (0, 1), carries above 0."""
    shares = sum(1 for v in lp.f.values() if tol < result.variable_values(v) < 1 - tol)
    carries = sum(1 for v in lp.carry.values() if result.variable_values(v) > tol)
    return shares + carries
