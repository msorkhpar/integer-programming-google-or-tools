A pest-control company's van leaves its base each morning, visits every booked customer once and
comes back. `walk.py` already builds the routing model (`build`, the same shape as the lesson's).
Write `solve_tour(cost, depot)`: solve the model with the `PATH_CHEAPEST_ARC` first-solution
strategy, then return the tour as a list of **node** numbers that starts and ends at the depot,
and the tour's total cost.

The solution holds no list of stops. It holds a successor $`\text{next}_i`$ for each solver index
$`i`$, and the tour is the chain

```math
s,\ \text{next}_s,\ \text{next}_{\text{next}_s},\ \dots,\ e
```

from the vehicle's start index $`s`$ to its end index $`e`$, with total
$`\sum c_{\text{node}(i),\, \text{node}(\text{next}_i)}`$ over every arc of the chain. Before you
code, say which call gives $`s`$, which tells you that you have reached $`e`$, and which node $`e`$
stands for.

The tests compare your total with the best of every possible order, which this small instance
allows. About twelve lines.
