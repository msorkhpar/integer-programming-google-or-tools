"""The GridCap timing model in gurobipy, opened in a quiet environment, for lesson 10.2.2.

GridCap is a fictional utility's portfolio. `quiet_env` sets `OutputFlag=0` before the environment
starts, so no license banner or log is printed, and `mask` hides what a Gurobi message can say about
the machine or the license holder (user, host, host id, cores, e-mail, license id), as in lessons
5.3.1 and 5.3.4. The programs print only numbers and error codes from Gurobi, never its messages.
"""

from __future__ import annotations

import re

import gurobipy as gp
from gurobipy import GRB

from gridcap import Portfolio
from plan_model import ordered, weight


def quiet_env() -> gp.Env:
    """A started environment that prints nothing; raises GurobiError if there is no license."""
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    return env


MASKS = [
    (re.compile(r"\buser [^,)]*"), "user <user>"),
    (re.compile(r"\bhost [^,)]*"), "host <host>"),
    (re.compile(r"\bhostid [^,)]*"), "hostid <hostid>"),
    (re.compile(r"\bcores \d+"), "cores <n>"),
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "<email>"),
    (re.compile(r"(?i)(license ?id\D{0,12})\d+"), r"\1<id>"),
]


def mask(text: str) -> str:
    for pattern, placeholder in MASKS:
        text = pattern.sub(placeholder, text)
    return text


def build_gurobi(env: gp.Env, portfolio: Portfolio, order: list[str] | None = None,
                 objective: str = "npv") -> tuple[gp.Model, dict]:
    """The timing model of plan_model.build, row for row, in gurobipy."""
    projects = ordered(portfolio, order)
    by_id = {p.project_id: p for p in projects}
    m = gp.Model(f"{portfolio.name} plan", env=env)
    x = {(p.project_id, t): m.addVar(vtype=GRB.BINARY, name=f"x_{p.project_id}_{t}")
         for p in projects for t in p.starts()}
    for p in projects:
        started = gp.quicksum(x[p.project_id, t] for t in p.starts())
        m.addConstr(started == 1 if p.must_do else started <= 1)
    groups: dict[str, list[str]] = {}
    for p in projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for members in groups.values():
        m.addConstr(gp.quicksum(x[i, t] for i in members for t in by_id[i].starts()) <= 1)
    for c in projects:
        if c.parent:
            for t in c.starts():
                m.addConstr(gp.quicksum(x[c.project_id, u] for u in c.starts() if u <= t)
                            <= gp.quicksum(x[c.parent, s] for s in by_id[c.parent].starts()
                                           if s <= t - c.parent_lag))
    for y in portfolio.years:
        m.addConstr(gp.quicksum(p.spend(t)[y] * x[p.project_id, t] for p in projects
                                for t in p.starts() if y in p.spend(t)) <= portfolio.budget[y])
    m.setObjective(gp.quicksum(weight(p, t, objective) * x[p.project_id, t] for p in projects
                               for t in p.starts()), GRB.MAXIMIZE)
    return m, x
