A logistics team (not GridCap) runs its MIP models through OR-Tools' linear solver wrapper, and lets
each deployment list its preferred solvers in order, such as `["GUROBI", "CBC", "SCIP"]`. The same
list runs on laptops, on build machines and in containers that have different solvers, so the
service must use the first preference that is actually there and can solve a MIP.

Write `pick_backend(preferences)` in `backend.py`. It returns the first solver ID in `preferences`
for which both hold, or `None` when none does:

- `pywraplp.Solver.CreateSolver(id)` returns a solver, not `None`;
- that solver solves MIPs: its `IsMip()` is true. An LP-only solver given an integer variable solves
  the LP relaxation and still reports `OPTIMAL` (the lesson's last section shows it), so it must
  never be picked for a MIP.

Never fall back to a solver that is not in the list. The tests run in the course runner's
OR-Tools 9.15.6755. About six lines.
