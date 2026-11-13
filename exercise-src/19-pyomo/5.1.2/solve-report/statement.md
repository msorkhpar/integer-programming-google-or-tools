A crew-rostering service runs a Pyomo model every night and posts one line about the result to the
operations channel. Last week a roster nobody could meet crashed the job with an exception, and a
model with a missing bound was posted as "infeasible", which sent a planner looking for a conflict
that did not exist.

Write `outcome(model, **options)` in `report.py`. Solve `model` with HiGHS through Pyomo's newer
interface (`SolverFactory("highs")` from `pyomo.contrib.solver.common.factory`), passing `options`
on to `solve`, and **never raise** because of the result. Return a dict:

- `"status"`: the word `WORDS` gives the termination condition, or `"stopped"` for any condition
  `WORDS` does not list;
- `"objective"`: the incumbent's objective when the solve has a solution (its solution status is
  optimal or feasible), else `None`;
- `"plan"`: when there is a solution, `{v.name: v.value}` for every variable of the model after the
  solution is loaded; else `{}`.

`WORDS` and the imports are in the starter. The tests build small rostering models: one with an
optimum, one no roster can meet, and one whose objective can improve forever. About twelve lines.
