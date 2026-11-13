"""The first builder a team writes from DataFrames: correct, readable, and slow on 10,000 projects.

It reads the tables of `tables.py` row by row with `iterrows` and finds each project's rows with a
boolean mask, so every lookup scans a whole table. GridCap is fictional.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from tables import Tables


def build_slow(t: Tables) -> mathopt.Model:
    model = mathopt.Model(name=f"{t.name} timing")
    x = {}
    for _, s in t.starts.iterrows():
        x[s.project_id, int(s.start)] = model.add_variable(
            lb=0, ub=1, is_integer=True, name=f"x_{s.project_id}_{s.start}")

    def starts_of(pid: str) -> list[int]:
        return [int(s) for s in t.starts[t.starts.project_id == pid]["start"]]    # scans every start row

    for _, p in t.projects.iterrows():
        started = sum(x[p.project_id, s] for s in starts_of(p.project_id))
        if p.must_do:
            model.add_linear_constraint(started == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started <= 1, name=f"once_{p.project_id}")
    for g in t.projects[t.projects.alt_group != ""]["alt_group"].unique():
        members = t.projects[t.projects.alt_group == g]["project_id"]
        model.add_linear_constraint(sum(x[m, s] for m in members for s in starts_of(m)) <= 1, name=f"alt_{g}")
    for _, c in t.projects[t.projects.parent != ""].iterrows():
        mine, parents, lag = starts_of(c.project_id), starts_of(c.parent), int(c.parent_lag)
        for start in mine:
            model.add_linear_constraint(
                sum(x[c.project_id, u] for u in mine if u <= start)
                <= sum(x[c.parent, s] for s in parents if s <= start - lag),
                name=f"after_{c.project_id}_{start}")
    spend = {int(y): 0 for y in t.budget["year"]}
    for _, s in t.starts.iterrows():
        profile = t.costs[t.costs.project_id == s.project_id]                     # scans every cost row
        for _, c in profile.iterrows():
            spend[int(s.start) + int(c.k)] += int(c.amount) * x[s.project_id, int(s.start)]
    for _, b in t.budget.iterrows():
        model.add_linear_constraint(spend[int(b.year)] <= int(b.budget), name=f"budget_{b.year}")
    model.maximize(sum(int(s.npv) * x[s.project_id, int(s.start)] for _, s in t.starts.iterrows()))
    return model
