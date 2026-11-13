An operations dashboard shows a long MIP solve's progress as a line: the value of the best plan found
so far, after each solution the solver reports. Lesson 4.3.5 showed that SCIP reports *every*
feasible solution its heuristics find, worse ones included, so the callback has to keep the best
itself.

Write `make_tracker(objective, maximize)`. `objective` is a dict from variable to its objective
coefficient; `maximize` says the sense. It returns a pair `(callback, history)`:

- `history`, a list, empty at first;
- `callback`, a function for `Event.MIP_SOLUTION`. Given a `mathopt.CallbackData`, it computes the
  reported solution's objective value $`\sum_v c_v \cdot \text{solution}[v]`$, appends the best value
  seen so far (the largest when maximizing, the smallest when minimizing) to `history`, and returns
  an empty `mathopt.CallbackResult()`.

The tests call your callback with hand-made `CallbackData` and also register it on a real SCIP
solve. About twelve lines.
