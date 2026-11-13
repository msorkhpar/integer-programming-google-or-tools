A regional cellular carrier is upgrading towers under a state broadband grant. The model in
`grant.py` has a binary `x[tid]` per candidate tower (1 if upgraded this cycle) and a binary
`y[oid]` per backhaul option, the link that carries a hub tower's traffic (fiber, radio or
satellite). The grant and the carrier's own limits set three rules:

- **Coverage.** Each county `c` in `need` must end the cycle with at least `need[c]` upgraded
  towers. Towers upgraded in earlier cycles count: `already[c]` of them exist (missing means 0).
- **Crews.** A county in `crew_limit` can take at most `crew_limit[c]` upgrades this cycle; a county
  not in it has no limit.
- **Backhaul.** `backhaul` maps each hub tower to its backhaul options. An upgraded hub gets exactly
  one of its options. A backhaul link is only built for a hub that is upgraded.

Write `add_grant_rules(model, x, y, towers, need, already, crew_limit, backhaul)` so that the model
allows exactly the plans that keep all three rules.

The model so far, with $`T`$ the candidate towers, $`H \subseteq T`$ the hubs and $`O_h`$ the
backhaul options of hub $`h`$:

```math
\begin{aligned}
& x_t \in \{0, 1\} && \forall t \in T && \text{(upgrade tower } t\text{)} \\
& y_o \in \{0, 1\} && \forall h \in H,\ o \in O_h && \text{(build backhaul option } o\text{)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the remaining sets and parameters (the counties, the towers of each county, the targets, the
towers already upgraded, the limits), write your rows first, each with its quantifier and a label,
and only then code them. Before you write a coverage row, ask what it should be for a county that
already meets its target. (The reference writes no coverage row for such a county: its row would ask
for 0 or fewer new upgrades, which every plan keeps, so skipping it allows the same plans.)

The tests fix every tower and every backhaul option through the variables' bounds and ask the
solver whether the model accepts the plan, so any correct formulation passes. About ten lines.
