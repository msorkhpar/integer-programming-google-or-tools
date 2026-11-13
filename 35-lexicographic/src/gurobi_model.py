"""The start-year model of `lex_model.py`, written row for row in gurobipy, plus a quiet environment.

`quiet_env` sets `OutputFlag=0` before the environment starts, so neither the license banner nor a
solver log reaches the program's output. `mask` hides what a Gurobi message can say about the
machine and the license holder (user, host, host id, e-mail); every Gurobi message a program prints
goes through it first. The model has 80 variables and 49 rows on GridCap small, well inside the
size-limited license. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import gurobipy as gp
from gurobipy import GRB

from gridcap import Portfolio
from lex_model import coefficients


def quiet_env() -> gp.Env:
    """A started environment that prints nothing: no license banner, no solver log."""
    env = gp.Env(empty=True)              # empty: parameters can be set before the license is read
    env.setParam("OutputFlag", 0)
    env.start()
    return env


MASKS = [(re.compile(r"\b(user|host|hostid) [^,)]*"), r"\1 <hidden>"),
         (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "<email>")]


def mask(text: str) -> str:
    for pattern, placeholder in MASKS:
        text = pattern.sub(placeholder, text)
    return text


@dataclass
class GrbModel:
    model: gp.Model
    x: gp.tupledict                               # x[i, t] = 1: project i starts in year t
    objective: dict[str, gp.LinExpr]              # "npv", "risk", "spend"


def build(env: gp.Env, portfolio: Portfolio) -> GrbModel:
    m = gp.Model(f"{portfolio.name} lexicographic", env=env)
    keys = [(p.project_id, t) for p in portfolio.projects for t in p.starts()]
    x = m.addVars(keys, vtype=GRB.BINARY, name="x")
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        started = x.sum(p.project_id, "*")
        if p.must_do:
            m.addConstr(started == 1, name=f"must_{p.project_id}")
        else:
            m.addConstr(started <= 1, name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        m.addConstr(gp.quicksum(x.sum(i, "*") for i in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                m.addConstr(gp.quicksum(x[c.project_id, u] for u in c.starts() if u <= t)
                            <= gp.quicksum(x[parent.project_id, s] for s in parent.starts() if s <= t - c.parent_lag),
                            name=f"after_{c.project_id}_{t}")
    spend = {y: gp.LinExpr() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                if year in spend:
                    spend[year].add(x[p.project_id, t], amount)
    for y in portfolio.years:
        m.addConstr(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    coef = coefficients(portfolio)
    objective = {name: gp.quicksum(c[k] * x[k] for k in keys) for name, c in coef.items()}
    return GrbModel(m, x, objective)


def chosen(gm: GrbModel) -> dict[str, int]:
    """Project id -> start year, read from the model's current solution."""
    return {i: t for (i, t), v in gm.x.items() if v.X > 0.5}
