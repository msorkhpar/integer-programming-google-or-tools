A pipeline operator (not GridCap) chooses which lines to inspect this year. Line $`i`$ is $`k_i`$ km
long (a whole number), $`x_i \in \{0, 1\}`$ says whether it is inspected, and the regulator's rule is
a **floor**, a knapsack row turned around:

```math
\sum_{i \in I} k_i\, x_i \ge F \qquad \text{(floor)}
```

The LP relaxation meets the floor with fractions of lines, so the planners want valid rows that cut
such points off, built from the same idea as a cover. Call a set $`C`$ of lines **needed** when the
lines *outside* it add up to less than the floor. Then every whole plan that meets the floor
inspects at least one line of $`C`$, so the row

```math
\sum_{i \in C} x_i \ge 1 \qquad \text{(needed}_C)
```

is valid. Write `separate_floor(km, floor, xstar)` in `inspection.py`. Given an LP point
`xstar` (line -> value between 0 and 1), it returns a needed set whose row the point breaks, as a list
of line names, choosing the one the point breaks the most; or `None` when no needed set's row is
broken.

Before coding, write the separation problem the way the lesson wrote the cover one: a binary per
line for "is in $`C`$", the row that says $`C`$ is needed (the lengths are whole kilometres), and the
objective. You may solve it with MathOpt and HiGHS, which the workspace has.

The tests check by trying every whole plan that a returned set is really needed, and that the LP
point really breaks its row. About ten lines.
