"""The GridCap multi-period plan as a CP-SAT model, the model every program of module 17 tunes.

GridCap is a fictional utility's portfolio. The model is a start-year plan (lesson 6.4.1, later in the course, treats it in depth: start-year
binaries, once and must-do rows, alternatives, cumulative precedence, yearly budgets) plus crew
caps, written with `cp_model`. With `flags=True` every rule group is guarded by its own Boolean
flag (`only_enforce_if`), so lesson 4.6.2 can ask the solver which flags clash.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from gridcap import Portfolio


@dataclass
class Plan:
    model: cp_model.CpModel
    x: dict[tuple[str, int], cp_model.IntVar]             # x[i, t] = 1: project i starts in year t
    flags: dict[str, cp_model.IntVar] = field(default_factory=dict)   # rule name -> its flag


def active(project, t: int, year: int) -> bool:
    """Is a project that starts in year t being worked on in `year`?"""
    return t <= year < t + project.duration


def build(portfolio: Portfolio, *, budget_scale: float = 1.0, crews: bool = True,
          flags: bool = False) -> Plan:
    model = cp_model.CpModel()
    x = {(p.project_id, t): model.new_bool_var(f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}
    plan = Plan(model, x)

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

    def rule(name: str, constraint) -> None:
        """Add a row; with flags on, the row holds only when its flag is true."""
        if flags:
            plan.flags[name] = model.new_bool_var(f"flag_{name}")
            constraint.only_enforce_if(plan.flags[name])

    for p in portfolio.projects:
        model.add(started(p.project_id) <= 1)                       # once: never a rule to drop
        if p.must_do:
            rule(f"must_{p.project_id}", model.add(started(p.project_id) >= 1))
    for g in sorted({p.alt_group for p in portfolio.projects if p.alt_group}):
        rule(f"alt_{g}", model.add(sum(started(p.project_id) for p in portfolio.projects
                                       if p.alt_group == g) <= 1))
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                rule(f"after_{c.project_id}_{t}",
                     model.add(sum(x[c.project_id, u] for u in c.starts() if u <= t)
                               <= sum(x[c.parent, s] for s in by_id[c.parent].starts() if s <= t - c.parent_lag)))
    for y in portfolio.years:
        cap = int(portfolio.budget[y] * budget_scale)
        rule(f"budget_{y}", model.add(sum(p.spend(t)[y] * x[p.project_id, t] for p in portfolio.projects
                                          for t in p.starts() if y in p.spend(t)) <= cap))
    if crews:
        for (g, y), months in sorted(portfolio.crews.items()):
            use = [p.crew_months * x[p.project_id, t] for p in portfolio.projects if p.program == g
                   for t in p.starts() if active(p, t, y)]
            if use:
                rule(f"crews_{g}_{y}", model.add(sum(use) <= months))
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return plan


def schedule(plan: Plan, solver: cp_model.CpSolver) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in plan.x.items() if solver.value(v)}
