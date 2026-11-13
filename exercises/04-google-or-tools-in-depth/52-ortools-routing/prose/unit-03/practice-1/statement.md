A lift-maintenance company sends one engineer a day to several office buildings. Each building lets
the engineer in only during an access window, each visit takes some minutes of work, the engineer
may wait outside a building for up to `max_wait` minutes, and the shift ends at `shift_end` minutes
after the start. `windows.py` builds the route priced in travel minutes; write `add_time(routing,
manager, travel, service, windows, shift_end, max_wait)` so the model allows exactly the plans that
keep these rules. `windows[node] = (opens, closes)` is the arrival window of a building; the depot
has none, and the engineer may leave it whenever suits.

In the lesson's notation, with $`\text{time}_i`$ the arrival time at index $`i`$ and
$`\text{wait}_i`$ the waiting there:

```math
\begin{aligned}
& \text{time}_{\text{next}_i} = \text{time}_i + \text{service}_{\text{node}(i)} + \text{travel}_{\text{node}(i),\, \text{node}(\text{next}_i)} + \text{wait}_i && \forall i && \text{(Time)} \\
& 0 \le \text{wait}_i \le \text{max\_wait} && \forall i && \text{(waiting)} \\
& \text{opens}_a \le \text{time}_i \le \text{closes}_a && \forall i \text{ with node } a \text{ in windows} && \text{(window}_a) \\
& 0 \le \text{time}_i \le \text{shift\_end} && \forall i && \text{(shift)}
\end{aligned}
```

Before you code, name the argument of `AddDimension` that carries each of the waiting, shift and
"leave whenever suits" rules, and the index you must take a building's cumul at.

The tests ask the model whether hand-built plans are allowed, so any correct formulation passes.
About eight lines.
