A depot-planning MILP decides how many trucks to station at each depot (a whole number, often more
than 1) and whether to open each depot (0 or 1). Its LP relaxation has just come back from the
solver, and the branch-and-bound loop needs to know which variables are still fractions.

Write `fractional(x, tol=1e-6)` in `fractional.py`. `x` maps each variable's name to its LP value.
Return the names of the variables whose value is more than `tol` away from the nearest whole number:

```math
\text{fractional}(x) = \{\, j : |x_j - \operatorname{round}(x_j)| > \text{tol} \,\}
```

in the order `x` lists them. A value such as 0.9999999 is a whole number that picked up float
error, so it is not fractional. Values can be above 1 (truck counts) or below 0 (a change in a
count).
