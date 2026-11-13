A regional food bank moves pallets from its warehouses to its pantries, some directly and some
through sorting hubs. Each route is one-way, has a cost per pallet and a capacity. Warehouses may
keep pallets no pantry needs; a pantry must receive exactly its demand; a hub keeps nothing.

The network has nodes $`N`$ and arcs $`A`$ (pairs $`(i, j)`$). $`S \subseteq N`$ are the warehouses,
with supply $`a_n`$; $`D \subseteq N`$ the pantries, with demand $`d_n`$; every other node is a
hub. A node named in both `supply` and `demand` is treated as a warehouse: it gets only its
$`\text{supply}_n`$ row, and its demand entry is ignored. Arc $`(i, j)`$ costs $`c_{ij}`$ per pallet and carries at most $`u_{ij}`$. With
$`\text{in}_n = \sum_{(i,n) \in A} f_{in}`$ and $`\text{out}_n = \sum_{(n,j) \in A} f_{nj}`$:

```math
\begin{aligned}
\min \;& \sum_{(i,j) \in A} c_{ij}\, f_{ij} \\
\text{s.t. }& \text{out}_n - \text{in}_n \le a_n && \forall n \in S && \text{(supply}_n) \\
& \text{in}_n - \text{out}_n = d_n && \forall n \in D && \text{(demand}_n) \\
& \text{in}_n - \text{out}_n = 0 && \forall n \in N \setminus (S \cup D) && \text{(balance}_n) \\
& 0 \le f_{ij} \le u_{ij} && \forall (i,j) \in A
\end{aligned}
```

$`f_{ij}`$ is continuous: pallets moved on arc $`(i, j)`$. Write `ship(supply, demand, arcs)` in
`flow.py`. `supply` and `demand` map node names to pallets; `arcs` maps `(i, j)` to
`(cost, capacity)`; the nodes are every name that appears in them. It solves the model with GLOP
and returns `(status, cost, flows)`: the name of the termination reason; when it is `OPTIMAL`, the
cost and a dict from every arc to its flow (not rounded); otherwise `None, None`.

About eighteen lines.
