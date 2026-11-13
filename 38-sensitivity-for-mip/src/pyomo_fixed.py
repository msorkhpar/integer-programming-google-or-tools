"""Lesson 9.2.2: Pyomo's dual Suffix on a MILP. It does not run the fixed-integer re-solve; you do.

The same selection with routine line clearance as selection.py, written in Pyomo and solved with
HiGHS through Pyomo's appsi interface (the standalone highspy package). GridCap is fictional.
"""

import pyomo.environ as pyo

from gridcap import generate

small = generate("small")
RATE, CAP = 0.25, 800            # line clearance: $k of NPV per $k, and its cap (this module's assumption)


def build(budget: float) -> pyo.ConcreteModel:
    projects = {p.project_id: p for p in small.projects}
    m = pyo.ConcreteModel()
    m.x = pyo.Var(list(projects), domain=pyo.Binary)
    m.y = pyo.Var(bounds=(0, None))
    m.cap = pyo.Constraint(expr=m.y <= CAP)
    m.budget = pyo.Constraint(expr=sum(p.capex * m.x[i] for i, p in projects.items()) + m.y <= budget)
    m.must = pyo.Constraint([i for i, p in projects.items() if p.must_do], rule=lambda m, i: m.x[i] == 1)
    m.parent = pyo.Constraint([i for i, p in projects.items() if p.parent],
                              rule=lambda m, i: m.x[i] <= m.x[projects[i].parent])
    groups = sorted({p.alt_group for p in projects.values() if p.alt_group})
    m.alt = pyo.Constraint(groups, rule=lambda m, g: sum(m.x[i] for i, p in projects.items() if p.alt_group == g) <= 1)
    m.npv = pyo.Objective(expr=sum(p.value * m.x[i] for i, p in projects.items()) + RATE * m.y, sense=pyo.maximize)
    return m


def highs(presolve: bool = True):
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    if not presolve:
        solver.highs_options["presolve"] = "off"
    return solver


B = small.capital_budget

# 1. A dual Suffix on the MILP: Pyomo asks HiGHS for duals, and there are none.
m = build(B)
m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
try:
    highs().solve(m)
except RuntimeError as error:
    print("MILP with a dual Suffix:", error)

for presolve in (True, False):
    # 2. Solve the MILP without the Suffix.
    m = build(B)
    highs(presolve).solve(m)
    print(f"\npresolve {'on ' if presolve else 'off'}: MILP reported optimal, NPV {pyo.value(m.npv):,.1f},"
          f" clearance {m.y.value:,.0f}")
    # 3. Fixing the binaries is not enough: they are still declared Binary, so the model is still a MILP.
    for v in m.x.values():
        v.fix(round(v.value))
    m.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
    try:
        highs(presolve).solve(m)
    except RuntimeError as error:
        print("  fixed, still Binary:", error)
    # 4. Relax integrality, then solve the LP that is left: now the Suffix fills.
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(m)
    highs(presolve).solve(m)
    print(f"  fixed and relaxed: NPV {pyo.value(m.npv):,.1f}, budget dual {m.dual[m.budget]:g},"
          f" cap dual {m.dual[m.cap]:g}")
