A city transit agency plans next year's bus purchases with a small MILP, and its board wants a
report of the rules the chosen plan sits on. The agency's model is stored as data: each row is a
`Row` with a name, its coefficients by variable, a sense (`"<="`, `">="` or `"=="`) and a
right-hand side. A plan gives each variable a value; a variable the plan does not mention is 0.

Write two functions in `slacks.py`:

- `slack(row, plan)`: the room the plan leaves on the row, $`\ge 0`$ when the row holds, $`0`$ when
  the plan sits exactly on it, and negative when the plan breaks it. An `==` row is broken by any
  miss, above or below.
- `binding(rows, plan, tol=1e-6)`: the names of the rows the plan keeps with no room left, within
  `tol`, in the order given.

With $`a`$ a row's coefficients, $`x`$ the plan and $`b`$ its right-hand side, write the slack of
each kind of row first, then code it:

```math
\text{slack}(a^\top x \le b) = \;? \qquad \text{slack}(a^\top x \ge b) = \;? \qquad \text{slack}(a^\top x = b) = \;?
```

"Binding" here means what the board will read: the plan keeps the row and has no room left on it.
A row the plan breaks is a different finding, and the tests check that it is not reported as
binding. The tests use their own rows and plans; no solver is needed.
