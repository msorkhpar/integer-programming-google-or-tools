"""What every program of module 21 shares: a quiet Gurobi environment, GridCap's models in gurobipy, and a mask.

`quiet_env` starts a Gurobi environment with `OutputFlag=0` set before it starts, so neither the
license banner nor a solver log reaches the program's output. `mask` hides what a Gurobi message
can say about the machine and the license holder: user, host, host id, core count, e-mail
addresses and license ids. Every message a program prints from Gurobi goes through it first.

`build_selection` is the project-selection model of lesson 4.2.1 and `build_plan` the timing model
of lesson 6.4.1, written in gurobipy row for row. GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import gurobipy as gp
from gurobipy import GRB

from gridcap import Portfolio


def quiet_env() -> gp.Env:
    """A started environment that prints nothing: no license banner, no solver log."""
    env = gp.Env(empty=True)              # empty: parameters can be set before the license is read
    env.setParam("OutputFlag", 0)
    env.start()                           # reads the license; raises GurobiError if there is none
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
    """The text with every user, host, host id, core count, e-mail and license id replaced by a placeholder."""
    for pattern, placeholder in MASKS:
        text = pattern.sub(placeholder, text)
    return text


STATUS = {getattr(GRB.Status, n): n for n in dir(GRB.Status) if n.isupper()}   # 2 -> "OPTIMAL", ...


@dataclass
class Selection:
    model: gp.Model
    x: gp.tupledict                       # x[i] = 1: project i is in the plan
    budget: gp.tupledict                  # budget[y], one row per year


def build_selection(env: gp.Env, portfolio: Portfolio, integer: bool = True) -> Selection:
    """Fund projects, each at its earliest start, to maximize NPV within each year's budget."""
    m = gp.Model(f"{portfolio.name}-selection", env=env)
    vtype = GRB.BINARY if integer else GRB.CONTINUOUS
    x = m.addVars(portfolio.project_ids, lb=0.0, ub=1.0, vtype=vtype, name="x")
    for p in portfolio.projects:
        if p.must_do:
            m.addConstr(x[p.project_id] == 1, name=f"must_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        m.addConstr(gp.quicksum(x[i] for i in members) <= 1, name=f"alt_{g}")
    for p in portfolio.projects:
        if p.parent:
            m.addConstr(x[p.project_id] <= x[p.parent], name=f"needs_{p.project_id}")
    budget = m.addConstrs(
        (gp.quicksum(p.spend(p.earliest_start).get(y, 0) * x[p.project_id] for p in portfolio.projects)
         <= portfolio.budget[y] for y in portfolio.years), name="budget")
    m.setObjective(gp.quicksum(p.value * x[p.project_id] for p in portfolio.projects), GRB.MAXIMIZE)
    return Selection(m, x, budget)


@dataclass
class Plan:
    model: gp.Model
    x: gp.tupledict                                        # x[i, t] = 1: project i starts in year t
    once: dict[str, gp.Constr] = field(default_factory=dict)   # once_i or must_i
    budget: dict[int, gp.Constr] = field(default_factory=dict)
    spend: dict[int, gp.LinExpr] = field(default_factory=dict)
    npv: gp.LinExpr = field(default_factory=gp.LinExpr)


def build_plan(env: gp.Env, portfolio: Portfolio) -> Plan:
    """The timing model of lesson 6.4.1, with the row names lesson 4.3.5's MathOpt model uses."""
    m = gp.Model(f"{portfolio.name} plan", env=env)
    keys = [(p.project_id, t) for p in portfolio.projects for t in p.starts()]
    x = m.addVars(keys, vtype=GRB.BINARY, name="x")
    pl = Plan(m, x)
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        started = x.sum(p.project_id, "*")                 # every start year of project p
        if p.must_do:
            pl.once[p.project_id] = m.addConstr(started == 1, name=f"must_{p.project_id}")
        else:
            pl.once[p.project_id] = m.addConstr(started <= 1, name=f"once_{p.project_id}")
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
    pl.spend = {y: gp.LinExpr() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                if year in pl.spend:
                    pl.spend[year].add(x[p.project_id, t], amount)
    pl.budget = {y: m.addConstr(pl.spend[y] <= portfolio.budget[y], name=f"budget_{y}") for y in portfolio.years}
    pl.npv = gp.quicksum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
    m.setObjective(pl.npv, GRB.MAXIMIZE)
    return pl


def chosen(pl: Plan) -> dict[str, int]:
    """Project id -> start year, read from the model's current solution."""
    return {i: t for (i, t), v in pl.x.items() if v.X > 0.5}
