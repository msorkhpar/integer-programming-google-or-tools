A water utility is lining a failing trunk main. First a temporary bypass pipe goes in (project
`BY`), then the permanent replacement (project `RP`). The utility's rule: the replacement starts
in the same year as the bypass or at most `within` years later, because the bypass is only rated
for that long. A bypass is never laid without its replacement, and a replacement is never started
without its bypass.

A colleague wrote the rule in `add_aggregated_deadline` as rows on the two projects' weighted
start-year sums. It refuses exactly the right whole-number schedules, but the LP bound of the
planning model is loose and its solves are slow.

Write `add_deadline_rows(model, x, bypass, replacement, within)` in `deadline.py`: the same rule,
written so that it checks the schedule year by year. Nothing in the lesson writes this rule; derive
it from the lesson's idea of running totals ("started by year $`t`$").

The model so far, with $`T_{BY}`$ and $`T_{RP}`$ the years each project may start in, $`Y`$ their
union, and $`W`$ the value of `within`:

```math
\begin{aligned}
& 0 \le x_{i,t} \le 1, \ x_{i,t} \text{ integer in the plan, continuous in the LP} && \forall i \in \{BY, RP\},\ t \in T_i \\
& \textstyle\sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in \{BY, RP\} \quad \text{(once}_i) \\
& \text{?} && \text{(your rows)}
\end{aligned}
```

Write your rows in this notation first, each with its quantifier and a label, then code them. Check
them against a bypass started in the last year of its window.

The tests fix a schedule by its variables' bounds and ask the solver whether it is allowed, so any
correct set of rows passes; one more test checks that on a small LP your rows give a smaller LP value (a tighter bound: for a maximization the
LP value bounds every plan from above) than the colleague's. About ten lines in total.
