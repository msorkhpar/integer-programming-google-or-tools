A regional water utility relines old mains in standard **lots**. Each lot type $`j`$ takes
$`a_j`$ crew-days, is worth $`c_j`$ (in $10k of avoided breaks), and can be bought at most
$`u_j`$ times this season, because each type needs a liner the supplier rations. With $`d`$
crew-days, the best season is

```math
z(d) \;=\; \max \sum_{j} c_j\, x_j
\qquad \text{s.t.} \quad \sum_{j} a_j\, x_j \le d \quad \text{(days)}, \qquad
x_j \in \{0, 1, \dots, u_j\} \ \ \forall j
```

Write `value_function(days, worth, limits, capacity)`, which returns the list
$`[z(0), z(1), \dots, z(\text{capacity})]`$. `days`, `worth` and `limits` hold $`a_j`$, $`c_j`$
and $`u_j`$ for each lot type, all whole numbers, with every $`a_j \ge 1`$.

A table filled from small $`d`$ to large, as lesson 9.2.1's `value_function` did, works once
each type has a limit, if each copy of a type is treated as one more item that can be taken or
left. Decide how the table must be updated so that one copy is never counted twice.

The tests compare your list with every purchase enumerated by hand on small instances. About
eight lines.
