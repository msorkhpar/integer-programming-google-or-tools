A hospital's theatre-scheduling team stores its ranked objectives the MathOpt way, as a list of
levels:

```python
{"name": "urgent", "priority": 0, "maximize": True, "abs_tol": None, "rel_tol": 0.02}
```

A lower `priority` is optimized first; a tolerance of `None` means "not set", which in MathOpt allows
no loss. An analyst wants to check the schedules in Gurobi, so the same levels must become
`Model.setObjectiveN` calls on a model whose `ModelSense` is `GRB.MAXIMIZE`.

Write `set_objective_n_args(levels)`. It returns one dict of keyword arguments per level, in the
order of `levels`, with the keys `index` (the level's position in the list), `priority`, `weight`,
`abstol`, `reltol` and `name`, so that each can be passed as `model.setObjectiveN(expr, **args)` and
Gurobi optimizes the objectives in the same order, with the same senses and the same tolerances as
MathOpt would. Any integers that give the right order are accepted. Gurobi's documentation (the
`setObjectiveN` docstring of gurobipy 13.0 and the multi-objective attributes page) types
`ObjNPriority` as an integer with default 0 and states no range, so it neither promises nor rules
out negative priorities. The reference does not rely on them: it maps each MathOpt priority $`p`$ to
$`p_{\max} - p`$, where $`p_{\max}`$ is the largest MathOpt priority in the list, so every Gurobi
priority is 0 or more and the level MathOpt solves first gets the largest. The tests only compare
the order the priorities give, so a negative mapping such as $`-p`$ passes them too.

The tests need no Gurobi license: they read your dicts. About eight lines.
