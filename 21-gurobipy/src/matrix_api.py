"""Lesson 5.3.1: GridCap small's selection model written as matrices, with addMVar and addMConstr."""

import numpy as np
import scipy.sparse as sp
import gurobipy as gp
from gurobipy import GRB

from gridcap import generate
from grb import STATUS, build_selection, quiet_env

env = quiet_env()
small = generate("small")
ids = list(small.project_ids)
col = {pid: j for j, pid in enumerate(ids)}
n = len(ids)

# Data as arrays: one column per project, one row per year (budget) or rule.
c = np.array([p.value for p in small.projects], dtype=float)
spend = sp.lil_matrix((len(small.years), n))
for p in small.projects:
    for y, amount in p.spend(p.earliest_start).items():
        if y in small.years:
            spend[small.years.index(y), col[p.project_id]] = amount
B = np.array([small.budget[y] for y in small.years], dtype=float)

groups: dict[str, list[str]] = {}
for p in small.projects:
    if p.alt_group:
        groups.setdefault(p.alt_group, []).append(p.project_id)
alt = sp.lil_matrix((len(groups), n))
for r, members in enumerate(groups.values()):
    for pid in members:
        alt[r, col[pid]] = 1
children = [p for p in small.projects if p.parent]
needs = sp.lil_matrix((len(children), n))             # x_child - x_parent <= 0
for r, p in enumerate(children):
    needs[r, col[p.project_id]] = 1
    needs[r, col[p.parent]] = -1
lb = np.array([1.0 if p.must_do else 0.0 for p in small.projects])   # must-do: x_i = 1 as a bound

m = gp.Model("small-matrix", env=env)
xv = m.addMVar(n, lb=lb, ub=1.0, vtype=GRB.BINARY, name="x")
m.addMConstr(spend.tocsr(), xv, "<", B, name="budget")
m.addMConstr(alt.tocsr(), xv, "<", np.ones(len(groups)), name="alt")
m.addMConstr(needs.tocsr(), xv, "<", np.zeros(len(children)), name="needs")
m.setObjective(c @ xv, GRB.MAXIMIZE)
m.Params.MIPGap = 0.0
m.optimize()
print("matrix model :", STATUS[m.Status], m.ObjVal, "|", m.NumVars, "variables,", m.NumConstrs, "rows")
print("x as an array:", xv.X[:10].round().astype(int), "...")

# The same model built row by row has the same optimum, and getA() hands back its matrix.
sel = build_selection(env, small)
sel.model.Params.MIPGap = 0.0
sel.model.optimize()
A = sel.model.getA()
print("row by row   :", STATUS[sel.model.Status], sel.model.ObjVal, "|", sel.model.NumVars, "variables,",
      sel.model.NumConstrs, "rows")
print("getA():", type(A).__name__, A.shape, "nonzeros", A.nnz)
print("budget rows of getA() equal the spend matrix:",
      bool((A[[sel.budget[y].index for y in small.years], :] != spend.tocsr()).nnz == 0))
