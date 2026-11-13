# 14.1.1 The First Request: Which Circuits to Trim This Year

This module grows one project, GridCap's vegetation crew planner, from a first small request into a
CP-SAT crew scheduler, one requirement per lesson. Each lesson starts from the code the last one left
and ends with the code the next one starts from. The project is kept as complete snapshots, each a
directory you can run on its own:

| Snapshot | What it is |
| --- | --- |
| `steps/00` | the project before this lesson: a skeleton that loads a season and plans nothing |
| `steps/01` | the project after this lesson |
| `steps/NN` | the project after the module's NN-th lesson, up to `steps/08` |

Every snapshot holds the package `vegcrew`, its tests and a `pytest.ini`, so `python -m pytest` and
`python -m vegcrew` run inside it. A lesson shows each file it changes, before and after, the
formulation before and after, the tests it adds and how they fail on the old code, and what the step
did to the code's size and style. Its practice starts you from the snapshot before the lesson and is
graded by the tests of the snapshot after it.

GridCap is a fictional utility. The project generates its own seasons from a seed
(`vegcrew/generate.py`); none of the circuits, costs or risks is a real utility's data.

The first request comes from GridCap's vegetation program manager:

> We have $962k for tree trimming this year and twenty distribution circuits that are due. Tell me
> which ones to trim so that we take out the most tree risk. I don't need dates yet, just the list.

Trimming here means clearing the trees along a circuit's overhead lines, a whole circuit at a time.
Each circuit has a cost, in $k, and a **risk**: the dollars a year of tree-caused outages and damage
that a trim removes (an estimate of the kind lesson 7.3.4 computes). The manager asks for the
set of circuits, within the money, whose risks add up to the most.

## The Starting Code Loads a Season and Plans Nothing

`steps/00` is the skeleton a team would set up before the first model: the data types, a loader, a
generator, a report and an entry point, with the planner's body still to write.

| File | What it holds |
| --- | --- |
| `vegcrew/generate.py` | `scenario(size, seed)`: a season as plain JSON-ready values, the shape the circuit inventory exports |
| `vegcrew/data.py` | `Circuit` and `Season`, frozen dataclasses, and `season_from_dict`, which reads only the columns the planner uses |
| `vegcrew/planner.py` | `Trim`, `Plan` and `make_plan(season)`, the function this lesson writes |
| `vegcrew/report.py` | `format_plan(season, plan)`: the plan as text |
| `vegcrew/__main__.py` | `python -m vegcrew [tiny\|small\|medium] [--seed N]` |
| `tests/test_data.py` | three tests of the generator and the loader |
| `main.py`, `expected/report.txt` | plans the tiny season and prints the report, wherever it is started from; the report it prints |

The planner is a signature, a contract in its docstring, and a body that returns an empty plan:

<!-- snapshot: steps/00/vegcrew/planner.py -->
```python
@dataclass(frozen=True)
class Plan:
    status: str                                     # OPTIMAL, FEASIBLE, INFEASIBLE or NOT_SOLVED
    trims: dict[str, Trim] = field(default_factory=dict)
    cost: int = 0                                   # $k spent
    risk_removed: int = 0                           # $k a year of risk the trims remove


def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim this year: the most risk removed within the budget.

    Not written yet (lesson 14.1.1).
    """
    return Plan("NOT_SOLVED")
```

`Plan` is the answer's shape, settled before any model exists: a status, the trims by circuit id, and
two totals. Every later lesson reads a plan through these fields, so they are the project's public
face; the model behind them can change completely (and it will, in the lesson *A trim takes weeks on one crew: from MILP to CP-SAT intervals*) without the report
or the tests noticing. Run on the small season, the skeleton says what it cannot do:

```text
steps/00:
season small-54: 20 circuits, budget $962k
status NOT_SOLVED: 0 trims, cost $0k, risk removed $0k a year
```

The generator draws each column from its own random stream, named after the seed, the size and the
column. That matters later: when the lesson *Crews and months: capacity over time* adds a column for crew-weeks, the costs and risks of
every circuit stay exactly what they were, so plans from different lessons can be compared.

## A Budget and Yes-or-No Choices Make a 0-1 Knapsack

Read the request as a model (lesson 1.1.1): the **decision** is, for each circuit, trim it or not; the
**objective** is the total risk removed, as large as possible; the one **constraint** is the money.
That is the 0-1 knapsack of lesson 6.3.1: items with a weight (cost) and a value (risk), one capacity
row, each item taken whole or not at all.

