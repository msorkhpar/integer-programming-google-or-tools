A school district buys bus service route by route. Two operators bid: a private company
(operator 0) and the city's transit agency (operator 1). Each **offer** is a row
`(seats, operator, price)`: that operator will run one route with a bus of that many seats at that
price. The city can take at most `city_limit` routes. A route needs a bus with at least as many seats
as it has riders.

Write `buy_routes(routes, offers, city_limit)` in `buses.py`. `routes` maps a route to its riders.
Return `(total, plan)`, with `total` an `int` (`round(solver.objective_value)`, not `int(...)`),
where `plan` maps each route to the offer it takes, as the tuple
`(seats, operator, price)`, chosen so that the total price is as small as possible. Every instance in
the tests has a plan.

The model, with $`R`$ the routes, $`n_r`$ their riders, $`O`$ the set of offer rows and $`L`$ the
city's limit:

```math
\begin{aligned}
& q_r \in \mathbb{Z},\ k_r \in \{0, 1\},\ p_r \in \mathbb{Z} && \forall r \in R && \text{(seats, operator, price)} \\
& \min \; \textstyle\sum_{r \in R} p_r \\
& (q_r, k_r, p_r) \in O && \forall r \in R && \text{(offer}_r) \\
& q_r \ge n_r && \forall r \in R && \text{(fits}_r) \\
& \textstyle\sum_{r \in R} k_r \le L && && \text{(city\_limit)}
\end{aligned}
```

The (offer) rows are table constraints. Bound $`q_r`$ and $`p_r`$ by the smallest and largest seats
and prices in the offers. The tests check the plan you return and its total, so any optimal plan
passes. About fifteen lines.
