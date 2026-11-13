"""Lesson 5.1.1: the parts of a Pyomo ConcreteModel, one component at a time, on GridCap tiny.

GridCap is a fictional utility's portfolio. Each block below builds one kind of indexed component
and prints what Pyomo made of it.
"""

import pyomo.environ as pyo

from gridcap import generate
from pyomo_timing import build

tiny = generate("tiny")

# Sets: a plain set of projects, and a set of (project, year) pairs that holds only allowed starts.
m = pyo.ConcreteModel()
m.P = pyo.Set(initialize=[p.project_id for p in tiny.projects])
m.Y = pyo.Set(initialize=tiny.years)
m.S = pyo.Set(dimen=2, initialize=[(p.project_id, t) for p in tiny.projects for t in p.starts()])
print("P:", list(m.P))
print(f"P x Y has {len(m.P * m.Y)} pairs; S has {len(m.S)}:", list(m.S)[:4], "...")

# Params: data keyed by a set. An index outside the set is an error; a default fills the gaps inside it.
m.npv = pyo.Param(m.S, initialize={(p.project_id, t): p.npv[t] for p in tiny.projects for t in p.starts()})
m.cost = pyo.Param(m.S, m.Y, default=0, initialize={
    (p.project_id, t, y): c for p in tiny.projects for t in p.starts() for y, c in p.spend(t).items()})
m.budget = pyo.Param(m.Y, initialize=dict(tiny.budget), mutable=True)
print("npv[P001,2029] =", m.npv["P001", 2029], "  budget[2027] =", pyo.value(m.budget[2027]))
print("cost[P003,2027,2028] =", m.cost["P003", 2027, 2028], "  cost[P003,2027,2029] =", m.cost["P003", 2027, 2029])
try:
    m.npv["P001", 2027]
except KeyError as error:
    print("npv[P001,2027]:", type(error).__name__, error)

# Vars: one per member of S, with its domain.
m.x = pyo.Var(m.S, domain=pyo.Binary)
print(f"x: {len(m.x)} variables, x[P001,2028] in {m.x['P001', 2028].domain}, bounds {m.x['P001', 2028].bounds}")


# Constraints: a rule called once per index; Constraint.Skip writes no row for that index.
def once_rule(m, i):
    starts = [m.x[j, t] for j, t in m.S if j == i]
    if len(starts) == 1:
        return pyo.Constraint.Skip       # one start variable: its 0/1 domain already says "at most once"
    return sum(starts) <= 1


m.once = pyo.Constraint(m.P, rule=once_rule)
print("once rows:", [m.once[i].name for i in m.once], f"({len(m.once)} of {len(m.P)} projects)")
print("once[P008]:", m.once["P008"].expr)

# A rule that returns True or False instead of a row is an error, not a skipped row.
try:
    m.bad = pyo.Constraint(rule=lambda m: sum(m.x[i, t] for i, t in m.S if t == 2035) <= 1)
except ValueError as error:
    print("bad:", type(error).__name__, str(error).splitlines()[0])

# A mutable Param stays a name inside every row that uses it, so a new value reaches the row.
full = build(tiny)
print("spend_cap[2027] upper side:", full.spend_cap[2027].upper, "=", pyo.value(full.spend_cap[2027].upper))
full.budget[2027] = 1500
print("after full.budget[2027] = 1500:", full.spend_cap[2027].upper, "=", pyo.value(full.spend_cap[2027].upper))
