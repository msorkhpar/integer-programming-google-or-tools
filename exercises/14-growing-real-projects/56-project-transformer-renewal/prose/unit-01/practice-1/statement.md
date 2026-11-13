The asset team sent the first request:

> **Request 1.** We have $10,000k for transformer replacements in 2027. Replace the worst
> transformers we can afford. The list must be repeatable, so put it in code, with tests.

You start from the skeleton: it generates a fleet and ranks it worst condition first, stopping at the
first unit that does not fit. Keep the ranking as a baseline, and make `plan` choose with a model
instead. Each transformer is replaced this year or not, the replaced units together cost no more
than the budget, and the plan removes the most risk, where a unit's risk is its probability of
failure this year times its consequence of failure (`fleet.risk`). Build the model with MathOpt and
solve it with HiGHS. Then write `feasible`, which pins one whole list and asks the solver whether the
model allows it, so a test can show a list at the budget allowed and one just over it refused.

The starting code is the skeleton, plus the files this step adds as the reference has them, with
the blueprint's methods stubbed. `renewal/model.py` has its imports and `Built`, and the `build`
stub. `renewal/solve.py` is whole: the lesson's `FOUND`, `solve_quietly`, `is_feasible` and
`read_plan`, ready for `plan.py` to call. `renewal/risk.py` is the next step's stub; nothing in
this step imports it, so leave it as it is.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56, with a $2,000k budget, by the ranking and by the model,
and prints what each list costs and removes; `expected/report.txt` is the report it should print.
Its three lines are, with money in $k, a comma between thousands and no decimals:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k in 2027
worst first: <units> units, $<cost>k, risk removed $<risk>k
model      : <units> units, $<cost>k, risk removed $<risk>k (<status>)
```

where `<cost>` is what the list's units cost, `<risk>` the sum of `fleet.risk` over them, and
`<status>` the `Plan`'s status, the termination reason's name. Submit runs every test in `tests/`,
the skeleton's own included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `plan` in `renewal/plan.py`

```python
def plan(fleet: list[Transformer], request: Request) -> Plan
```

- **Contract.** Builds the model, solves it with HiGHS through MathOpt, and returns a Plan: each transformer whose variable is 1 mapped to FIRST_YEAR, the objective value, the dual bound, and the name of the termination reason as the status. With no plan found, a Plan with no replacements and the status alone. Nothing the solver prints may reach standard output, since Run's report is compared line by line.
- **Modeling idea.** Read the termination first, then the variable values; a binary is 1 when its value is above 0.5.
- **Taught in** [4.2.2 Reading `SolveResult`: Termination, Primal and Dual Solutions, Statistics](../../../../04-google-or-tools-in-depth/13-mathopt-core/units/unit-02/4.2.2-reading-solveresult-termination-primal-and-dual-solutions-statistics.unit.html).

#### `build` in `renewal/model.py`

```python
def build(fleet: list[Transformer], request: Request) -> Built
```

- **Contract.** A new module. Returns a Built, a dataclass holding the MathOpt model, the variables `x` keyed by transformer id, and the budget row: one binary variable per transformer named `x_<tid>`, one row named `budget` keeping the summed cost of the replaced units within request.budget, and the summed risk of the replaced units as the objective to maximize.
- **Modeling idea.** A yes-or-no choice per unit under one budget is a 0-1 knapsack: the best list is a combination, which no ranking finds in general.
- **Taught in** [6.3.1 0-1 and Multi-Dimensional Knapsack](../../../../06-formulation-craft/25-knapsack-and-assignment/units/unit-01/6.3.1-0-1-and-multi-dimensional-knapsack.unit.html).

#### `feasible` in `renewal/plan.py`

```python
def feasible(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> bool
```

- **Contract.** Builds the same model, fixes the variable of every listed unit to 1 and of every other unit to 0, solves, and answers whether the solver found a plan.
- **Modeling idea.** To test a rule, pin a whole plan with variable bounds and ask whether it is feasible; a pair of plans on either side of a limit shows the row is there and in the right place.
- **Taught in** [12.3.1 Unit-Testing One Constraint at a Time](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-01/12.3.1-unit-testing-one-constraint-at-a-time.unit.html).
