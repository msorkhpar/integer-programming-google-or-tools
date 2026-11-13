A food bank (not GridCap) leases vans for its weekend drive. Each van type $`t`$ carries
$`\text{cap}_t`$ pallets and costs $`c_t`$ dollars for the weekend. The dealer has $`a_t`$ vans of the
type, and leases them only in packs of $`k_t`$ (a pack of 2 means 0, 2, 4, ... vans). The drive
must move `demand` pallets, the board approved `budget` dollars, and every van needs one of the
`drivers` volunteers.

Write `build(types, demand, budget, drivers)` in `vans.py`. It returns a CP-SAT model and a dict
`n` of its variables, one per van type, keyed by the type's name. The model is:

```math
\begin{aligned}
\min \;& \sum_{t \in T} c_t\, n_t \\
\text{s.t. }& \sum_{t \in T} \text{cap}_t\, n_t \ge \text{demand} && \text{(cover)} \\
& \sum_{t \in T} c_t\, n_t \le \text{budget} && \text{(budget)} \\
& \sum_{t \in T} n_t \le \text{drivers} && \text{(drivers)} \\
& n_t \in \{0, k_t, 2k_t, \dots\},\ n_t \le a_t && \forall t \in T
\end{aligned}
```

The last line is each variable's domain, not a row: give every $`n_t`$ exactly the values a lease
allows when you create it.

The tests fix every $`n_t`$ to a value with an equality and ask CP-SAT whether the model still has a
solution, so they check which fleets your model allows and refuses. About eight lines.
