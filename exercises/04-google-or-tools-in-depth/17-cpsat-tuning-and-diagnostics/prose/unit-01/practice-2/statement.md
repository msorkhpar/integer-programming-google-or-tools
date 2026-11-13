The same inspection week as before. `improve(jobs, hours, plan, free)` is now given: one LNS step
that frees the jobs in `free`, keeps every other job as `plan` has it, and returns the best plan
it finds. The planner wants a loop around it.

Write `lns(jobs, hours, start, rounds)`. `rounds` is a list of neighborhoods (sets of job names),
used in order, one step each. Return a pair: the final plan (a set of job names) and a list of
plan values, the start plan's value first and then the value after each round. A round whose step
finds nothing better leaves the plan as it was: replace the current plan only when the step's plan
is worth strictly more, so a plan of equal value never replaces it (the reference compares with
`>`). Compute values as whole numbers, by summing the picked jobs' values, not from the float
`objective_value`.

Each step solves the model of the previous practice with the rows that keep the jobs outside the
neighborhood as they are:

```math
\begin{aligned}
\max \;& \sum_{j \in J} v_j\, \text{pick}_j \quad \text{s.t.} \quad \sum_{j \in J} h_j\, \text{pick}_j \le \text{hours},\\
& \text{pick}_j = [\, j \in \text{current} \,] && \forall j \in J \setminus \text{free}
\end{aligned}
```

Think about which plan "current" is in the second round. About eight lines.