There are three ways to answer it, and the choice is the lesson's design decision:

| Option | What it gives | Why not, or why |
| --- | --- | --- |
| Rank by risk per $k and fund down the list | a spreadsheet answer anyone can check | not always the best set: a high-ratio circuit can block two that together remove more |
| Dynamic programming over budget amounts (lesson 6.3.1) | the exact best set, fast for one row | one more resource (crews, next lesson) needs one more table axis, and the table grows with every row |
| A MILP: one binary per circuit, solved by HiGHS through MathOpt (lesson 4.2.1) | the exact best set, proven | chosen: every later requirement is one more row or variable, not a new algorithm |

The MILP wins on the next lessons, not on this one. A ranking might be good enough for a single
budget row, but the manager's list of rules will grow, and a model can take rules one row at a time.

## The Model

**Sets.** $`C`$, the circuits on the list.

**Parameters.** $`\text{cost}_c`$, the cost of trimming circuit $`c`$ ($k); $`\text{risk}_c`$, the
risk a trim of $`c`$ removes ($k a year); $`B`$, the year's budget ($k).

**Variables.** $`x_c \in \{0, 1\}`$ for every $`c \in C`$: 1 if circuit $`c`$ is trimmed this year.

**Objective.**

```math
\max \; \sum_{c \in C} \text{risk}_c \, x_c
```

**Constraints.**

```math
\begin{aligned}
\sum_{c \in C} \text{cost}_c \, x_c &\le B && && \text{(budget)}
\end{aligned}
```

| Label | Row name in `planner.py` |
| --- | --- |
| budget | `budget` |

The model before this lesson was no model at all; this is the whole of it.

## The Change, File by File

Only `vegcrew/planner.py` changes for the requirement. (`steps/01` also carries two one-line stubs for
the lesson *Crews and months: capacity over time*, a constant in `data.py` and a field of `Trim`, so that the next practice's tests import
cleanly; they do nothing yet.)

**Imports and constants, added.** MathOpt, the exact-gap setting, and a map from MathOpt's
termination reasons to the plan's status words:

<!-- snapshot: steps/01/vegcrew/planner.py -->
```python
from ortools.math_opt.python import mathopt

from vegcrew.data import Season

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
STATUS = {mathopt.TerminationReason.OPTIMAL: "OPTIMAL", mathopt.TerminationReason.FEASIBLE: "FEASIBLE",
          mathopt.TerminationReason.INFEASIBLE: "INFEASIBLE"}
```

`EXACT` asks HiGHS not to stop until it has proved the plan optimal, with no relative gap (the gap is
defined in lesson 3.4.1). MathOpt's `SolveParameters` docstring says a solver may stop, and report
OPTIMAL, once the relative gap is at most its tolerance; with a tolerance above zero, a test that
compares the plan with a brute-force answer could fail on a plan that is merely near the best.

**`build(season)`, added.** This is the model, and the page leaves its code to the practice. It
takes a `Season` and returns the MathOpt model with its variables, written the way *The Model* above
reads:

- one binary $`x_c`$ per circuit, named `x_<cid>` and keyed in the returned dictionary by the
  circuit id (`x_C07` under `"C07"`);
- the row (budget), named `budget`: the summed $`\text{cost}_c \, x_c`$ of all circuits at most the
  season's `budget`;
- the objective: maximize the summed $`\text{risk}_c \, x_c`$.

Lesson 4.2.1 has every call it needs: `mathopt.Model(name=...)`, `add_binary_variable(name=...)`,
`add_linear_constraint(expression <= bound, name=...)` and `maximize`. The snapshot names the model
`trim_<season name>`.

Building and solving are separate functions on purpose. A test or a lesson program can build the
model and look at it (its variables, its rows) without solving it, and the next lessons change the
model in `build` while `make_plan` stays a reader of results.

**`make_plan(season)`, before and after.** Before, it returned `Plan("NOT_SOLVED")`. After, it solves
and turns the solver's answer into the plan's terms:

<!-- snapshot: steps/01/vegcrew/planner.py -->
```python
def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim this year: the most risk removed within the budget."""
    model, x = build(season)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
    status = STATUS.get(result.termination.reason, result.termination.reason.name)
    if status not in ("OPTIMAL", "FEASIBLE"):
        return Plan(status)
    chosen = [c for c in season.circuits if result.variable_values(x[c.cid]) > 0.5]
    return Plan(status, {c.cid: Trim(c.cid) for c in chosen},
                cost=sum(c.cost for c in chosen), risk_removed=sum(c.risk for c in chosen))
```

