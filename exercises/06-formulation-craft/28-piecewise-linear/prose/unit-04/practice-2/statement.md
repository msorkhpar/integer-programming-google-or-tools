A water utility has a refurbishment fund for its fleet of pumps. Each pump in `pumps` has an age
(years), a Weibull shape `beta` and scale `eta` (years), a cost per failure `cof` ($k) and the cost
of a full refurbishment `capex` ($k). A refurbishment of **depth** `d` between 0 and 1 costs
`d * capex` and leaves the pump as old as `(1 - d) * age`. A failed pump is repaired just enough to
run again, so the expected number of failures between ages `a` and `a + h` is
`((a + h) / eta) ** beta - (a / eta) ** beta`.

1. Write `value_points(pump, horizon)`: the failure cost (in $k) that a refurbishment avoids over
   the next `horizon` years, at each depth of `DEPTHS = (0, 0.25, 0.5, 0.75, 1)`, as a list of five
   numbers.
2. Write `plan(pumps, fund, horizon)`: a MathOpt model that chooses a depth per pump, with each
   pump's value read from the five-point curve through `value_points` (straight lines between
   them), keeps the total cost within `fund`, and maximizes the total value. Solve it with HiGHS to
   a zero gap and return the optimal value and a dict of depths.

With $`R`$ the pumps and $`V_{i,j}`$ pump $`i`$'s value at depth $`D_j`$, write the formulation first:

```math
\begin{aligned}
\max \;& \sum_{i \in R} v_i \\
& \sum_{i \in R} \text{capex}_i\, d_i \le \text{fund}, \qquad 0 \le d_i \le 1 \\
& v_i = \text{the five-point curve of pump } i \text{ at } d_i \qquad \text{(your variables and rows)}
\end{aligned}
```

Some fleets have pumps whose failure rate speeds up with age, and some whose rate grows slowly.
Look at the curves' shapes before you choose how to write each one; the cheapest exact choice per
pump is the one a reviewer expects, but any exact formulation passes.

The tests compare your points with the formula, and your plan's value with a Pyomo model built from
the same curves with `pyomo.environ.Piecewise(..., pw_constr_type="EQ", pw_repn="INC")` and solved
by HiGHS. About thirty lines.
