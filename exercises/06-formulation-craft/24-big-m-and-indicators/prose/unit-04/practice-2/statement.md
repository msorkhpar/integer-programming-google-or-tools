The same feeder as before is upgraded in exactly one of two ways. A **line crew** spends between 10
and 30 ($k) and adds at most half of what it spends in capacity. A **rebuild** spends between 60 and
100 and adds at most 40.

A colleague wrote the choice as big-M rows (`add_bigm_modes`, given): every row of both modes,
each switched off by $`M = 100`$. The rows are correct, but the planning model's LP bound is loose:
on the objective "3 times the gain, less the spend", its LP relaxation promises 110 where the best
plan is worth 60.

Write `add_hull_modes(model, s, g, r)` in `upgrade.py`: the same disjunction in hull form. The lesson
built a hull for two jobs that must not overlap; here each disjunct has its own spend range and its
own rule for the gain, so decide which variables need a copy per mode and which constants must be
scaled by the mode's switch.

The model so far, with $`r = 1`$ for a rebuild:

```math
\begin{aligned}
& 10 \le s \le 100, \quad 0 \le g \le 40, \quad r \in \{0, 1\} && \\
& \big[\, 10 \le s \le 30,\ g \le 0.5\, s \,\big] \;\vee\; \big[\, 60 \le s \le 100,\ g \le 40 \,\big] && \text{(mode)}
\end{aligned}
```

Write your copies and rows in this notation first, then code them. Check by hand that with
$`r = 1`$ every line-crew copy is forced to 0.

The tests fix a plan by its variables' bounds and ask the solver whether it is allowed, so any
correct hull passes; one more test checks that your LP bound is the best plan's value, 60, and below
the colleague's. About ten lines.
