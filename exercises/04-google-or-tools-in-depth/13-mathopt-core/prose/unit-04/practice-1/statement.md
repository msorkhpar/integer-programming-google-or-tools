An airline's crew-pairing service runs on whichever solver its configuration names, and its operators
set four things: a time budget in seconds, a relative gap, a thread count and a random seed. They can
also ask a MILP solve to stop at its first plan, for a quick feasibility check. The service must
never send a parameter the chosen solver refuses, because in OR-Tools 9.15 a refusal stops the solve.

Write `params_for(solver, seconds, rel_gap, threads, seed, first_plan=False)` in `params.py`. It
returns a `mathopt.SolveParameters` with:

- `time_limit` set to `seconds` as a `datetime.timedelta`, and `relative_gap_tolerance` set to
  `rel_gap`, for every solver;
- `threads` set to `threads`, except for HiGHS, which refuses the common parameter;
- `random_seed` set to `seed`, except for PDLP, which refuses it;
- `solution_limit=1` when `first_plan` is true, for HiGHS, SCIP and CP-SAT only (GLOP and PDLP solve
  LPs and refuse a solution limit).

Every field you do not set stays at its default, `None`, which means the solver's own default. The
tests build the parameters for each solver and solve a model with them, so a refused setting shows up
as an exception from `mathopt.solve`.
