An airport authority funds runway and terminal projects, each whole or not at all: project $`i`$
costs `costs[i]` and is worth `values[i]` (whole $k). Its finance office forecasts what extra
budget buys with the LP relaxation's budget price, and the planning office wants that forecast
printed beside the real gain, for every scenario.

`build(costs, values, budget, integer)` is given: it returns a MathOpt model of the selection
($`\max \sum_i v_i x_i`$ subject to $`\sum_i c_i x_i \le B`$, with $`x_i \in \{0, 1\}`$, or
$`0 \le x_i \le 1`$ when `integer` is `False`) and its budget row. Write
`forecast_and_gain(costs, values, budget, extra)`, which returns a dict:

- `"forecast"`: the LP relaxation's budget price at `budget` (solved with GLOP), times `extra`;
- `"gain"`: the MILP's best value at `budget + extra` less its best value at `budget` (solved with
  HiGHS at `relative_gap_tolerance=0.0`).

Write down first what each number means to finance, and which one is the true answer. The tests
use small instances where the two agree and where they do not. About ten lines.
