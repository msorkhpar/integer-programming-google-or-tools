"""Copy a MathOpt model, row for row and name for name, into gurobipy, Pyomo or CP-SAT.

Lesson 9.1.3 asks three tools for an IIS of the same model. Building the GridCap plan three times
by hand would risk three slightly different models; these converters copy what MathOpt holds
(variables with bounds and integrality, linear rows with both bounds, the linear objective), so all
three tools see exactly the same rows under the same names. Lesson 9.1.5 uses the CP-SAT copy.

`quiet_env` starts Gurobi with `OutputFlag=0` set before the license is read, so neither the
license banner nor a log reaches the output (lesson 5.3.3 does the same).
"""

from __future__ import annotations

import math

import gurobipy as gp
import pyomo.environ as pyo
from gurobipy import GRB
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model


def quiet_env() -> gp.Env:
    """A started Gurobi environment that prints nothing."""
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    env.start()
    return env


def to_gurobi(model: mathopt.Model, env: gp.Env) -> gp.Model:
    g = gp.Model(model.name, env=env)
    var = {v: g.addVar(lb=v.lower_bound, ub=v.upper_bound, vtype=GRB.INTEGER if v.integer else GRB.CONTINUOUS,
                       name=v.name) for v in model.variables()}
    for row in model.linear_constraints():
        expr = gp.quicksum(t.coefficient * var[t.variable] for t in row.terms())
        lo, hi = row.lower_bound, row.upper_bound
        if lo == hi:
            g.addConstr(expr == hi, name=row.name)
        elif math.isinf(lo):
            g.addConstr(expr <= hi, name=row.name)
        elif math.isinf(hi):
            g.addConstr(expr >= lo, name=row.name)
        else:
            g.addRange(expr, lo, hi, name=row.name)
    objective = model.objective
    g.setObjective(gp.quicksum(t.coefficient * var[t.variable] for t in objective.linear_terms())
                   + objective.offset, GRB.MAXIMIZE if objective.is_maximize else GRB.MINIMIZE)
    g.update()
    return g


def to_pyomo(model: mathopt.Model) -> pyo.ConcreteModel:
    m = pyo.ConcreteModel(model.name.replace(" ", "_"))
    names = [v.name for v in model.variables()]
    m.x = pyo.Var(names)
    for v in model.variables():
        m.x[v.name].domain = pyo.Integers if v.integer else pyo.Reals
        m.x[v.name].setlb(None if math.isinf(v.lower_bound) else v.lower_bound)
        m.x[v.name].setub(None if math.isinf(v.upper_bound) else v.upper_bound)
    rows = list(model.linear_constraints())
    m.rows = pyo.Constraint([r.name for r in rows])
    for r in rows:
        body = sum(t.coefficient * m.x[t.variable.name] for t in r.terms())
        lo = None if math.isinf(r.lower_bound) else r.lower_bound
        hi = None if math.isinf(r.upper_bound) else r.upper_bound
        m.rows[r.name] = (lo, body, hi) if lo != hi else (body == hi)
    objective = model.objective
    m.obj = pyo.Objective(expr=sum(t.coefficient * m.x[t.variable.name] for t in objective.linear_terms()),
                          sense=pyo.maximize if objective.is_maximize else pyo.minimize)
    return m


def to_cpsat(model: mathopt.Model, flagged=()) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    """A CP-SAT copy of a model with integer data. Each row named in `flagged` holds only when its
    Boolean flag is true (`only_enforce_if`); the flags are returned by row name."""
    cp = cp_model.CpModel()
    var = {}
    for v in model.variables():
        if not v.integer:
            raise ValueError(f"CP-SAT needs integer variables; {v.name} is continuous")
        var[v] = cp.new_int_var(int(v.lower_bound), int(v.upper_bound), v.name)
    flags = {}
    for row in model.linear_constraints():
        expr = sum(int(t.coefficient) * var[t.variable] for t in row.terms())
        lo = cp_model.INT_MIN if math.isinf(row.lower_bound) else int(row.lower_bound)
        hi = cp_model.INT_MAX if math.isinf(row.upper_bound) else int(row.upper_bound)
        ct = cp.add_linear_constraint(expr, lo, hi)
        if row.name in flagged:
            flags[row.name] = cp.new_bool_var(f"flag_{row.name}")
            ct.only_enforce_if(flags[row.name])
    objective = sum(int(t.coefficient) * var[t.variable] for t in model.objective.linear_terms())
    if model.objective.is_maximize:
        cp.maximize(objective)
    else:
        cp.minimize(objective)
    return cp, flags
