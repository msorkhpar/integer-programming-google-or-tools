A transit agency runs its bus-replacement scheduler as a service. Every night it solves a MathOpt
model and must decide, from the `SolveResult` alone, what to do next. The agency's rules:

| The solve ended | The service |
| --- | --- |
| with a proven optimal plan | `"publish"` |
| with a plan stopped by a limit, whose relative gap is at most `max_gap` | `"publish"` |
| with a plan stopped by a limit, whose gap is larger | `"rerun"` (with more time) |
| with no plan because a limit stopped the search | `"rerun"` |
| with a proof that no plan exists | `"conflict"` (send it to the conflict finder) |
| with a proof that plans improve without end | `"model-bug"` |
| unable to tell infeasible from unbounded | `"separate"` (the zero-objective solve) |
| any other way | `"escalate"` |

Write `next_step(result, max_gap)`. The reason is `result.termination.reason`, a
`mathopt.TerminationReason`, and it alone tells the cases apart: "a plan stopped by a limit" is
`TerminationReason.FEASIBLE`, "no plan because a limit stopped the search" is `NO_SOLUTION_FOUND`.
The tests' results carry no solutions, so don't ask `result.has_primal_feasible_solution()` as the
lesson's `verdict` does; that check reads a real solve's plans, which these results don't have. For a plan stopped by a limit, the bounds are in
`result.termination.objective_bounds` (`primal_bound`, the plan's objective, and `dual_bound`,
the best bound). The relative gap is the distance between the two divided by the size of
`primal_bound`. When `primal_bound` is 0, publish only if the two bounds are equal. The agency's
models both maximize ridership and minimize cost, so the bound can lie on either side of the plan.

The tests build results directly with `mathopt.SolveResult(termination=mathopt.Termination(...))`,
so no solver runs. About twenty lines.