Three choices in it are worth naming. A status other than OPTIMAL or FEASIBLE returns an empty plan
with that status, never an exception: "no plan" is an answer the caller must handle (lesson 9.1.1).
A circuit is chosen when its value is above 0.5, not equal to 1, because a MILP solver returns values
within a tolerance of whole numbers (lesson 6.4.1). And the totals are recomputed from the data, not
read from the objective value, so they are exact integers in $k.

## The Plan Beats the Ranking by $8k a Year

`first_plan.py` runs `steps/01` on the small season, then funds the same circuits the spreadsheet
way, by risk per $k down the list:

```text
steps/01:
season small-54: 20 circuits, budget $962k
status OPTIMAL: 9 trims, cost $952k, risk removed $2,114k a year
  C01 River  34 mi  cost $ 179k  risk $ 301k
  C04 River  39 mi  cost $ 150k  risk $ 339k
  C05 River  23 mi  cost $  85k  risk $ 138k
  C06 River  20 mi  cost $  75k  risk $ 143k
  C09 River  23 mi  cost $ 106k  risk $ 251k
  C10 Hills   8 mi  cost $  41k  risk $  89k
  C12 Hills  38 mi  cost $ 136k  risk $ 287k
  C13 River  19 mi  cost $  65k  risk $ 161k
  C17 Hills  36 mi  cost $ 115k  risk $ 405k
ranking by risk per $k: 9 trims, cost $936k, risk removed $2,106k a year
in the plan, not the ranking: C05
in the ranking, not the plan: C02
model: 20 binary variables, 1 row
```

The two answers differ by one circuit. The ranking takes C02 and stops with $26k unspent; the model
swaps C02 for C05, which costs $16k more, removes $8k a year more, and still fits. `OPTIMAL` says no
set of circuits within $962k removes more than $2,114k a year. On twenty circuits the gap is small;
the point is that the ranking has no way to know whether it is small.

## Four Tests Pin the Requirement Down

A requirement is not done until a test says so. `steps/01` adds `tests/test_planner.py`, with four
tests, each for one thing the manager would check. The first is built by hand so that the right
answer is obvious and the ranking gets it wrong:

<!-- snapshot: steps/01/tests/test_planner.py -->
```python
def test_the_plan_beats_ranking_by_risk_per_dollar():
    # By risk per $k, A (2.0) ranks first; A leaves no room for B and C, which together remove more.
    s = season(100, ("A", 60, 120), ("B", 50, 90), ("C", 50, 90))
    plan = make_plan(s)
    assert plan.status == "OPTIMAL"
    assert sorted(plan.trims) == ["B", "C"]
    assert (plan.cost, plan.risk_removed) == (100, 180)
```

