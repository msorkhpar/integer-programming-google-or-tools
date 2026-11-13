The planning lead read the two plans of the lesson before and asked for something in between:

> The NPV plan leaves too much risk on the table, and the risk plan gives up $5.7M of NPV. Show us
> the options in between: for each extra bit of risk removed, how much NPV does it cost? And let us
> set a floor on risk removed and get the best NPV above it.

You start from the planner that values each start by NPV and by risk removed. Give the planners
the frontier: plans from the best NPV to the most risk removed, with plans in between, none of
which is beaten on both goals by another, and where two plans tie on one goal, the one that does
better on the other. Let the export set a floor on risk removed, and plan the best NPV above it.

`cipt/goals.py` already defines `Point`, one frontier plan with its NPV and risk removed. Two
plans whose NPVs differ by at most 0.5 count as the same point, and only the first found is kept;
dominated points are dropped after that. Every NPV in the export is a whole $k.

Run's report gains a section: after the plan, `main.py` prints an empty line, the line
`NPV against risk removed:`, then one line per frontier point of the demo export, from the best NPV
to the most risk removed:
`  NPV $<npv>k  risk removed $<risk>k  funds <ids>`, with two spaces before `NPV` and between the
parts, NPV in whole $k and risk with one decimal (both with thousands commas), and the funded
project ids in id order, separated by a comma and a space.

`cipt/diagnose.py` is the next lesson's stub, as the reference has it; no code of this step
imports it, so leave it as it is.

Submit runs every test in `tests/`, the earlier steps' included, and compares Run's report with the
expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `best` in `cipt/goals.py`

```python
def best(request: Request, first: str, floor: float | None = None) -> Plan
```

- **Contract.** Maximizes the goal named first ('npv' or 'risk'), with an optional floor on the risk removed as a row named risk_floor; then, holding the first goal at its best within KEEP, maximizes the other. Returns the second solve's Plan, or the first one's when it is not optimal.
- **Modeling idea.** A lexicographic second solve keeps the first goal and takes the most of the other, so no point is beaten by a plan equal on the first goal.
- **Taught in** [8.2.1 Hierarchical Objectives with Tolerances](../../../../08-multi-objective-optimization/35-lexicographic/units/unit-01/8.2.1-hierarchical-objectives-with-tolerances.unit.html).

#### `dominates` in `cipt/goals.py`

```python
def dominates(a: Point, b: Point) -> bool
```

- **Contract.** True when point a is at least as good as b on both goals and better on one, each comparison within the slack KEEP gives that goal.
- **Modeling idea.** A point is on the frontier when no other point dominates it.
- **Taught in** [8.3.2 AUGMECON: Avoiding Weakly Efficient Points](../../../../08-multi-objective-optimization/36-epsilon-constraint/units/unit-02/8.3.2-augmecon-avoiding-weakly-efficient-points.unit.html).

#### `frontier` in `cipt/goals.py`

```python
def frontier(request: Request, points: int = 5) -> list[Point]
```

- **Contract.** Returns up to `points` non-dominated points, from the best NPV to the most risk removed: the two ends, then best NPV for risk floors spread evenly between the ends' risk. Drops a point whose NPV repeats one already found, and any dominated point. Empty when either end is not optimal.
- **Modeling idea.** The epsilon-constraint method: maximize one goal while the other must reach a floor, for a series of floors.
- **Taught in** [8.3.1 The ε-Constraint Method](../../../../08-multi-objective-optimization/36-epsilon-constraint/units/unit-01/8.3.1-the-constraint-method.unit.html).

#### `risk_floor` in `cipt/rules.py`

```python
def risk_floor(built: Built) -> None
```

- **Contract.** Adds a row risk_floor (the plan removes at least the request's risk_floor) when the request sets one, and nothing otherwise.
- **Modeling idea.** A floor the planners set is one more named row over the risk expression.
- **Taught in** [8.3.1 The ε-Constraint Method](../../../../08-multi-objective-optimization/36-epsilon-constraint/units/unit-01/8.3.1-the-constraint-method.unit.html).

#### `solve_built` in `cipt/solve.py`

```python
def solve_built(built: Built) -> Plan
```

- **Contract.** Solves a Built the caller may have changed after build (a new objective, an extra row) and returns its Plan.
- **Modeling idea.** Solving a model you changed is a separate step from building it.
- **Taught in** [14.2.5 Two Goals: Risk Against NPV](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-05/14.2.5-two-goals-risk-against-npv.unit.html).

#### `build` in `cipt/model.py`

```python
def build(request: Request) -> Built
```

- **Contract.** Sets the NPV and risk expressions on the Built before the rules run, so a rule may name them.
- **Modeling idea.** A rule over a goal needs the goal's expression to exist first.
- **Taught in** [14.2.5 Two Goals: Risk Against NPV](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-05/14.2.5-two-goals-risk-against-npv.unit.html).

#### `load_request` in `cipt/data.py`

```python
def load_request(raw: dict) -> Request
```

- **Contract.** Also reads the request's optional risk_floor, in $k; None when the export has none.
- **Modeling idea.** The floor is a request setting, so the planners can ask for it in the export.
- **Taught in** [14.2.5 Two Goals: Risk Against NPV](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-05/14.2.5-two-goals-risk-against-npv.unit.html).
