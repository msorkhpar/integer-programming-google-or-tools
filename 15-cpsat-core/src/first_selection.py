"""Lesson 4.4.1: GridCap small's selection with crew rows and a credit line, solved by CP-SAT.

GridCap is a fictional utility's portfolio. The same model is solved with HiGHS through MathOpt to
check CP-SAT's answer.
"""

from ortools.sat.python import cp_model

from gridcap import PROGRAMS, generate
from cpsat_models import (EXACT, TRANCHE, crew_capacity, crew_need, funded, mathopt_selection, one_worker, selection,
                          solve_highs)

small = generate("small")
sel = selection(small)

solver = one_worker()
status = solver.solve(sel.model)
print("status:", solver.status_name(status))
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    plan = funded(sel, solver)
    print(f"objective {solver.objective_value:,.0f}   bound {solver.best_objective_bound:,.0f}")
    print(f"funded {len(plan)} projects: {' '.join(plan)}")
    print(f"tranches drawn {solver.value(sel.k)} -> ${TRANCHE * solver.value(sel.k):,}k borrowed")
    capex = sum(p.capex * sel.x[p.project_id] for p in small.projects)
    print(f"capex {solver.value(capex):,} of {small.capital_budget:,} + {TRANCHE * solver.value(sel.k):,}")
    own = crew_capacity(small)
    for g in PROGRAMS:
        use = sum(crew_need(p) * sel.x[p.project_id] for p in small.projects if p.program == g)
        print(f"  crews_{g:12} uses {solver.value(use):3} of {own[g]:3} crew-months")
    print("types:", type(solver.value(sel.k)).__name__, type(solver.boolean_value(sel.x["P001"])).__name__,
          type(solver.objective_value).__name__)

model, x, k = mathopt_selection(small)
result = solve_highs(model, EXACT)
print(f"HiGHS {result.termination.reason.name}  objective {result.objective_value():,.0f}  "
      f"same plan: {[pid for pid, v in x.items() if result.variable_values(v) > 0.5] == plan}")
