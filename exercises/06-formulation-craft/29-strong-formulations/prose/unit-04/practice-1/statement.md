A transmission operator (not GridCap) keeps spare parts in depots. Each substation draws $`d_i`$
parts a year and is served by exactly one open depot; depot $`j`$ holds at most $`U_j`$ parts and
costs $`\phi_j`$ a year to keep open; serving substation $`i`$ from depot $`j`$ costs $`h_{i,j}`$ a
year in hauling. `build` in `depots.py` has the variables ($`x_{i,j} \in \{0,1\}`$: $`i`$ is served
by $`j`$; $`y_j \in \{0,1\}`$: $`j`$ is open), the "served once" rows and the objective

```math
\min \; \sum_j \phi_j\, y_j + \sum_{i,j} h_{i,j}\, x_{i,j}
```

The model you inherit (`add_inherited_rules`) states the rules "only an open depot serves" and "a
depot holds at most its capacity" as

```math
\sum_i x_{i,j} \le |I|\, y_j \quad \text{(open}_j), \qquad \sum_i d_i\, x_{i,j} \le U_j \quad \text{(cap}_j)
```

It allows exactly the right plans, and its LP bound is $42.13k against a best plan of $77k.

Audit it as the lesson did: solve its LP relaxation and look at the $`y_j`$. Then write
`add_rules(model, x, y, d)` with the same two rules in their strongest form. Write your rows with
labels and quantifiers first, and for each one show on paper (a) that with whole numbers it allows
the same plans as the colleague's, and (b) which fractional point of the colleague's LP it refuses.

The tests fix whole plans and ask whether each is allowed, and compare your LP bound with what the
strongest rows give. Since this model minimizes, a higher LP bound is a tighter one. About six lines.
