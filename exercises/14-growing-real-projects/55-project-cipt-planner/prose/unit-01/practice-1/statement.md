The planning lead's first request:

> We have $38.39M of capital for the next five years and 40 candidate projects on GridCap small.
> Tell us which to fund to get the most value. Use the NPV finance quoted for each project.
> We'll worry about years later.

The project you start from is the skeleton: it reads the export and prints a report, but its model
is empty and `solve` funds nothing. Make the planner decide. Each project is a yes-or-no choice, the
funded projects together may cost no more than the capital budget, and the plan has the most total
value. Solve the model with HiGHS through MathOpt, keep anything HiGHS prints out of the report, and
read the answer back as a `Plan` in which each funded project starts in its earliest year.

The command line, `python -m cipt EXPORT.json`, plans the export file it is given.

`cipt/solve.py` already imports MathOpt and holds stubs for `run_highs` and `read_plan`; write
their bodies and make `solve` use them. `cipt/report.py` needs no change. It prints the report in
this format, every amount in whole $k with thousands commas:

- `<request name>: <status>`;
- `funded <n> of <all> projects, capex $<capex>k of $<capital budget>k, value $<value>k`, where
  capex and value are the totals of the funded projects;
- one line per funded project, in id order: two spaces, the id, two spaces, `start <year>`, two
  spaces, `capex` and a space and the capex right-aligned in 6 characters, two spaces, `value` and
  a space and the value right-aligned in 6 characters, two spaces, the project's name.

Run executes `main.py`, which plans the demo export in `data/demo.json` (GridCap tiny, a fictional
utility) and prints the report; `expected/report.txt` is the report it should print. Submit runs
every test in `tests/`, the skeleton's own included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `build` in `cipt/model.py`

```python
def build(request: Request) -> Built
```

- **Contract.** Takes a Request. Returns a Built holding a MathOpt model with one binary variable per project (named `x_<id>`), one row named budget that keeps the summed capex of the funded projects within capital_budget, and the summed value of the funded projects as the objective to maximize.
- **Modeling idea.** A yes-or-no choice per project under one budget is a 0-1 knapsack: the best fill is a combination, which no sort by value per dollar finds in general.
- **Taught in** [6.3.1 0-1 and Multi-Dimensional Knapsack](../../../../06-formulation-craft/25-knapsack-and-assignment/units/unit-01/6.3.1-0-1-and-multi-dimensional-knapsack.unit.html).

#### `run_highs` in `cipt/solve.py`

```python
def run_highs(model: mathopt.Model) -> mathopt.SolveResult
```

- **Contract.** Solves the model with HiGHS through MathOpt, on one thread, and returns the SolveResult. Nothing HiGHS prints may reach the program's standard output.
- **Modeling idea.** The solver is a call with parameters; its log is not the planner's report.
- **Taught in** [4.2.1 Model, Variables, Constraints, Objective](../../../../04-google-or-tools-in-depth/13-mathopt-core/units/unit-01/4.2.1-model-variables-constraints-objective.unit.html).

#### `read_plan` in `cipt/solve.py`

```python
def read_plan(built: Built, result: mathopt.SolveResult) -> Plan
```

- **Contract.** Turns a SolveResult into a Plan: the status in lower case, each project whose variable is 1 mapped to its earliest start year, and the objective value. With no feasible solution, a Plan with the status alone.
- **Modeling idea.** Read the termination first, then the variable values; a binary is 1 when its value is above 0.5.
- **Taught in** [4.2.2 Reading `SolveResult`: Termination, Primal and Dual Solutions, Statistics](../../../../04-google-or-tools-in-depth/13-mathopt-core/units/unit-02/4.2.2-reading-solveresult-termination-primal-and-dual-solutions-statistics.unit.html).

#### `solve` in `cipt/solve.py`

```python
def solve(request: Request) -> Plan
```

- **Contract.** Builds the model for a Request, solves it and returns the Plan.
- **Modeling idea.** Keep building, solving and reading back in separate functions, so each can be tested and changed alone.
- **Taught in** [14.2.1 The First Request: Fund Projects Within One Budget](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-01/14.2.1-the-first-request-fund-projects-within-one-budget.unit.html).
