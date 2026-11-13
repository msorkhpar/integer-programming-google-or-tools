A grocery delivers online orders with two vans that carry 8 crates each, and today's orders add up
to more than both vans hold. Prepaid orders must go out today; the others may wait until tomorrow,
at a cost the shop sets per order (a discount voucher, a lost customer). `optional.py` builds the
routes and the van capacity. Write two functions:

- `make_optional(routing, manager, penalties)`: each node in `penalties` may be skipped at
  `penalties[node]`; every other order stays required.
- `skipped(routing, manager, solution)`: the nodes on no route, in increasing order, so the shop
  can send the vouchers.

In the lesson's notation, with $`O`$ the optional orders, $`\pi_a`$ their penalties and
$`\text{active}_i = 1`$ when a route visits index $`i`$:

```math
\begin{aligned}
\min \; & \sum_{\text{arcs driven}} \text{distance} \; + \; \sum_{a \in O} \pi_a \,(1 - \text{active}_{\text{index}(a)}) \\
\text{s.t.} \; & \text{active}_{\text{index}(a)} = 1 \quad \forall a \notin O \qquad \text{(required)} \\
& \text{next}_i = i \iff \text{active}_i = 0 \qquad \text{(a skipped order points to itself)}
\end{aligned}
```

Before you code, say which call makes one order optional, what it takes (a node or an index), and
which indices `skipped` must leave out of its test.

The tests price hand-built plans and read a solve, so any correct formulation passes. About six
lines.
