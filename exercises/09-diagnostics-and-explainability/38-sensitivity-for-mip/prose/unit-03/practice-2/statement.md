A library system renovates branches: renovation $`i`$ costs `costs[i]` and is worth
`values[i]` (whole $k), done whole or not at all. `best(costs, values, budget)` is given: it
returns $`V(B)`$, the best total value within budget $`B`$. Finance already knows the budget it
has, `hi`, and asks how far the value would fall with less: every budget in `[lo, hi]` where
$`V`$ steps, found by walking the curve **downward** from `hi`.

Lesson 9.2.3 walked upward. Downward, the question at a budget $`b`$ is: at which budget did the
flat stretch that $`b`$ stands on begin? It began at the cheapest plan worth $`V(b)`$. So:

1. Write the formulation of `cheapest(costs, values, level)`: the least cost of any plan worth at
   least `level`, with its variables, objective and constraints.
2. Write `cheapest`, then `step_points(costs, values, lo, hi)`. It returns the list of
   `(budget, value)` pairs where $`V`$ steps in `[lo, hi]`, in increasing order of budget,
   starting with `(lo, V(lo))`, exactly the list lesson 9.2.3's `step_points` returns. Costs and
   budgets are whole numbers, so the budget just below a stretch that begins at $`s`$ is
   $`s - 1`$.

The tests compare your list with a curve computed at every whole budget. About fifteen lines.
