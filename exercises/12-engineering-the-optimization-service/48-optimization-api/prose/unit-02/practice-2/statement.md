The crew-roster service solves with CP-SAT (lesson 4.4.1), not MathOpt, and CP-SAT has its own status
codes. The job service still promises its callers the same four finished statuses as the lesson's:
`optimal`, `time_limit`, `infeasible` and `failed`. Something has to translate.

Write `outcome(status, objective, bound, limit_s)` in `roster_outcome.py`. The roster model
maximizes; `objective` and `bound` are the solver's `objective_value` and `best_objective_bound`,
and `limit_s` is the time limit the job ran with (the only limit the service sets). Return a dict
with `status`, `value` (the roster's value, or `None` when there is no roster), `gap` (or `None`)
and a one-sentence `message` for the planner.

CP-SAT's statuses, as lesson 4.4.1 teaches them:

| CP-SAT status | What it says |
| --- | --- |
| `cp_model.OPTIMAL` | a roster was found and proven best |
| `cp_model.FEASIBLE` | a roster was found; a limit stopped the search before the proof |
| `cp_model.INFEASIBLE` | proven: no roster meets every rule |
| `cp_model.UNKNOWN` | a limit stopped the search before any roster was found or any proof |
| `cp_model.MODEL_INVALID` | the model itself was refused |

Map each to the service status that tells a planner the truth, as lesson 9.1.1's distinctions do.
The gap is the distance from the roster's value to the bound, as a share of the roster's value
(with 1 as the smallest divisor, so a roster worth 0 does not divide by zero). A roster proven
best has a gap of exactly `0.0`, whatever the two numbers say; a roster stopped by the limit has the
gap computed from them, never below 0; a job with no roster has `None`. The tests use two
real CP-SAT solves and three hand-made statuses, so any correct mapping passes.
