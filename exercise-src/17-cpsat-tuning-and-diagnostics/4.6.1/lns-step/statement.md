A utility's inspection planner picks which substation inspections the crews run this week. Each
job has a district, a value (risk points removed) and the crew-hours it takes; the crews have
`hours` in total. `build(jobs, hours)` in `inspections.py` already makes the whole week's CP-SAT
model, with one Boolean `pick[name]` per job.

The planner has a plan and wants to improve it one district at a time: free the jobs of one
district, keep every other job exactly as the plan has it, and let CP-SAT re-plan the freed part.

Write `improve(jobs, hours, plan, free)`. `plan` and `free` are sets of job names. Return the set of
job names in the best plan that agrees with `plan` on every job not in `free`.

The model `build` makes, with $`J`$ the jobs, $`v_j`$ their values and $`h_j`$ their hours:

```math
\begin{aligned}
\max \;& \sum_{j \in J} v_j\, \text{pick}_j \\
\text{s.t. } & \sum_{j \in J} h_j\, \text{pick}_j \le \text{hours} && \text{(hours)} \\
& \text{pick}_j \in \{0, 1\} && \forall j \in J
\end{aligned}
```

Write the rows your step adds in this notation first, with their quantifier: one for the jobs the
plan runs and one for the jobs it leaves out, each only outside the neighborhood. Then code them,
hint the current plan, and solve with one worker. About eight lines.
