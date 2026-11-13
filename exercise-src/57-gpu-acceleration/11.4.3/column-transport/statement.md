A distributor ships from $`m`$ depots to $`n`$ customers. Depot $`i`$ holds $`a_i`$ units, customer
$`j`$ needs $`d_j`$, a unit on route $`(i, j)`$ costs $`k_{ij}`$, and each route can carry at most
$`q_{ij}`$ units. A depot need not ship everything it holds. The team wants the cheapest shipping
plan, and it wants the LP handed to HiGHS in the column-wise form that GPU solvers read fast, so
that the same model object runs on the CPU and, where there is one, on the GPU.

Before you code, write the formulation: the variables with their bounds, the objective, and one
labelled row per depot and per customer, with the direction of each. Then build it in `routes.py`:
`build(supply, demand, cost, cap)` returns a `highspy.HighsLp` with the depot rows first (rows
$`0 .. m-1`$), the customer rows after them (rows $`m .. m+n-1`$), and variable $`i \cdot n + j`$ for
route $`(i, j)`$. Store the matrix column-wise (`highspy.MatrixFormat.kColwise`): `start_[k]` is
where column $`k`$'s entries begin in `index_` (the row numbers) and `value_`. `solve(lp, solver)` is
given. On the GPU image with a GPU, `test_the_routes_are_solved_at_the_cheapest_cost` also solves
your model with HiGHS's GPU PDLP. On a machine without a GPU that test runs its CPU part only, and it
says nothing about the GPU part: no test is reported as skipped. About fifteen lines.
