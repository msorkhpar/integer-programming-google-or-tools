A bus depot sends each bus through some of its bays (wash, service, inspection) in an order that
depends on the bus. A bay handles one bus at a time, a bus is in one bay at a time, and a step,
once started, runs to its end. Hours are numbered from 0.

Write `plan_depot(buses)` in `depot.py`. `buses` maps a bus to its steps in order, each a pair
`(bay, hours)`. Return the start hour of every step as a dict keyed `(bus, k)`, where `k` is the
step's position (0 for the first), chosen so that the last bus leaves as early as possible.

This is the job shop. With $`J`$ the buses, step $`k`$ of bus $`b`$ on bay $`m_{b,k}`$ for
$`d_{b,k}`$ hours, $`K_b`$ the number of steps of bus $`b`$, $`M`$ the bays, and the horizon
$`H = \sum_{b,k} d_{b,k}`$ (every step one after another):

```math
\begin{aligned}
& s_{b,k} \in \{0, \dots, H\} && \forall b \in J,\ k < K_b && \text{(start hour)} \\
& C \in \{0, \dots, H\} && && \text{(the hour the last bus leaves)} \\
& \min \; C \\
& \text{NoOverlap}\big(\{[s_{b,k}, s_{b,k} + d_{b,k}) : m_{b,k} = m\}\big) && \forall m \in M && \text{(bay}_m) \\
& s_{b,k+1} \ge s_{b,k} + d_{b,k} && \forall b \in J,\ k < K_b - 1 && \text{(order}_{b,k}) \\
& C = \max_{b \in J} \big(s_{b,K_b-1} + d_{b,K_b-1}\big) && && \text{(makespan)}
\end{aligned}
```

Group the intervals by bay before you add the NoOverlap rows. The tests check the plan you return
and how early the depot clears, so any optimal plan passes. About twenty lines.
