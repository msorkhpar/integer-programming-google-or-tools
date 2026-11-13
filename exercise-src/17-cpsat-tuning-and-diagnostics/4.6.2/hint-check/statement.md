A rural cooperative replaces poles in batches. This year's rules are in `build(costs, values, must,
budget)` in `carryover.py`: fund batches within the budget, fund every must-do batch, and maximize
value. Before re-planning, the planners ask a simple question: does last year's plan (a set of batch
names) still keep this year's rules?

Write two functions:

- `add_plan_hint(model, pick, plan)`: hint the plan to the model, one hint per batch.
- `fits(costs, values, must, budget, plan)`: build the model, hint the plan, have CP-SAT fix every
  variable to its hint, solve with one worker, and return whether a solution exists.

The model, with $`P`$ the batches, $`c_p`$ their costs, $`v_p`$ their values and $`M`$ the must-dos:

```math
\begin{aligned}
\max \;& \sum_{p \in P} v_p\, \text{pick}_p \\
\text{s.t. } & \sum_{p \in P} c_p\, \text{pick}_p \le \text{budget} && \text{(budget)} \\
& \text{pick}_p = 1 && \forall p \in M && \text{(must}_p) \\
& \text{pick}_p \in \{0, 1\} && \forall p \in P
\end{aligned}
```

The hint is $`\bar x_p = 1`$ if $`p`$ is in the plan, for every $`p \in P`$. Think about what the
solver may do with a variable that has no hint at all. About ten lines.