The other three check that the plan never spends more than the budget on the small season; that it
removes as much risk as the best of all $`2^6 = 64`$ subsets of the tiny season, found by brute force
(lesson 1.1.1's method); and that a zero budget is an answer, OPTIMAL with no trims, not an error.
The brute-force test is the strongest of the four: it checks the optimum against an answer computed
without any solver.

`step01.py` runs the new tests against the code before the lesson and after it. Before, every one of
them fails on an assertion, which is what a practice starting from `steps/00` needs: the tests run,
and they say what is missing.

```text
tests added by lesson 14.1.1: 4
against steps/00 (before):
  FAILED test_planner::test_a_zero_budget_is_an_answer_with_no_trims  AssertionError: assert ('NOT_SOLVED', {}) == ('OPTIMAL', {})
  FAILED test_planner::test_the_plan_beats_ranking_by_risk_per_dollar  AssertionError: assert 'NOT_SOLVED' == 'OPTIMAL'
  FAILED test_planner::test_the_plan_matches_every_subset_of_the_tiny_season  AssertionError: assert 0 == 355
  FAILED test_planner::test_the_plan_never_spends_more_than_the_budget  AssertionError: assert ('NOT_SOLVED' == 'OPTIMAL'
  ...and 3 of 3 earlier tests pass
against steps/01 (after): 7 of 7 pass
```

## The Step Added One Function and Kept Every Other File

```text
code, steps/00 -> steps/01 (lines, functions; blanks and comments left out):
  __init__.py     4   0  ->    4   0
  __main__.py    16   1  ->   16   1
  data.py        22   2  ->   23   2  changed
  generate.py    26   2  ->   26   2
  planner.py     18   1  ->   35   2  changed
  report.py      12   1  ->   12   1
  package        98   7  ->  116   8
  tests          18   3  ->   48   7  (lines, tests)
```

Seventeen lines of planner, one new function, and the tests grew by more than the code did (30 lines
against 18). That ratio is normal for a model: the model is short, and the tests are where you say
what "right" means. `data.py`'s one extra line is the stub for the lesson *Crews and months: capacity over time*. The style is set here
for the rest of the module: frozen dataclasses for data, a `build` that mirrors the formulation, and
a `make_plan` that turns solver output into the plan's words.

**Practice.** This lesson's project practice starts from the whole package as `steps/00` left it.
Submit grades it with the practice's own `tests/` (the tests of `steps/01`) and checks that `main.py`,
which plans the tiny season, prints the practice's `expected/report.txt`.

<!-- practice 1 -->

## Summary

- **The starting code loads a season and plans nothing.** The plan's shape (`Plan`, `Trim`) is fixed
  before the model, so the model can change behind it.
- **A budget and yes-or-no choices make a 0-1 knapsack.** A MILP was chosen over a ranking and over
  dynamic programming because later requirements add rows, not algorithms.
- **The plan beats the ranking.** On the small season the model removes $2,114k a year against the
  ranking's $2,106k, and proves no set does better.
- **Four tests pin the requirement down,** and each fails on an assertion against `steps/00`.

## Reference

| Item | In the code |
| --- | --- |
| $`x_c \in \{0,1\}`$ | `x[c.cid]`, `add_binary_variable(name=f"x_{c.cid}")` |
| budget row | `add_linear_constraint(... <= season.budget, name="budget")` |
| objective | `model.maximize(sum(c.risk * x[c.cid] ...))` |
| exact optimum | `SolveParameters(relative_gap_tolerance=0.0)` |
| a trim is chosen | `result.variable_values(x[c.cid]) > 0.5` |

| Command, inside a snapshot | What it does |
| --- | --- |
| `python -m pytest` | runs the snapshot's tests |
| `python -m vegcrew small` | plans the generated small season and prints the plan |

**Further reading:** [ortools 9.15.6755 on PyPI](https://pypi.org/project/ortools/9.15.6755/) (the
release the course pins; this lesson's MathOpt calls were checked against the docstrings of its
`ortools.math_opt.python` package, read in the runner: `mathopt.solve` and its parameters, and
`fast_sum`, which the lesson *Crews and months: capacity over time* uses); lesson [6.3.1](../25-knapsack-and-assignment/README_6.3.1.md)
(the knapsack, its dynamic program and why no single ratio ranks items) and lesson
[4.2.1](../13-mathopt-core/README_4.2.1.md) (a MathOpt model's parts).

## Challenges

1. The manager adds "at least one circuit in every region". Write the rows, then the test that would
   fail without them.
2. Change `EXACT` to the default gap and run the brute-force test a few times on other seeds. Does it
   ever fail? Why could it?
3. Rank by risk per $k, but after the ranking stops, try swapping one funded circuit for one unfunded
   one. Does that close the gap on the small season?

## Design Note: Fix the Answer's Shape Before the Model

The skeleton fixed `Plan` before there was a model. Every later lesson changes the model: a month index,
then CP-SAT intervals, then a new objective. The report, the tests and, in the lesson *From script to service, and what the code became*, an HTTP API
read plans only through `Plan` and `Trim`, so most of those changes stay inside one file. When a field
must be added (a crew, a start week), it is added to the plan, and everything that does not need it
keeps working. A model's variables are an implementation detail; a plan is the contract.

## The Full Programs

Each output above was printed by one of these programs, run from the module's `src/` folder. They
import the project from a chosen snapshot with `snapshots.use`, so one program can compare two steps.

**first_plan.py.** Plans the small season with `steps/00` and `steps/01` and compares the plan with a
ranking by risk per $k (*The Plan Beats the Ranking by $8k a Year*). *Try:* Plan the medium season.
Predict whether the ranking's shortfall grows.

- Program: [first_plan.py](src/first_plan.py)

**step01.py.** Runs the tests this lesson adds against `steps/00` and `steps/01`, and counts the code
of both (*Four Tests Pin the Requirement Down*). *Try:* Break `build` in `steps/01` by turning `<=`
into `>=` on a copy, and predict which tests fail.

- Program: [step01.py](src/step01.py)

**snapshots.py.** The helpers every program of this module uses: import a snapshot, run one
snapshot's tests on another's code, count lines and functions.

- Library: [snapshots.py](src/snapshots.py)
