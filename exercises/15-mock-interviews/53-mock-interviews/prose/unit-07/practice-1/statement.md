A rail operator's planners ask, for every track renewal, "what would it cost to decide the other
way?". `costs.py` already builds the one-budget selection: a binary per renewal, the budget row, a
row per must-do, and the most value as the objective. Write `decision_costs(projects, budget)`:

- Solve once, to proven optimality (the module gives `EXACT`), and note which renewals are funded.
- For each renewal in turn, reverse its decision: a funded one is forced out, an unfunded one forced
  in. Re-solve, and record the best value lost, the base optimum minus the forced optimum.
- When the rules refuse the reversal, record `None`, not a number. A refused reversal is a forced
  model that has no plan: HiGHS ends it with `TerminationReason.INFEASIBLE` (a must-do forced out,
  for one). Record a number only when the re-solve ends `OPTIMAL`.

Build the model once and change only the reversed renewal's bounds for each re-solve, so that each
reversal is priced on its own. The tests compare with brute force. About fifteen lines.
