A municipal electric utility buys the distribution transformers for this year's projects in a
single order from one supplier. Each candidate project needs `units` transformers (some need none).
The supplier's terms:

- An order is for at least `min_order` and at most `max_order` transformers. The utility may also
  place **no order at all**, but then it can fund no project that needs a transformer.
- An order carries a `delivery_fee` ($k), paid from the same budget as the projects. No order, no
  fee.

The model in `order.py` has a binary `x[pid]` per project (1 if funded) and nothing else. Write
`add_order_rules(model, x, projects, min_order, max_order, delivery_fee, budget)` so that the model
allows exactly the plans the supplier's terms and the budget allow, including the budget row. Add
whatever variables you need.

With $`P`$ the projects, $`u_p`$ the transformers project $`p`$ needs and $`c_p`$ its cost ($k),
the model so far is

```math
x_p \in \{0, 1\} \quad \forall p \in P \qquad \text{(fund project } p\text{)}
```

Write the rest first: each new variable with its domain, then each row with a label. Check your
rows against the cases that matter: no project funded, only projects needing no transformer, an
order just under the minimum, and one just over the maximum.

The tests fix which projects are funded and ask the solver whether the model accepts the plan, so any
correct formulation passes. About six lines.
