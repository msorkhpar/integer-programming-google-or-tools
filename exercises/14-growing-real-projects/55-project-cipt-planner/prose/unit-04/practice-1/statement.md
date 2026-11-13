Finance and the asset team both had comments on the step-03 plan:

> Finance: you value every project at its earliest-start NPV, whatever year you start it. A project
> started in 2030 is worth less than the same project started in 2027; we sent you the NPV for
> every start year. Use it.
>
> Asset management: NPV is not why we replace old equipment. Each project lowers the failure risk of
> one asset. We want to see how much risk a plan removes, and a plan that removes the most of it.

You start from the rule-keeping planner of the lesson before. Price every start: its NPV is the
figure finance quotes for that start year, and the risk it removes is the asset's yearly risk,
failure probability times the cost of a failure, over every year after the work ends to the end of
the plan. The failure probability comes from the asset's Weibull curve. The export says which of
the two the plan maximizes, NPV unless it says risk, and the plan and its report carry both.

The export gives each asset's `age` in the plan's first year; the asset is one year older in each
later year. The report changes in three ways, every amount with thousands commas:

- the funded line keeps its form,
  `funded <n> of <all> projects, capex $<capex>k of $<budgets>k, value $<value>k`, but its value
  is now the plan's objective, what the model maximized, in whole $k (the NPV of the actual starts
  when the export asks for NPV);
- a new line follows it: `NPV $<npv>k, risk reduced $<risk>k (maximized: <objective>)`, NPV in
  whole $k and risk with one decimal;
- each funded project's line ends `capex <capex>  npv <npv>  <name>`: the label `npv` replaces
  `value`, and the amount, right-aligned in 6 characters, is the NPV of the year the project
  starts.

`cipt/goals.py` is the next lesson's stub, as the reference has it; no code of this step imports
it, so leave it as it is.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `annual_pof` in `cipt/value.py`

```python
def annual_pof(beta: float, eta: float, age: float) -> float
```

- **Contract.** Returns the chance that an asset of this age fails within the next year, given that it has not failed yet, on a Weibull curve with shape beta and scale eta.
- **Modeling idea.** The conditional one-year PoF is 1 - exp(H(age) - H(age + 1)), with the cumulative hazard H(a) = (a / eta) ** beta.
- **Taught in** [7.3.1 Probability of Failure and Hazard Curves (Weibull)](../../../../07-the-capital-planning-domain/32-asset-risk/units/unit-01/7.3.1-probability-of-failure-and-hazard-curves-weibull.unit.html).

#### `annual_risk` in `cipt/value.py`

```python
def annual_risk(request: Request, project: Project, year: int) -> float
```

- **Contract.** Returns the expected failure cost, in $k, of the project's asset in a calendar year if nothing is done: the consequence of failure times the PoF at the asset's age in that year. The export's age is the asset's age in the plan's first year, so in year y the age is age + y - first year.
- **Modeling idea.** Risk is PoF times CoF, and the age grows by one each year from the plan's first year.
- **Taught in** [7.3.3 Consequence of Failure and Risk = PoF × CoF](../../../../07-the-capital-planning-domain/32-asset-risk/units/unit-03/7.3.3-consequence-of-failure-and-risk-pof-cof.unit.html).

#### `risk_reduction` in `cipt/value.py`

```python
def risk_reduction(request: Request, project: Project, start: int) -> float
```

- **Contract.** Returns the risk removed by a start in a given year: the asset's annual risk summed over every year after the work ends, to the plan's last year.
- **Modeling idea.** Work removes the risk of the years after it is done; a later start removes fewer years.
- **Taught in** [7.3.4 Risk Reduction From an Intervention, Year by Year](../../../../07-the-capital-planning-domain/32-asset-risk/units/unit-04/7.3.4-risk-reduction-from-an-intervention-year-by-year.unit.html).

#### `coefficients` in `cipt/value.py`

```python
def coefficients(request: Request) -> dict[tuple[str, int], tuple[int, float]]
```

- **Contract.** Returns, for every project and start year the model has a variable for, the pair (NPV of that start, risk reduction of that start).
- **Modeling idea.** Price each start before the model is built, so each variable gets its own coefficient.
- **Taught in** [7.2.4 Precomputing NPV Coefficients by Start Year](../../../../07-the-capital-planning-domain/31-financial-evaluation/units/unit-04/7.2.4-precomputing-npv-coefficients-by-start-year.unit.html).

#### `build` in `cipt/model.py`

```python
def build(request: Request) -> Built
```

- **Contract.** Keeps the plan's NPV and its risk removed as two expressions on the Built, and maximizes the one the request's objective names ('npv' or 'risk').
- **Modeling idea.** Two measures over the same variables are two linear expressions; the objective picks one.
- **Taught in** [14.2.4 Value: NPV by Start Year and Risk Reduction](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-04/14.2.4-value-npv-by-start-year-and-risk-reduction.unit.html).

#### `read_plan` in `cipt/solve.py`

```python
def read_plan(built: Built, result: mathopt.SolveResult) -> Plan
```

- **Contract.** Also returns the plan's NPV and risk removed, evaluated from the two expressions at the solution.
- **Modeling idea.** The plan reports both measures whichever one was maximized.
- **Taught in** [4.2.2 Reading `SolveResult`: Termination, Primal and Dual Solutions, Statistics](../../../../04-google-or-tools-in-depth/13-mathopt-core/units/unit-02/4.2.2-reading-solveresult-termination-primal-and-dual-solutions-statistics.unit.html).

#### `load_request` in `cipt/data.py`

```python
def load_request(raw: dict) -> Request
```

- **Contract.** Also reads each project's NPV for every start year and its asset (id, age, Weibull shape and scale, consequence of failure), and the request's objective, 'npv' by default; refuses any other objective.
- **Modeling idea.** The export already carries NPV by start year and asset health; read them where they are.
- **Taught in** [7.2.4 Precomputing NPV Coefficients by Start Year](../../../../07-the-capital-planning-domain/31-financial-evaluation/units/unit-04/7.2.4-precomputing-npv-coefficients-by-start-year.unit.html).

#### `render` in `cipt/report.py`

```python
def render(request: Request, plan: Plan) -> str
```

- **Contract.** Changes the report in three ways. The funded line's `value $<value>k` is now the plan's objective, what the model maximized (the NPV of the actual starts when the objective is 'npv'). After it comes the line `NPV $<npv>k, risk reduced $<risk>k (maximized: <objective>)`, NPV in whole $k and risk with one decimal, both with thousands commas. Each funded project's line shows `npv` and the NPV of the year the project starts, right-aligned in 6 characters, where it showed `value` and the earliest-start value.
- **Modeling idea.** A report shows the measure that was not maximized as well as the one that was.
- **Taught in** [14.2.4 Value: NPV by Start Year and Risk Reduction](../../../../14-growing-real-projects/55-project-cipt-planner/units/unit-04/14.2.4-value-npv-by-start-year-and-risk-reduction.unit.html).
