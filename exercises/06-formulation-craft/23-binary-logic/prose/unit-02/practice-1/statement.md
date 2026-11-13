A regional water utility is choosing next year's capital projects. Its engineers have handed the
planners four kinds of rule, each given to you as data:

- **Supports** (`needs_any`, a dict from a project to a list of projects). A project may be funded
  only if at least one of its supports is funded too. The treatment-plant expansion, for example,
  needs either the north main or the south main to carry its output.
- **Group triggers** (`all_trigger`, a list of `(group, consequence)`). If *every* project in the
  group is funded, the consequence must be funded as well; if only some of them are, the rule asks
  nothing. A group may hold any number of projects.
- **Incompatible pairs** (`never_with`, a list of `(a, b)`). The two projects may not both be funded.
- **Pairs** (`together`, a list of `(a, b)`). Both are funded, or neither is.

The model in `water_rules.py` already has a binary `x[pid]` per project (1 if funded) and a budget
row. Write `add_engineering_rules(model, x, needs_any, all_trigger, never_with, together)` so that
the model allows exactly the plans that keep every rule.

With $`P`$ the projects, the model so far is

```math
\begin{aligned}
& x_p \in \{0, 1\} && \forall p \in P && \text{(fund project } p\text{)} \\
& \sum_{p \in P} c_p\, x_p \le B && && \text{(budget, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the sets each kind of rule needs (the supports $`S_p`$ of a project, the projects $`G`$ of a
group and its consequence $`k_G`$, the pairs), write one family of rows per kind with its quantifier
and a label, and check each row against the rule on the 0/1 combinations before you code it. Mind
the group trigger: your row must work for a group of any size.

The tests fix a plan through the variables' bounds and ask the solver whether the model accepts it,
so any correct formulation passes. About ten lines.
