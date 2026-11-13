A staffing team's models are LPs and small MILPs, and when one comes back infeasible they want the
rows to blame without a commercial solver. HiGHS can tell them whether a model is feasible; the
**deletion filter** turns that yes/no answer into an irreducible infeasible subsystem.

Write `deletion_filter(model)` in `iis.py`. It receives an infeasible Pyomo model and returns the
sorted names of the rows of one irreducible infeasible subsystem; variable bounds always stay.

1. Deactivate the objective: only feasibility matters. Objectives and constraints both have
   `.deactivate()` and `.activate()`; for the objective the reference calls `objective.deactivate()` on each
   one `model.component_data_objects(pyo.Objective, active=True)` yields.
2. Take each active row in turn (`model.component_data_objects(pyo.Constraint, active=True)`).
   Call `row.deactivate()` and ask `feasible(model)` (in the starter).
   If the model is now feasible, the row is part of the conflict: `row.activate()` and keep it.
   If the model is still infeasible, leave the row out for good.
3. The rows left active at the end are the subsystem.

The tests use models with one conflict and with two unrelated ones. About ten lines.
