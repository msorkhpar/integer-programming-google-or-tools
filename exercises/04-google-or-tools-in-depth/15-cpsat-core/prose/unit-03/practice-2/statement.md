A haulage firm (not GridCap) loads a truck with crates by solving a CP-SAT model that maximizes the
value of the load. The dispatcher does not need the proven best load: any load worth at least a
target is good enough, and the truck should leave as soon as one is found. The dispatcher also wants
to see how the value improved along the way.

Write the class `TargetStopper(target)` in `stopper.py`, a `cp_model.CpSolverSolutionCallback`. Each
time the solver reports a solution, append its objective value to `self.objectives`; when that value
reaches the target, stop the search. In the lesson's terms, for the solutions $`1, 2, \dots`$ the
search reports with objective values $`o_1 < o_2 < \dots`$, the callback records them until the
first $`t`$ with

```math
o_t \ge \text{target}
```

and stops there. The tests run the same model with one worker, so every run reports the same
solutions in the same order. About four lines.
