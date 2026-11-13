During a storm, a utility places mobile generators at critical sites (a hospital feeder, a water
plant, a shelter). The fleet has `fleet` generator-hours in all. Site $`s`$ is worth a value per
generator-hour and can use at most a number of hours (its demand). A site gets generator-hours
**only if** a hookup is built there first, which costs a fixed fee. The planners maximize value
less fees.

`build(sites, fleet, big_m, integer)` in `generators.py` already creates the hours $`g_s \ge 0`$, the
hookup binaries $`h_s`$, the demand and fleet rows and the objective. Write three things:

- the hookup row in `build`, one per site, switched by $`h_s`$, using `big_m[s]`;
- `tight_m(sites, fleet)`: each site's smallest valid $`M`$, from the rows the model already has (no
  solve);
- `bounds(sites, fleet)`: the LP relaxation's value with $`M = 10^6`$ for every site (`"loose"`),
  the LP relaxation's value with `tight_m` (`"tight"`), and the MILP optimum with `tight_m`
  (`"milp"`). Use GLOP for the LPs and HiGHS for the MILP.

The model, with $`v_s`$ the value per hour, $`D_s`$ the demand, $`f_s`$ the fee and $`H`$ the fleet:

```math
\begin{aligned}
\max \;& \textstyle\sum_s v_s\, g_s - \sum_s f_s\, h_s \\
& g_s \ge 0, \quad h_s \in \{0, 1\} && \forall s \\
& g_s \le D_s && \forall s \quad \text{(demand}_s) \\
& \textstyle\sum_s g_s \le H && \text{(fleet)} \\
& \text{?} && \forall s \quad \text{(hookup}_s)
\end{aligned}
```

Write the hookup row and the formula for $`M_s`$ in this notation first. Before running anything,
predict which of the two LP values is higher, and why.

The tests fix a plan by its variables' bounds and ask the solver whether it is allowed, so any
correct row passes; two more tests check `tight_m`'s values and the three numbers `bounds` returns.
About ten lines.
