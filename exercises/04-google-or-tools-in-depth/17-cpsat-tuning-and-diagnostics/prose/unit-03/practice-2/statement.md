A cooperative's planning service must give the same answer when an auditor reruns a past solve.
The model does not matter here; the solver settings do.

Write `repeatable_solver(seed, work)` in `repeatable.py`. Return a `cp_model.CpSolver` set up so
that solving the same model twice, on the same OR-Tools version, gives the same status, objective,
counts and plan every time: use `seed` as the random seed and stop after `work` units of
deterministic time.

Think about which settings make a run depend on the machine or on the clock, and leave every one of
them out. About four lines.
