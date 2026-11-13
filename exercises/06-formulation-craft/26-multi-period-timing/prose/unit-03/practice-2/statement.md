An electric cooperative is rebuilding a substation (project `SUB`). Four feeder upgrades (`F1` to
`F4`) hang off it: each one is only worth doing if the substation is rebuilt, but the substation
may be rebuilt with any number of its feeders, none included. This is a one-period selection: each
project is funded or not.

A colleague wrote the rule in `add_aggregated_needs` as one row for all the children together. It
allows exactly the right whole-number plans, but the LP bound of the planning model is loose.

Write `add_parent_rows(model, x, parent, children)` in `feeders.py`: the same rule, written so that
the LP relaxation cannot fund a valuable feeder on a small fraction of the substation. `x[pid]` is
each project's variable.

The model so far, with $`p`$ the parent, $`C`$ its children and the colleague's row shown for
comparison:

```math
\begin{aligned}
& 0 \le x_i \le 1, \ x_i \text{ integer in the plan, continuous in the LP} && \forall i \in \{p\} \cup C \\
& \textstyle\sum_{c \in C} x_c \le |C|\, x_p && \text{(the colleague's row)} \\
& \text{?} && \text{(your rows)}
\end{aligned}
```

Write your rows in this notation first, each with its quantifier and a label, then code them. Check
them against a plan with only the substation, and against a plan with two feeders.

The tests fix a plan by its variables' bounds and ask the solver whether it is allowed, so any
correct set of rows passes; one more test checks that on a small LP your rows give a smaller LP value (a tighter bound: for a maximization the
LP value bounds every plan from above) than the colleague's. About three lines.
