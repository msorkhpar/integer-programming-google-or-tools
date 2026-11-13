A software team (not GridCap) picks which features ship in the next release. The product owner's
rules come in four kinds, each a list of tuples of feature names:

- `requires`: `(a, b)`, "feature a needs feature b";
- `excludes`: `(a, b)`, "a and b never ship in the same release";
- `needs_one_of`: `(a, [o1, o2, ...])`, "a needs at least one of the options";
- `bundles`: `(a, b)`, "a and b ship together or not at all".

`x[f]` is the Boolean "feature f ships". In logic, the four kinds are

```math
\begin{aligned}
x_a &\Rightarrow x_b && \forall (a, b) \in \text{requires} \\
\lnot x_a \lor \lnot x_b & && \forall (a, b) \in \text{excludes} \\
x_a &\Rightarrow (x_{o_1} \lor x_{o_2} \lor \dots) && \forall (a, O) \in \text{needs\_one\_of} \\
x_a &= x_b && \forall (a, b) \in \text{bundles}
\end{aligned}
```

Write `add_rules(model, x, requires, excludes, needs_one_of, bundles)` in `release.py`: one CP-SAT
constraint per rule, with no linear algebra and no big-M. The tests fix which features ship and ask
CP-SAT whether the rules allow it. About eight lines.
