A home-care agency sends its nurses from one office to patients' homes. The labor agreement caps
how long each nurse may spend driving in a day, the drive back to the office included, and the
part-time nurses have a lower cap than the full-time ones. `shifts.py` builds one route per nurse,
priced in drive minutes; `shifts[v]` is nurse `v`'s cap. Write `add_drive_limits(routing,
drive_index, shifts)` so the model refuses any route that drives longer than its nurse's cap.

In the lesson's notation, with $`\text{drive}_i`$ the minutes driven on arrival at index $`i`$,
$`s_v`$ and $`e_v`$ nurse $`v`$'s start and end, and $`c`$ the drive callback:

```math
\begin{aligned}
& \text{drive}_{s_v} = 0 && \forall v && \text{(start at zero)} \\
& \text{drive}_{\text{next}_i} = \text{drive}_i + c_{\text{node}(i),\, \text{node}(\text{next}_i)} && \forall i && \text{(accumulate)} \\
& \text{drive}_i \le \text{shift}_v && \forall i \text{ on nurse } v\text{'s route} && \text{(cap}_v)
\end{aligned}
```

Before you code, say what slack this dimension needs, and which dimension call takes one cap per
vehicle.

The tests ask the model whether hand-built routes are allowed (`ReadAssignmentFromRoutes`), so any
correct dimension passes. One line.
