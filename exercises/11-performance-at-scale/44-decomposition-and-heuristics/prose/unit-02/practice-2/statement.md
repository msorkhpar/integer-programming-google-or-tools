The water district of the previous practice now wants Benders to choose its stations. Building
station $`j`$ costs $`F_j`$ (`"build"`), and the whole question is

```math
\min_{x \in \{0,1\}} \; \sum_j F_j\, x_j + Q(x)
```

where $`Q(x)`$ is the pumping subproblem's cost. `pumping_cut` is given, with the same signature
as in practice 1 but a simpler inside, so that it does not give practice 1 away. It finds $`Q(\hat x)`$
without an LP, by filling the need from the cheapest source up (built stations by energy cost, then
the neighbor's water), and it returns the plain cut that works for any 0/1 plan when $`Q \ge 0`$:

```math
\theta \;\ge\; Q(\hat x)\Bigl(1 - \sum_{j:\ \hat x_j = 1} (1 - x_j) - \sum_{j:\ \hat x_j = 0} x_j\Bigr)
```

At $`\hat x`$ the bracket is 1, so the cut says $`\theta \ge Q(\hat x)`$; at every other 0/1 plan the
bracket is 0 or less, so the cut asks nothing that $`\theta \ge 0`$ does not already. It is valid,
but weaker than practice 1's dual cut, which also bounds the plans it did not come from. Your loop
must work with either: once your practice 1 passes, you may paste your own `pumping_cut` in its
place.

Every plan has a pumping solution in this district, and in the tests: the purchase limit covers the
demand on its own, and each station's capacity covers its own refill. So no master plan ever needs a
feasibility cut, and `pumping_cut` is never called on an infeasible plan.

Write the master first: its variables with domains (the build decisions and one continuous variable
standing in for the pumping cost, with its bound), its objective, and the cut rows it collects.
Say which number is a lower bound on the optimum and which is an upper bound, and when the loop may
stop.

Then write `benders(stations, demand, limit, price, max_iterations)` to run the loop and return
`(best_cost, best_plan, history)`: the cheapest total cost found, its plan (station name to 0 or
1), and one `(master_value, best_cost_so_far)` pair per iteration. Solve the master with HiGHS
through MathOpt. The tests compare your answer with every plan tried by brute force, so any correct
loop passes.

About fifteen lines.
