"""Lesson 6.4.1's multi-period GridCap model, ported from MathOpt to a Pyomo ConcreteModel.

GridCap is a fictional utility's portfolio. Every rule lesson 6.4.1 builds with
`timing_model.build` is here: start variables only inside each project's window, once and must-do
rows, one project per alternative group, cumulative precedence with a lag, and a budget per year with each project's cost
spread over the years it is worked on. The Sets, Params, Vars and Constraints are Pyomo's indexed
components; nothing is solved here.
"""

from __future__ import annotations

import pyomo.environ as pyo

from gridcap import Portfolio


def build(portfolio: Portfolio, *, integer: bool = True) -> pyo.ConcreteModel:
    projects = portfolio.projects
    m = pyo.ConcreteModel(name=f"{portfolio.name} timing")

    # Sets: the indices, from the data.
    m.P = pyo.Set(initialize=[p.project_id for p in projects])
    m.Y = pyo.Set(initialize=portfolio.years)
    m.S = pyo.Set(dimen=2, initialize=[(p.project_id, t) for p in projects for t in p.starts()])
    m.M = pyo.Set(within=m.P, initialize=[p.project_id for p in projects if p.must_do])
    m.G = pyo.Set(initialize=sorted({p.alt_group for p in projects if p.alt_group}))
    m.members = pyo.Set(m.G, within=m.P,
                        initialize={g: [p.project_id for p in projects if p.alt_group == g] for g in m.G})
    m.C = pyo.Set(dimen=2, initialize=[(c.project_id, t) for c in projects if c.parent for t in c.starts()])

    # Params: the numbers, keyed by those indices.
    m.npv = pyo.Param(m.S, initialize={(p.project_id, t): p.npv[t] for p in projects for t in p.starts()})
    m.cost = pyo.Param(m.S, m.Y, default=0, initialize={
        (p.project_id, t, y): amount for p in projects for t in p.starts() for y, amount in p.spend(t).items()})
    m.budget = pyo.Param(m.Y, initialize=dict(portfolio.budget), mutable=True)
    m.parent = pyo.Param(m.P, within=m.P, initialize={p.project_id: p.parent for p in projects if p.parent})
    m.lag = pyo.Param(m.P, default=0, initialize={p.project_id: p.parent_lag for p in projects if p.parent})

    # Vars: x[i, t] = 1 if project i starts in year t, only for (i, t) in S.
    m.x = pyo.Var(m.S, domain=pyo.Binary if integer else pyo.UnitInterval)

    def started(m, i, by=None):
        """Sum of project i's start variables, up to year `by` if given (0 if there are none)."""
        return sum(m.x[j, t] for j, t in m.S if j == i and (by is None or t <= by))

    def once_rule(m, i):
        return started(m, i) == 1 if i in m.M else started(m, i) <= 1
    m.once = pyo.Constraint(m.P, rule=once_rule)

    def alt_rule(m, g):
        return sum(started(m, i) for i in m.members[g]) <= 1
    m.alt = pyo.Constraint(m.G, rule=alt_rule)

    def after_rule(m, c, t):
        return started(m, c, by=t) <= started(m, m.parent[c], by=t - m.lag[c])
    m.after = pyo.Constraint(m.C, rule=after_rule)

    def budget_rule(m, y):
        spend = sum(m.cost[i, t, y] * m.x[i, t] for i, t in m.S if m.cost[i, t, y])
        if isinstance(spend, int):          # no project can spend in year y: no row
            return pyo.Constraint.Skip
        return spend <= m.budget[y]
    m.spend_cap = pyo.Constraint(m.Y, rule=budget_rule)

    m.value = pyo.Objective(expr=sum(m.npv[i, t] * m.x[i, t] for i, t in m.S), sense=pyo.maximize)
    return m


def schedule(m: pyo.ConcreteModel) -> dict[str, int]:
    """Project id -> start year, for every project the loaded solution starts."""
    return {i: t for i, t in m.S if pyo.value(m.x[i, t]) > 0.5}


def highs(gap: float = 0.0):
    """HiGHS through Pyomo's appsi interface, asked for a proven optimum."""
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = gap
    return solver
