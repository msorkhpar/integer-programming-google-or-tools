A transmission operator (not GridCap) funds upgrade jobs under one budget. Each substation has a
list of jobs, and the regulator pays a **commissioning bonus** for a substation only when every one
of its jobs is funded, so that the substation can be put back in service fully upgraded. A job
belongs to one substation.

`build` in `bonus.py` already has the variables, the budget row and the objective:
$`x_j \in \{0, 1\}`$ (fund job $`j`$), $`z_s \in \{0, 1\}`$ (substation $`s`$ is commissioned and earns
its bonus $`R_s`$), and

```math
\max \; \sum_j v_j\, x_j + \sum_s R_s\, z_s \qquad \text{s.t.} \quad \sum_j c_j\, x_j \le B
```

A colleague wrote the rule as one row per substation, $`|J_s|\, z_s \le \sum_{j \in J_s} x_j`$
(`add_colleague_rows`, given). It allows exactly the right plans, but its LP relaxation lets a
substation count as two-thirds commissioned when two of its three jobs are funded, and collect
two-thirds of the bonus.

Write `add_commissioning(model, x, z, jobs_of)`: the same rule in the strongest form you can find.
Before coding, write your rows with their labels and quantifiers, check on paper that with whole
numbers they allow exactly the plans the colleague's row allows, and show that the colleague's row
is a sum of yours, so your relaxation's region lies inside the colleague's.

The tests fix whole plans and ask the solver whether each is allowed, so any correct formulation
passes them; one more test checks that your LP bound on a budget of 9 is no looser than the best
rows give. About three lines.
