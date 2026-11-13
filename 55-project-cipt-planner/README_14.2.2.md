# 14.2.2 Many Years: Start Years, Windows and Cash-Flow Spreading

Finance read the first plan and sent it back:

> Your plan spends $13.14M in 2027. We have $8.89M that year. The $38.39M was five yearly budgets
> added up, and they are not interchangeable: money not spent in a year does not roll over. Plan
> by year. A project may start in any year of its window, and its cost lands in the years it is
> worked on, not all at the start. And no plan may run past 2031.

## The One-Envelope Plan Overspends the First Year

`steps/01` has one number for money and no years. It funds a project "in its earliest year", which
was the planners' assumption, not a decision. `years.py` takes the step-01 plan of GridCap small
(the fictional utility's 40 projects) and computes what it spends in each calendar year, from
the cost profiles the export has always carried:

```text
step 01 plan, spend against each year's budget ($k):
  2027  13,140 of  8,890  over by 4,250
  2028   6,620 of  8,120
  2029   7,870 of  8,760
  2030   6,740 of  8,610
  2031   4,020 of  7,850
```

The total fits; 2027 does not. The code cannot see it, for two reasons that both live in the
data structures. `Request` has `capital_budget`, one number, so no year can have its own limit.
`Project` has `capex`, one number, so the code cannot know that P022's $2,550k is spent as 360,
720 and 1,470 over three years. The model then has no variable that says *when*.

## A Start-Year Variable per Project and Year Carries the When

Three designs were considered:

| Choice | For | Against |
| --- | --- | --- |
| keep $`x_i`$, add a second integer variable for the start year | few variables | the year a cost lands in becomes a product of two variables, which is not linear |
| $`x_{i,t}`$, one binary per project and allowed start year (chosen) | each year's spend is linear in $`x`$ (lesson 6.4.1); windows are just "no variable" | more variables: 80 for GridCap small instead of 40 |
| charge the whole cost to the start year | the old budget row barely changes | lesson 6.4.2 showed it overspends later years on this same portfolio |

With $`x_{i,t}`$, a project's spend in year $`y`$ is $`\sum_{t \le y} c_{i,y-t}\, x_{i,t}`$: the
start variable carries the slice of the profile that lands in $`y`$ (lesson 6.4.2). A window
is the set of $`t`$ that get a variable at all, cut so the work ends inside the plan.

## The Model

The model of the lesson *The first request: fund projects within one budget*, with $`x_i`$ replaced by start-year variables and the envelope by
yearly budgets. Every part of it changed, so it is given whole.

**Sets.** $`P`$, the projects; $`Y`$, the plan's years (2027 to 2031 for GridCap small);
$`T_i \subseteq Y`$, the start years of project $`i`$: its window from the export, cut so that
$`t + d_i - 1 \le \max Y`$, where $`d_i`$ is its number of years of work.

**Parameters.** $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work,
$`k = 0, \dots, d_i - 1`$ ($k); $`v_i`$, its value, still the NPV of a start in its earliest
year ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P && \text{(once}_i) \quad \leftarrow \text{new} \\
\sum_{i \in P} \sum_{t \in T_i,\; t \le y < t + d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{was one envelope row}
\end{aligned}
```

The code names the rows `once_P001` and `budget_2027`. Note what the objective does not say: $`v_i`$
is the same for every start year, so the model has no reason to prefer an early start. That gap
is left on purpose for the lesson *Value: NPV by start year and risk reduction*, where finance's NPV by start year fills it.

## The Change, File by File

**`cipt/data.py`.** `Project` swaps `capex` for the profile and gains the window's end; `capex`
becomes a property, so code that read it keeps working. Two more members know the profile's
arithmetic: `duration`, the number of years of work ($`d_i`$, the profile's length), and
`spend(start)`, a dict from each calendar year of work to what the project spends in it. From
`steps/02/cipt/data.py`:

<!-- snapshot: steps/02/cipt/data.py -->
```python
    cost_profile: tuple[int, ...]   # $k spent in each year of work, from the start year on
    value: int                      # $k, the NPV finance quotes for a start in the earliest year
    earliest_start: int
    latest_start: int

    @property
    def capex(self) -> int:
        return sum(self.cost_profile)

    @property
    def duration(self) -> int:
        return len(self.cost_profile)

    def spend(self, start: int) -> dict[int, int]:
        """What the project spends in each calendar year if it starts in `start`."""
        return {start + k: amount for k, amount in enumerate(self.cost_profile)}
```

For P022, whose profile is 360, 720 and 1,470, `duration` is 3 and `spend(2028)` is
`{2028: 360, 2029: 720, 2030: 1470}`.

`Request` loses `capital_budget` and gains `years` and `budget`, a dict from year to $k. The window
cut is a method of `Request`, not of `Project`, because it needs the plan's last year. In `steps/01`
it was a stub that returned the earliest year alone; now, from `steps/02/cipt/data.py`:

<!-- snapshot: steps/02/cipt/data.py -->
```python
    def starts(self, project: Project) -> range:
        """The project's window, cut so that its work starts and ends inside the plan's years."""
        first = max(project.earliest_start, self.years[0])
        last = min(project.latest_start, self.years[-1] - project.duration + 1)
        return range(first, last + 1)
```

A window that the cut empties is an empty range, so the project gets no variable and cannot be
funded. That is how finance's "no plan may run past 2031" becomes code: not a row, an absence.

**`cipt/model.py`.** The variables are keyed by `(project, year)`: `x[p.project_id, t]` for each
`t` in `request.starts(p)`. Each year's spend is built once as an expression (lesson 6.4.2), then
bounded. The function that builds it, `spend_by_year(request, x)`, is the cash-flow spreading of
this step, and the page leaves its code to the practice. It returns a dict with one entry per plan
year $`y`$, the left side of $`\text{budget}_y`$ in the model above: for every project $`i`$ and
every start $`t \in T_i`$, the amount the profile spends in its $`k`$-th year of work lands in the
calendar year $`t + k`$, as that amount times $`x_{i,t}`$. `Project.spend(t)` already lists those
calendar years and amounts. A plan year that no start can spend in still gets its entry, an empty
sum.

Collect each year's terms in a list and sum the list once with `fast_sum`, rather than growing an
expression with `+=`: one sum per year instead of one new expression object per term. `build` then
adds the two row families, each row under its label. From `steps/02/cipt/model.py`:

<!-- snapshot: steps/02/cipt/model.py -->
```python
    for p in request.projects:                                            # (once_i)
        name = f"once_{p.project_id}"
        built.rows[name] = model.add_linear_constraint(built.started(p.project_id) <= 1, name=name)
    for y, spend in spend_by_year(request, x).items():                    # (budget_y)
        name = f"budget_{y}"
        built.rows[name] = model.add_linear_constraint(spend <= request.budget[y], name=name)
```

`Built.started(pid)` is new: the sum of a project's start variables, 1 if it starts in some year.
The lesson *Business rules: must-dos, bundles, parents and alternatives* uses it in nearly every rule.

**`cipt/solve.py`.** One line of meaning changed. The start year is now read from the variable that
is 1, not assumed. From `steps/02/cipt/solve.py`:

<!-- snapshot: steps/02/cipt/solve.py -->
```python
    starts = {pid: t for (pid, t), var in built.x.items() if values[var] > 0.5}
```

**`cipt/report.py`.** A new `spend_by_year(request, plan)` computes the plan's spend from the funded
starts, and `render` prints it against each budget. It is a second definition of spend, next to
the model's, on purpose: the report checks the plan with plain integer arithmetic, so a mistake in
the model's expressions shows up as a report that disagrees with the budgets.

**`tests/conftest.py`.** The `export` helper changed: a one-year export built with
`capital_budget=` now gets that amount as its one yearly budget. The tests of the lesson *The first request: fund projects within one budget* keep
their meaning (one year, one envelope) and still pass on the new code.

The planner on the demo export now prints a year table, and the plan moved money between years:

```text
$ python -m cipt data/demo.json    # steps/02
GridCap tiny: optimal
funded 5 of 8 projects, capex $6,090k of $7,890k, value $3,892k
  2027  spend $1,120k of $2,300k
  2028  spend $2,840k of $3,280k
  2029  spend $2,130k of $2,310k
```

## Every Year Now Fits, and Some Projects Start Late for No Reason

On GridCap small the step-02 model has twice the variables, and its plan fits every year:

```text
step 02 model: 80 binary variables, 45 rows
GridCap small: optimal
funded 25 of 40 projects, capex $41,680k of $42,230k, value $29,027k
  2027  spend $8,870k of $8,890k
  2028  spend $7,800k of $8,120k
  2029  spend $8,580k of $8,760k
  2030  spend $8,580k of $8,610k
  2031  spend $7,850k of $7,850k
started after their earliest year: 7 of 25 (P002, P008, P011, P021, P029, P030, P032)
```

The "of $42,230k" is the five yearly budgets of the export added up; the step-01 envelope was the
export's separate `capital_budget` figure, $38,390k, so the yearly budgets hold $3,840k more in
all. That is why the plan funds one more project and claims $1,643k more value even though each
year is now a hard limit: money a year leaves unused is lost, as 2028's $320k is here.

Seven projects start after their earliest year. Some must, to fit a budget. But the objective
values a late start the same as an early one, so the solver is free to push a start late for no
reason at all. The value $29,027k is therefore not what this plan is worth: finance's NPV for a
late start is lower. The lesson *Value: NPV by start year and risk reduction* fixes the objective.

## Each New Test Fails on the One-Envelope Code

The new tests in `steps/02/tests/test_years.py` compute each year's spend from the export's rows
in the test itself, never through the planner's own `spend_by_year`. From that file:

<!-- snapshot: steps/02/tests/test_years.py -->
```python
def test_spread_cost_counts_in_every_year_of_work():
    # A spends 50 in each of two years. Funding A and B fits the two-year total but not 2028.
    raw = export([row("A", (50, 50), 80), row("B", (50,), 40), row("C", (100,), 100, earliest=2028)],
                 years=YEARS, budget={2027: 100, 2028: 100})
    plan = solve(load_request(raw))
    assert plan.funded == ("B", "C")
    assert all(spent(raw, plan)[y] <= 100 for y in YEARS)
```

```text
14.2.2: 5 tests added; on step 01, 5 fail on an assertion; on step 02, 14 of 14 pass
  test_spread_cost_counts_in_every_year_of_work
    before: assert ('A', 'C') == ('B', 'C')
    after:  passed
  test_each_year_stays_within_its_budget
    before: assert {2027: 200, 2028: 0} == {2027: 100, 2028: 100}
    after:  passed
  test_start_stays_inside_the_window
    before: assert {'A': 2027} == {'A': 2028}
    after:  passed
  test_work_must_end_inside_the_plan
    before: assert ('A',) == ()
    after:  passed
  test_report_shows_spend_against_each_budget
    before: assert '  2027  spend $0k of $0k' in 'test: optimal\nfunded 1 of 1 projects, capex $100k
    after:  passed
```

Each "before" line is what the step-01 code answered. `{2027: 200, 2028: 0}` is the first year
overspent exactly as on GridCap small, in a case small enough to see why.

## Years Made the Data Richer and the Model Twice as Long

```text
14.2.2: steps/01 -> steps/02
  package lines 154 -> 192, functions 11 -> 17, tests 9 -> 14
  most branches: report.render (5) -> report.render (6)
  data.py        51 ->   65
  model.py       20 ->   36
  report.py      15 ->   24
  solve.py       35 ->   34
```

`data.py` grew almost as much as `model.py`: the years entered as data first (`cost_profile`,
`budget`, `duration`, `spend`, `starts`), and the model only reads them. That is the style the planner keeps from here on: data
records know the domain's arithmetic (what a start spends, which starts exist), and `model.py`
only turns it into variables and rows.

**Practice.** This lesson's project practice starts from `steps/01`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds.

<!-- practice 1 -->

## Summary

- **The one-envelope plan overspends the first year**, by $4,250k on GridCap small, because
  neither the data nor the model had years.
- **A start-year variable per project and year carries the when.** The window is the set of
  variables that exist, cut so the work ends inside the plan.
- **Spend is built once per year as an expression** and bounded by that year's budget.
- **Every year now fits, and some projects start late for no reason**: the value does not depend
  on the start year yet.

## Reference

| Name | Meaning |
| --- | --- |
| $`x_{i,t}`$ | 1 if project $`i`$ starts in year $`t`$ |
| $`T_i`$ | `request.starts(project)`: the window cut to the plan |
| $`c_{i,k}`$ | `cost_profile[k]` |
| `once_P001`, `budget_2027` | row names, the labels of $`\text{once}_i`$ and $`\text{budget}_y`$ |
| `Built.started(pid)` | $`\sum_{t} x_{i,t}`$ |

**Further reading:** [MathOpt `expressions.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/expressions.py) (`fast_sum` builds one sum from an iterable); [MathOpt `variables.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/variables.py) (`LinearSum`, the type each year's spend is); [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) (one cash-flow row per period, as lesson 6.4.2 cited it).

## Challenges

1. Count the nonzero coefficients of `budget_2031` on GridCap small with your own code, from
   `built.x` and the cost profiles.
2. Finance says unspent money may roll over to the next year. Which lesson of section 6 writes that
   rule, and which file of the planner would change?
3. A project's window in the export starts before 2027. What does `request.starts` do with it, and
   is that right?

## Design Note: Two Definitions of Spend, Kept Apart on Purpose

Lesson 6.4.2 argued for one definition of spend shared by every rule. The planner has two: the
model's expressions and the report's integer sum. They serve different readers. Every rule inside
the model uses the one expression; the report and the tests use an independent sum, so a model
that miscounts spend cannot also approve its own plan. One definition inside the model, one
independent check outside it.

## The Full Programs

**years.py.** Computes the step-01 plan's spend by year from the export, then plans GridCap small
with `steps/02` (*The One-Envelope Plan Overspends the First Year*, *Every Year Now Fits*). *Try:*
cut 2031's budget by $2,000k in the export dictionary and predict which projects move.

- Program: [years.py](src/years.py)

**cli_demo.py, ledger.py, code_size.py.** The demo run, the test ledger and the size table of
the lesson *The first request: fund projects within one budget*, here for step 02.

- Program: [cli_demo.py](src/cli_demo.py)
- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
