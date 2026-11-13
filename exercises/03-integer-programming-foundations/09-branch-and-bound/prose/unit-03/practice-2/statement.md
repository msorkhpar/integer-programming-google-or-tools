The crew-rostering search branches on the first fractional variable it sees, and the team wants to
try the most-fractional rule instead.

Write `most_fractional(x, tol=1e-6)` in `most_fractional.py`. `x` maps each integer variable's name
to its LP value; values may be above 1 (counts of crews). A variable is a candidate when its value is
more than `tol` from the nearest whole number. Among the candidates, return the name with the largest

```math
\phi(x_j) = \min\big(x_j - \lfloor x_j \rfloor,\ \lceil x_j \rceil - x_j\big)
```

the distance from $`x_j`$ to the nearer whole number. Ties go to the variable listed first in `x`.
Return `None` when there is no candidate.
