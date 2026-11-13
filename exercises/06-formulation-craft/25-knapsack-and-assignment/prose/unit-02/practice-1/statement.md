A utility's central warehouse (not GridCap) is loading tomorrow's trucks to the field depots. Each
material order $`o`$ has a priority $`v_o`$, a weight $`w_o`$ (kg) and a volume $`u_o`$ (m³). Each
truck $`t`$ can carry at most $`W_t`$ kg and $`U_t`$ m³. The dispatcher's rules:

- An order travels on **one truck at most**; an order left off every truck waits for the next day.
- Every truck must stay within **both** its weight and its volume limit.
- Orders for the same **job site** (the same `site` value, when it is not `None`) are unloaded by one
  crew, so they travel **on the same truck, or all wait**.

The model in `loading.py` has a binary `x[oid, tid]` for every order and truck (1 if the order
travels on that truck) and maximizes the priority shipped. Write
`add_loading_rules(model, x, orders, trucks)` so that the model allows exactly the loadings the
dispatcher's rules allow.

With $`O`$ the orders and $`T`$ the trucks, the model so far is

```math
x_{o,t} \in \{0, 1\} \quad \forall o \in O,\ t \in T \qquad \text{(order } o \text{ travels on truck } t\text{)}
```

Write your rows first, each with its quantifier and a label; name the sets you need for the job
sites. Then code them.

The tests fix which order rides on which truck and ask the solver whether the rules allow it, so any
correct formulation passes. About twelve lines.
