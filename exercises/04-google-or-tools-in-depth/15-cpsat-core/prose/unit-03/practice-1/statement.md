A data team (not GridCap) feeds CP-SAT models from spreadsheets whose numbers have decimals: bench
hours per sample, grams of protein per portion, litres per bottle. Every row has to reach the solver
with whole numbers, and must allow exactly the integer points it allowed before.

Write `scale_row(coefficients, rhs, sense)` in `scaling.py`. The coefficients and the right-hand side
come as decimal text (`"1.25"`), and `sense` is `"<="`, `">="` or `"=="`. Return the pair
`(whole_coefficients, whole_bound)`: lists and numbers of Python `int`s. For a row

```math
\sum_j c_j\, x_j \;\square\; b, \qquad x_j \in \mathbb{Z}, \quad \square \in \{\le, \ge, =\}
```

find the smallest whole $`m \ge 1`$ that makes every $`m\,c_j`$ whole, and return $`m\,c_j`$ and a
whole bound $`b'`$ such that $`\sum_j m\,c_j\,x_j \;\square\; b'`$ allows exactly the same integer
points. Think about each sense separately: what is the right whole bound when $`m\,b`$ is not whole?
For `"=="`, return `None` as the bound when no integer point can meet the row.

`fractions.Fraction("1.25")` reads decimal text exactly. The tests compare the original row and yours
on every small integer point. About ten lines.
