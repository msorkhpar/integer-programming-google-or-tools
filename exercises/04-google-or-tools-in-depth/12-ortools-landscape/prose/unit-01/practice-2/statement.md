A water utility (not GridCap) sends its repair crews to depots each morning, one crew per depot, and
wants the least total travel. Some crews are not cleared for some depots. The data is a matrix
`hours[k][d]`: whole travel hours for crew `k` to reach depot `d`, or `None` where crew `k` is not
cleared for depot `d`. There are as many crews as depots.

Write `pair(hours)` in `pairing.py` with OR-Tools' assignment solver,
`linear_sum_assignment.SimpleLinearSumAssignment`. It returns `(total_hours, depot_of)`, where
`depot_of[k]` is the depot crew `k` goes to, or `None` when no pairing gives every crew a depot it is
cleared for. The problem it solves:

**Sets.** $`K`$, the crews; $`D`$, the depots ($`|K| = |D|`$); $`A \subseteq K \times D`$, the
cleared pairs (the entries that are not `None`).

**Parameters.** $`h_{k,d}`$, the hours for each $`(k, d) \in A`$.

**Variables.** $`y_{k,d} \in \{0, 1\}`$ for every $`(k, d) \in A`$.

```math
\begin{aligned}
\min \;& \sum_{(k,d) \in A} h_{k,d}\, y_{k,d} \\
\text{s.t. } & \sum_{d : (k,d) \in A} y_{k,d} = 1 && \forall k \in K && \text{(one\_depot}_k) \\
& \sum_{k : (k,d) \in A} y_{k,d} = 1 && \forall d \in D && \text{(one\_crew}_d)
\end{aligned}
```

You do not write this model: the assignment solver takes it as arcs. Give it one arc per cleared pair
(`add_arc_with_cost`), call `solve()`, and read `optimal_cost()` and `right_mate(k)`. Check what
`solve()` returns before you read anything: it is a status, one of
`OPTIMAL`, `INFEASIBLE` and `POSSIBLE_OVERFLOW`, and you compare it with the solver's own
`solver.OPTIMAL`. About ten lines.
