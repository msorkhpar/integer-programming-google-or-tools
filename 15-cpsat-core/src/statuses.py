"""Lesson 4.4.1: the five answers CpSolver.solve can give, each produced on GridCap small.

GridCap is a fictional utility's portfolio. Each run uses one worker, so it repeats exactly.
"""

from dataclasses import replace

from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import one_worker, selection

small = generate("small")


def report(label: str, sel, solver: cp_model.CpSolver, status) -> None:
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"{label:34} {solver.status_name(status):13} objective {solver.objective_value:>9,.0f}"
              f"  bound {solver.best_objective_bound:>9,.0f}")
    else:
        print(f"{label:34} {solver.status_name(status):13} no plan to read")


sel = selection(small)
solver = one_worker()
report("full search", sel, solver, solver.solve(sel.model))

solver = one_worker()
solver.parameters.stop_after_first_solution = True
report("stop after the first plan", sel, solver, solver.solve(sel.model))

solver = one_worker()
solver.parameters.max_number_of_conflicts = 0
solver.parameters.cp_model_presolve = False
report("no search allowed", sel, solver, solver.solve(sel.model))

must = sum(p.capex for p in small.projects if p.must_do)
cut = replace(small, capital_budget=must - 2_100)           # the must-do work no longer fits
sel_cut = selection(cut)
solver = one_worker()
report(f"budget ${cut.capital_budget:,}k (must-do ${must:,}k)", sel_cut, solver, solver.solve(sel_cut.model))

broken = selection(small)
broken.model.add(broken.k * 2**61 + broken.k * 2**61 >= 1)  # coefficients that can overflow
solver = one_worker()
report("a row that can overflow", broken, solver, solver.solve(broken.model))
print("validate:", broken.model.validate().splitlines()[0])
