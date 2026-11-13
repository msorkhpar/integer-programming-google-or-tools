A brewery delivers to pubs with two trucks. Each pub takes some kegs and some kilograms of bottled
stock, and each truck has two limits: how many kegs fit on it and how much weight it may carry. The
second truck is smaller. `loads.py` builds the routes; write `add_loads(routing, manager, demands,
capacities)`, where `demands[kind][node]` is what a stop takes of one kind and
`capacities[kind][v]` is the most truck `v` may carry of it. Make one dimension per kind, named
after the kind, so a planner can look each one up by name.

In the lesson's notation, for every kind $`q`$, with $`d^q_a`$ the demand of node $`a`$ and
$`K^q_v`$ truck $`v`$'s capacity:

```math
\begin{aligned}
& \text{load}^q_{s_v} = 0 && \forall q,\ v && \text{(leave the depot empty)} \\
& \text{load}^q_{\text{next}_i} = \text{load}^q_i + d^q_{\text{node}(i)} && \forall q,\ i && \text{(pick up at each stop)} \\
& \text{load}^q_i \le K^q_v && \forall q,\ i \text{ on truck } v\text{'s route} && \text{(capacity}^q_v)
\end{aligned}
```

Before you code, say why the demand callback takes one index and not two. Then mind two Python
traps when you register callbacks in a loop: what a dimension name that is already taken does
(the lesson says), and which `demand` list a function defined inside the loop reads when the
solver calls it later.

The tests ask the model whether hand-built routes are allowed, so any correct formulation passes.
About six lines.
