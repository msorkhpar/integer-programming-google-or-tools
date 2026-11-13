A substation has a 10-hour outage window, and the maintenance jobs that could run in it take
$`a_j`$ hours each. A planning MILP chooses jobs with binaries $`y_j \in \{0, 1\}`$ under the row

```math
\sum_{j \in J} a_j\, y_j \le W \qquad \text{(window)}
```

Its LP relaxation returned a point $`y^*`$ with some jobs fractional. Write the separation step that
turns that point into a cover cut.

Write `find_cover(hours, window, y)` in `cover.py`. `hours` maps each job to $`a_j > 0`$, `window`
is $`W`$, and `y` maps each job to $`y^*_j \in [0, 1]`$. Return a list of jobs $`C`$ such that

```math
\sum_{j \in C} a_j > W, \qquad
\sum_{j \in C} a_j - a_k \le W \;\; \forall k \in C, \qquad
\sum_{j \in C} \left(1 - y^*_j\right) < 1
```

that is, a minimal cover whose inequality $`\sum_{j \in C} y_j \le |C| - 1`$ the point breaks. Return
`None` when your search finds no such set. The tests accept any set with these three properties; the
lesson's greedy rule finds one on every test where one exists.

Use a tolerance of $`10^{-9}`$ when you compare the violation with zero.
