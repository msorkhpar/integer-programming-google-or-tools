GridCap's vegetation program manager sent the first request:

> We have $962k for tree trimming this year and twenty distribution circuits that are due. Tell me
> which ones to trim so that we take out the most tree risk. I don't need dates yet, just the list.

You start from the skeleton: it generates a season, reads it into a `Season` and prints a report,
but `make_plan` trims nothing. Make the planner decide. Each circuit is trimmed or not, the trimmed
circuits together cost no more than the season's budget, and the plan removes the most risk a year.
Build the model with MathOpt, solve it with HiGHS with no gap left between the plan and its bound,
and read the answer back as a `Plan` with one `Trim` per trimmed circuit, the total cost and the
total risk removed. A budget too small for any circuit is still an answer: an optimal plan with no
trims.

The report is already written: `vegcrew/report.py` prints the season line, the status line and one
line per trimmed circuit, and this step does not change it.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the skeleton's own included, and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `vegcrew/planner.py`

```python
def build(season: Season) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]
```

- **Contract.** Takes a Season. Returns a MathOpt model and its variables: one binary variable per circuit (named `x_<cid>`, keyed by the circuit id), one row named budget that keeps the summed cost of the trimmed circuits within the season's budget, and the summed yearly risk of the trimmed circuits as the objective to maximize.
- **Modeling idea.** A yes-or-no choice per circuit under one budget is a 0-1 knapsack: the best list is a combination, which no ranking by risk per dollar finds in general.
- **Taught in** [6.3.1 0-1 and Multi-Dimensional Knapsack](../../../../06-formulation-craft/25-knapsack-and-assignment/units/unit-01/6.3.1-0-1-and-multi-dimensional-knapsack.unit.html).

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season) -> Plan
```

- **Contract.** Builds the model, solves it with HiGHS through MathOpt with a relative gap of zero, and returns a Plan: the status (OPTIMAL, FEASIBLE, INFEASIBLE, or the name of any other termination reason), one Trim per circuit whose variable is above 0.5, and their summed cost and risk removed. With no feasible solution, a Plan with the status alone. A budget too small for any circuit is an OPTIMAL plan with no trims.
- **Modeling idea.** Read the termination first, then the variable values; a binary is 1 when its value is above 0.5.
- **Taught in** [4.2.1 Model, Variables, Constraints, Objective](../../../../04-google-or-tools-in-depth/13-mathopt-core/units/unit-01/4.2.1-model-variables-constraints-objective.unit.html).
