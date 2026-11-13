A regional water board picks this year's capital projects. Each project is `"maintenance"` (renewing
pipes and pumps that exist) or `"growth"` (new capacity), with a cost in $k. The model in `board.py`
has a binary `x[pid]` per project. The board's rules:

- **Budget.** The plan spends at most `budget`.
- **Use it.** The plan spends at least the share `use` of the budget: a plan that leaves too much
  unspent will cost the board its funding next year.
- **Maintenance band.** Maintenance makes up between the share `low` and the share `high` of what
  the plan actually spends.

Write `add_spend_rules(model, x, projects, budget, use, low, high)` so that the model allows exactly
the plans that keep the three rules.

The model so far, with $`P`$ the projects:

```math
\begin{aligned}
& x_i \in \{0, 1\} && \forall i \in P && \text{(project } i \text{ is funded)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the parameters and write the plan's spend and its maintenance spend as expressions first. The
band is a ratio of two of your expressions; write each of its two rows so that it is linear, with
its label, before you code it.

The tests fix every `x[pid]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About eight lines.
