A transport planner's model is infeasible, and the team has a `mathopt.ComputeInfeasibleSubsystemResult`
for it, from Gurobi through `compute_infeasible_subsystem` or from a hand-made deletion filter
(lesson 4.3.5). Write `explain(result)`, which turns it into sorted lines the planner can read:

| In `result.infeasible_subsystem` | Line |
| --- | --- |
| a row in `linear_constraints` with its `lower` side | `"<row name> >= <its lower bound>"` |
| a row with its `upper` side | `"<row name> <= <its upper bound>"` |
| a variable in `variable_bounds` with its `lower` side | `"<variable name> >= <its lower bound>"` |
| a variable with its `upper` side | `"<variable name> <= <its upper bound>"` |
| a variable in `variable_integrality` | `"<variable name> is integer"` |

Bounds are written with `:g` (so 120.0 prints as `120`). List only the sides the subsystem marks:
an equality row can be in it with only one side. If `result.feasibility` is not `INFEASIBLE`, the
subsystem means nothing and the function returns an empty list. Return the lines sorted. About
twelve lines.
