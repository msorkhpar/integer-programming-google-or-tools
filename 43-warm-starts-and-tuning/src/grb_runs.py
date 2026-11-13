"""The regional timing model in gurobipy, solved with every new incumbent recorded against Gurobi's work units.

Gurobi's `Work` is its deterministic measure of effort (its documentation: very roughly a second,
depending on the machine and the model), and a callback can read it at each new incumbent
(`GRB.Callback.WORK` in `MIPSOL`). Runs here use one thread and a fixed seed.

Every environment starts quiet (lesson 5.3.1), and every Gurobi message a program keeps passes
through `mask` (lesson 5.3.4), because license messages name the user and the host. Programs keep
only the log lines about MIP starts.
"""

from __future__ import annotations

import math
import re

import gurobipy as gp
from gurobipy import GRB

from gridcap import Portfolio
from plan_model import groups, keys
from runs import Run

MASKS = [
    (re.compile(r"\buser (?!MIP start)[^,)]*"), "user <user>"),     # "User MIP start ..." is a log line, not a name
    (re.compile(r"\bhost [^,)]*"), "host <host>"),
    (re.compile(r"\bhostid [^,)]*"), "hostid <hostid>"),
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "<email>"),
    (re.compile(r"(?i)(license ?id\D{0,12})\d+"), r"\1<id>"),
]


def mask(text: str) -> str:
    """The text with every user, host, host id, e-mail and license id replaced by a placeholder."""
    for pattern, placeholder in MASKS:
        text = pattern.sub(placeholder, text)
    return text


def quiet_env() -> gp.Env:
    """A started environment that prints nothing: no license banner, no solver log."""
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    return env


def build_gurobi(env: gp.Env, pf: Portfolio) -> tuple[gp.Model, dict]:
    m = gp.Model(pf.name, env=env)
    x = {(i, t): m.addVar(vtype=GRB.BINARY, name=f"x_{i}_{t}") for i, t in keys(pf)}
    by_id = {p.project_id: p for p in pf.projects}

    def started(i: str, by: int | None = None):
        return gp.quicksum(x[i, t] for t in by_id[i].starts() if by is None or t <= by)

    for p in pf.projects:
        if p.must_do:
            m.addConstr(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            m.addConstr(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    for g, members in groups(pf).items():
        m.addConstr(gp.quicksum(started(i) for i in members) <= 1, name=f"alt_{g}")
    for c in pf.projects:
        if c.parent:
            for t in c.starts():
                m.addConstr(started(c.project_id, t) <= started(c.parent, t - c.parent_lag),
                            name=f"after_{c.project_id}_{t}")
    for y in pf.years:
        m.addConstr(gp.quicksum(a * x[p.project_id, t] for p in pf.projects for t in p.starts()
                                for year, a in p.spend(t).items() if year == y) <= pf.budget[y],
                    name=f"budget_{y}")
    m.setObjective(gp.quicksum(p.npv[t] * x[p.project_id, t] for p in pf.projects for t in p.starts()),
                   GRB.MAXIMIZE)
    m.update()
    return m, x


def gurobi(env: gp.Env, pf: Portfolio, seed: int, start: dict | None = None, gap: float = 0.0,
           **params) -> Run:
    """Solve with Gurobi on one thread. `start` sets the `Start` attribute; `params` are Gurobi parameters."""
    m, x = build_gurobi(env, pf)
    m.Params.Threads = 1
    m.Params.Seed = seed
    m.Params.MIPGap = gap
    m.Params.LogToConsole = 0              # keep the log off the screen, then let callbacks see it
    m.Params.OutputFlag = 1
    for name, v in params.items():
        m.setParam(name, v)
    for k, v in (start or {}).items():
        if k in x:
            x[k].Start = v
    events: list[tuple[float, float]] = []
    kept: list[str] = []

    def callback(model, where):
        if where == GRB.Callback.MIPSOL:
            found = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            if not events or found > events[-1][1] + 1e-6:
                events.append((round(model.cbGet(GRB.Callback.WORK), 4), found))
        elif where == GRB.Callback.MESSAGE:
            line = model.cbGet(GRB.Callback.MSG_STRING).strip()
            if "MIP start" in line:
                kept.append(re.sub(r"\(\d+\.\d+s\)", "(<t>s)", mask(line)))     # times change on every run

    m.optimize(callback)
    status = {GRB.OPTIMAL: "optimal" if gap == 0 else "gap reached"}.get(m.Status, f"status {m.Status}")
    plan = {i: t for (i, t), v in x.items() if v.X > 0.5} if m.SolCount else {}
    run = Run("Gurobi", pf.name, seed, status, m.ObjVal if m.SolCount else math.nan, m.ObjBound,
              round(m.Work, 4), tuple(events), plan, tuple(kept), m.Runtime)
    m.dispose()
    return run
