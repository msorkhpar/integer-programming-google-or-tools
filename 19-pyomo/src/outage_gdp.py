"""Lesson 6.2.4's outage ordering, written once as a Pyomo.GDP disjunction per pair of jobs.

GridCap is a fictional utility's portfolio. Jobs that share a substation outage cannot overlap:
either i finishes before j starts, or j finishes before i starts. The disjunction is stated once;
a transformation (`gdp.bigm` or `gdp.hull`) turns it into MILP rows afterwards.
"""

from __future__ import annotations

from itertools import combinations

import pyomo.environ as pyo
from pyomo.gdp import Disjunction


def build(durations: dict[str, int], horizon: int) -> pyo.ConcreteModel:
    m = pyo.ConcreteModel(name="outage GDP")
    m.J = pyo.Set(initialize=list(durations))
    m.pairs = pyo.Set(dimen=2, initialize=list(combinations(durations, 2)))
    m.d = pyo.Param(m.J, initialize=durations)
    m.s = pyo.Var(m.J, bounds=lambda m, j: (0, horizon - m.d[j]))      # start month

    def order(m, i, j):
        return [[m.s[i] + m.d[i] <= m.s[j]],       # disjunct 0: i before j
                [m.s[j] + m.d[j] <= m.s[i]]]       # disjunct 1: j before i
    m.order = Disjunction(m.pairs, rule=order)

    m.finish = pyo.Objective(expr=sum(m.s[j] + m.d[j] for j in m.J), sense=pyo.minimize)
    return m


def first(m: pyo.ConcreteModel) -> dict[tuple[str, str], str]:
    """For each pair, the job the solution puts first, read from the disjuncts' indicator_var."""
    return {(i, j): i if m.order[i, j].disjuncts[0].indicator_var.value else j for i, j in m.pairs}
