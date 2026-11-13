A one-driver courier service plans tomorrow's delivery runs. Each run can be made with any vehicle
in its list, and each vehicle gives the run a length in hours and a cost in dollars: a cargo bike
is slow and cheap, a van is quicker and dearer. The driver makes one run at a time, and every run
must end by the `deadline` hour. Hours are numbered from 0.

Write `cheapest_runs(runs, deadline)` in `courier.py`. `runs` maps a run to `(hours, costs)`, two
lists of the same length, one entry per vehicle. Return `(total_cost, plan)`, where `plan` maps
each run to `(vehicle, start)`: the vehicle's index in the run's lists and the run's start hour,
chosen so that the total cost is as small as possible. Every instance in the tests has a plan.
`total_cost` is an `int`: `solver.objective_value` is a float, so convert it with `round(...)`, as
the reference does, never with `int(...)`, which turns a value such as 49.99999999999999 into 49.

The model, with $`R`$ the runs, $`h_{r,v}`$ and $`c_{r,v}`$ the hours and cost of run $`r`$ by
vehicle $`v`$, $`V_r`$ the vehicle indices of run $`r`$, and $`D`$ the deadline:

```math
\begin{aligned}
& v_r \in V_r,\quad \ell_r \in \{\min_v h_{r,v}, \dots, \max_v h_{r,v}\},\quad s_r, e_r \in \{0, \dots, D\} && \forall r \in R \\
& \min \; \textstyle\sum_{r \in R} c_{r, v_r} \\
& \ell_r = h_{r, v_r} && \forall r \in R && \text{(length, element)} \\
& e_r = s_r + \ell_r && \forall r \in R && \text{(the run's interval)} \\
& \text{NoOverlap}\big(\{[s_r, e_r) : r \in R\}\big) && && \text{(one driver)}
\end{aligned}
```

The cost $`c_{r, v_r}`$ is a second element (or a Boolean per vehicle with weighted sums). Remember
that an interval's size must be a single variable, not a sum. The tests check the plan you return and
its cost, so any optimal plan passes. About twenty lines.
