The pump-scheduling simplex now knows where to pivot. It needs the step itself: rewrite the
tableau so the entering variable becomes basic in the leaving row, which moves the plan to a
neighbouring vertex.

Write `pivot(T, r, k)` in `pivot.py`. `T` is a tableau (constraint rows, then the objective row;
every row ends with its right-hand side), `r` the pivot row and `k` the pivot column, with
$`T_{r,k} \neq 0`$. Return a new tableau $`T'`$ with

```math
T'_{r,j} = \frac{T_{r,j}}{T_{r,k}} \quad \forall j, \qquad
T'_{i,j} = T_{i,j} - T_{i,k}\, T'_{r,j} \quad \forall i \neq r,\ \forall j
```

where $`i`$ runs over every row, the objective row included, and $`j`$ over every column, the
right-hand side included. After it, column $`k`$ is 1 in row $`r`$ and 0 in every other row.

Leave `T` unchanged: the caller keeps the old tableau to print it next to the new one.
