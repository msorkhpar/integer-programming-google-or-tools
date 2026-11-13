A feeder that keeps tripping is upgraded in exactly one of two ways. A **line crew** reconductors the
worst spans: it spends between 10 and 30 ($k), and the capacity it adds is at most half of what it
spends. A **rebuild** replaces the feeder: it spends between 60 and 100, and adds at most 40 of
capacity, whatever it spends.

`mode_variables` (given) creates the spend $`s \in [10, 100]`$, the capacity gain $`g \in [0, 40]`$
and the binary $`r`$ (1 = rebuild, 0 = line crew). Write `add_bigm_modes(model, s, g, r)` in
`upgrade.py`: the disjunction as big-M rows, each with the smallest $`M`$ the variables' bounds
justify, computed in code from `s.lower_bound`, `g.upper_bound` and the module's constants.

"From the bounds" means from $`10 \le s \le 100`$ and $`0 \le g \le 40`$ alone, as in the
variable-bounds rule of lesson 6.2.1, and not from the other rows of the disjunct. For the line
crew's gain row, the reference takes the largest value $`g - 0.5\,s`$ can reach over those bounds,
$`40 - 0.5 \cdot 10 = 35`$. It does not use the rebuild's own floor $`s \ge 60`$, which would bring
that $`M`$ down to 10; that smaller value is also valid, and the tests accept it, but it is a step
beyond the bounds.

The model so far:

```math
\begin{aligned}
& 10 \le s \le 100, \quad 0 \le g \le 40, \quad r \in \{0, 1\} && \\
& \big[\, 10 \le s \le 30,\ g \le 0.5\, s \,\big] \;\vee\; \big[\, 60 \le s \le 100,\ g \le 40 \,\big] && \text{(mode)}
\end{aligned}
```

Some rows of each disjunct are already implied by the variables' bounds, and need no row of their
own. Decide which, write the remaining rows with their $`M`$s in this notation first, then code
them.

The tests fix a plan by its variables' bounds and ask the solver whether it is allowed, so any
correct set of rows passes; one more test checks that the LP relaxation of your rows is at least as
tight as rows with $`M`$s from the bounds. About six lines.
