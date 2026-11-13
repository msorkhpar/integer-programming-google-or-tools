# 14.2.3 Business Rules: Must-Dos, Bundles, Parents and Alternatives

The planners checked the step-02 plan against their own lists and wrote back:

> Three must-do projects are missing: P010, P017 and P039 are regulatory commitments, so they go in
> whatever they're worth. P030 and P031 are two ways to fix the same Valley line, and you funded
> both. Also, P023 can only start a year after P022 has started, P016 needs P015, and P011 and P012
> are one Coast crew visit: both or neither. The export has all of this in its columns.

## The Step-02 Plan Breaks Four Rules the Export Already Holds

The export always had the columns `must_do`, `alt_group`, `parent`, `parent_lag` and `bundle`. The
step-02 loader never read them, so the model could not keep rules it had never heard of.
`business_rules.py` checks the step-02 plan of GridCap small (a fictional utility) against those
columns, using the export alone:

```text
step 02 plan: value $29,027k, 4 rules broken
  must-do P010 not funded
  must-do P017 not funded
  must-do P039 not funded
  alternatives G030: P030 and P031 both funded
```

The parent and bundle rules happen to hold in this plan. They hold by luck, which is no guarantee
for the next export.

## Each Rule Is a Function That Adds Rows With the Names It Owns

So far `build` wrote its two row families inline. Five more would make it a long function in which
every rule edits the same lines. The design choices:

| Choice | For | Against |
| --- | --- | --- |
| keep writing rows inline in `build` | everything in one place | `build` grows with every rule; the rule's rows and its name scheme are far apart |
| one class per rule with `apply` and `check` methods | each rule can also check a plan | a class hierarchy for what are, today, five loops |
| one function per rule in `rules.py`, listed in `RULES` (chosen) | a rule is read in one place; a new rule is a new function, and `build` stays the same | the order of `RULES` matters only for row order, which a reader might think matters for meaning |

Each rule function receives `built` and adds rows through `built.add(name, row)`. The rule owns its
name prefix (`must_`, `alt_`, `bundle_`, `after_`), and that prefix is what the diagnostics of
the lesson *Why it failed, why it was deferred: a diagnostics layer* will turn back into planner language.

Row order carries no meaning, but order is not always invisible: when several plans tie for the
best value, which one HiGHS returns can depend on how the model was built. The section *The Rules
Cost $2,919k of Value and Break Nothing* measures that on the demo export.

## The Model

The model of the lesson *Many years: start years, windows and cash-flow spreading* with section 6's rules added. Helper sums keep the rows short:
$`\text{started}(i) = \sum_{t \in T_i} x_{i,t}`$ is 1 if project $`i`$ is funded, and
$`\text{started\_by}(i, t) = \sum_{u \in T_i,\, u \le t} x_{i,u}`$ is 1 if it has started by
year $`t`$ (both from lesson 6.5.2).

**Sets.** $`P`$, $`Y`$, $`T_i`$ as before; $`M \subseteq P`$, the must-do projects;
$`\mathcal{G}`$, the alternative groups, each a set of projects; $`\mathcal{B}`$, the bundles, each
a set of projects whose first member by id is $`b_1`$; $`C \subseteq P`$, the child projects, with
parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`c_{i,k}`$, $`v_i`$, $`B_y`$ as before ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} v_i\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \quad \leftarrow \text{new} \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \quad \leftarrow \text{new} \\
\text{started}(j) - \text{started}(b_1) &= 0 && \forall B \in \mathcal{B},\ j \in B \setminus \{b_1\} && \text{(bundle}_{b_1,j}) \quad \leftarrow \text{new} \\
\text{started\_by}(c, t) - \text{started\_by}(p(c), t - L_c) &\le 0 && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \quad \leftarrow \text{new} \\
\sum_{i \in P} \sum_{t \in T_i,\; t \le y < t + d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The parent row is the cumulative form of lesson 6.4.3: a child started by year $`t`$ needs its
parent started by $`t - L_c`$. If the parent's window has no year that early, the right side is an
empty sum, the row says $`\text{started\_by}(c, t) \le 0`$, and the child cannot start in $`t`$.
Each rule comes from section 6: must-dos from lesson 6.5.1, bundles and parents from lesson 6.5.2,
alternatives from lesson 6.5.3, lags from lesson 6.5.4.

## The Change, File by File

**`cipt/rules.py`** is new. The two files now import each other: `model.py` imports `RULES` from
`rules.py` to run them, and `rules.py` names `Built` in every rule's signature. Two imports at
module level would be circular: whichever file Python loads first would ask for a name the other has
not defined yet. `rules.py` breaks the circle by importing `Built` only for type checkers. With
`from __future__ import annotations`, a signature's types are kept as text and never evaluated when
the module runs, and `typing.TYPE_CHECKING` is `False` at run time, so the import inside the `if`
never runs; a type checker or an editor still reads it. The head of `steps/03/cipt/rules.py`:

<!-- snapshot: steps/03/cipt/rules.py -->
```python
from __future__ import annotations

from typing import TYPE_CHECKING

from ortools.math_opt.python import mathopt

if TYPE_CHECKING:
    from .model import Built
```

One of its five rules, from `steps/03/cipt/rules.py`, shows the shape every rule has:

<!-- snapshot: steps/03/cipt/rules.py -->
```python
def once_or_must(built: Built) -> None:
    """(once_i) a project starts at most once; (must_i) a must-do starts exactly once."""
    for p in built.request.projects:
        if p.must_do:
            built.add(f"must_{p.project_id}", built.started(p.project_id) == 1)
        else:
            built.add(f"once_{p.project_id}", built.started(p.project_id) <= 1)
```

The other rules are the practice's, and the one that carries this lesson's hardest row is
`parents`, the row $`\text{after}_{c,t}`$ of the model above. For every project $`c`$ whose
`parent` is set (it is `None` for a project with no parent), and for every start year $`t`$ of the
child's own window, `request.starts(c)`, it adds one row named `after_<child>_<t>`: the child's
$`\text{started\_by}(c, t)`$ minus the parent's $`\text{started\_by}(p(c), t - L_c)`$, at most 0.
The parent's record is `request.project(c.parent)` and the lag $`L_c`$ is `c.parent_lag`. The
rows run over the child's window, not the parent's, and a row is added for every such $`t`$, even
when the parent's side is the empty sum the paragraph under the model describes: that row is what
stops the child from starting in $`t`$.

The bundle row is written as a difference equal to zero rather than `started(j) == started(first)`:
both sides of `==` would be expressions, and keeping one side a number makes every row of the model
read "expression, bound". The budget rule moved here too, so every row of the model is made in this
one file, `steps/03/cipt/rules.py`:

<!-- snapshot: steps/03/cipt/rules.py -->
```python
RULES = (once_or_must, alternatives, bundles, parents, budgets)
```

**`cipt/model.py`.** Before (step 02), `build` held the `once` and `budget` loops. After, it runs
the rules, and `Built` gained the helpers the rules share: `add`, and `started_by` beside the
`started` of step 02. From `steps/03/cipt/model.py`:

<!-- snapshot: steps/03/cipt/model.py -->
```python
    def add(self, name: str, row) -> None:
        """Add one named row; the name is how reports and diagnostics refer to it."""
        self.rows[name] = self.model.add_linear_constraint(row, name=name)

    def started(self, pid: str) -> mathopt.LinearSum:
        """1 if project `pid` starts in some year of its window, else 0."""
        return mathopt.fast_sum(v for (p, _), v in self.x.items() if p == pid)

    def started_by(self, pid: str, year: int) -> mathopt.LinearSum:
        """1 if project `pid` starts in `year` or earlier, else 0."""
        return mathopt.fast_sum(v for (p, t), v in self.x.items() if p == pid and t <= year)
```

`started_by` keeps only the start variables of years up to `year`. When none is that early, the
sum is empty, and `fast_sum` of nothing is an expression equal to 0, which is the empty parent side
of an `after` row.

<!-- snapshot: steps/03/cipt/model.py -->
```python
    built = Built(request, model, x)
    for rule in RULES:
        rule(built)
```

`spend_by_year` moved from a module function into a method of `Built`, because the budget rule
now needs it through `built`, like every other rule.

**`cipt/data.py`.** `Project` gains five fields, all with defaults, so tests that build a `Project`
by hand still work. The loader reads the five columns and refuses one new kind of bad export. From
`steps/03/cipt/data.py`:

<!-- snapshot: steps/03/cipt/data.py -->
```python
    for p in projects:
        if p.parent is not None and p.parent not in ids:
            raise ValueError(f"{p.project_id} names an unknown parent {p.parent}")
```

Without that check, `request.project(c.parent)` would raise a `KeyError` deep inside `parents`,
and the planner would read a stack trace instead of a sentence. `Request.groups(column)` collects
the members of each alternative group or bundle, sorted, so the row names come out the same on
every run.

**`cipt/value.py`** is new and is a stub: `annual_pof` and `risk_reduction` return 0.0. It is there
so the practice of the next lesson starts from code that imports; the lesson *Value: NPV by start year and risk reduction* writes it.
No code of this step imports it, and in this lesson's practice it is already this stub: it is not
part of the task.

## The Rules Cost $2,919k of Value and Break Nothing

```text
step 03 rows: after 2, alt 2, budget 5, bundle 1, must 4, once 36
step 03 plan: value $26,108k, 0 rules broken, 24 projects funded
```

The value fell from $29,027k to $26,108k: the must-dos take money the model would have spent
elsewhere, and only one Valley alternative is funded. That $2,919k is what the rules cost, and
it is the honest number: the step-02 value was for a plan the planners could not use.

On the demo export, the plan changed in the same ways: P002, the must-do, is in; only one of the
alternatives P006 and P007 is funded; and P004, whose parent P003 is not funded, is out.

```text
$ python -m cipt data/demo.json    # steps/03
GridCap tiny: optimal
funded 5 of 8 projects, capex $6,000k of $7,890k, value $2,782k
  2027  spend $1,120k of $2,300k
  2028  spend $2,730k of $3,280k
  2029  spend $2,150k of $2,310k
  P001  start 2029  capex  2,150  value  1,386  Ridge substation transformer replace (A001)
  P002  start 2028  capex  2,730  value    871  Valley 115 kV line rebuild (A002)
  P005  start 2027  capex    250  value    123  Ridge circuit trim (A005)
  P007  start 2027  capex    290  value    265  Valley substation transformer repair (A006)
  P008  start 2027  capex    580  value    137  Plains corridor widen (A008)
```

This plan is one of several with the same value. The value still ignores the start year, so P007
can start in 2027 or 2028 for the same $2,782k, and HiGHS returns one of them. Which one can depend
on how the model was built. `business_rules.py` plans the demo export with every order of `RULES`,
then with each project's start variables created latest year first:

```text
demo, every one of the 120 orders of RULES: 1 plan
demo, start variables made latest year first: value $2,782k -> $2,782k, P007 2027 -> 2028
```

On this export the order of the rows changed nothing, but the order of the variables moved P007 to
the other tied year. The expected report of this lesson's practice is the plan the reference's
order gives: start variables created project by project, each project's years in ascending order,
and the rules run in the order of `RULES`. A correct model built in another order can print a
different tied plan.

## A Rule's Test Uses Data Where the Old Plan Breaks That Rule

A test that a must-do is funded proves nothing if the must-do would have been funded anyway. Each
test of `steps/03/tests/test_rules.py` builds an export where the best plan without the rule
breaks it, so the test can only pass if the rule is there:

<!-- snapshot: steps/03/tests/test_rules.py -->
```python
def test_child_starts_a_lag_after_its_parent():
    raw = export([row("P", (50,), 10), row("C", (50,), 100, latest=2028, parent="P", lag=1),
                  row("D", (50,), 60, earliest=2028)], years=TWO, budget={2027: 50, 2028: 50})
    assert solve(load_request(raw)).starts == {"P": 2027, "C": 2028}
```

Without the rule, C (worth 100) starts in 2027 and D fills 2028, for 160. With it, C must wait a
year for P, and the best plan is P then C, for 110. The ledger shows each test's answer from the
step-02 code:

```text
14.2.3: 8 tests added; on step 02, 8 fail on an assertion; on step 03, 22 of 22 pass
  test_must_do_is_funded_even_at_low_value
    before: assert ('B',) == ('A',)
    after:  passed
  test_alternatives_fund_at_most_one
    before: assert ('A', 'B') == ('A',)
    after:  passed
  test_bundle_is_all_or_nothing
    before: assert ('A', 'C') == ('A', 'B')
    after:  passed
  test_child_starts_a_lag_after_its_parent
    before: assert {'C': 2027, 'D': 2028} == {'P': 2027, 'C': 2028}
    after:  passed
  test_child_is_not_funded_without_its_parent
    before: assert 'C' not in ('C',)
    after:  passed
  test_must_dos_beyond_the_budget_are_infeasible
    before: assert 'optimal' == 'infeasible'
    after:  passed
  test_every_rule_has_a_named_row
    before: assert {'after_F_202..._D', 'must_A'} <= {'budget_2027...'once_D', ...}
    after:  passed
  test_refuses_an_unknown_parent
    before: Failed: DID NOT RAISE ValueError
    after:  passed
```

`test_must_dos_beyond_the_budget_are_infeasible` is the first test whose right answer is "no
plan". Must-dos can ask for more than the money there is, and the planner must say so rather than
quietly drop one. Saying *which* rules clash is the lesson *Why it failed, why it was deferred: a diagnostics layer*.

## The Rules Moved Into Their Own File and `build` Got Shorter

```text
14.2.3: steps/02 -> steps/03
  package lines 192 -> 265, functions 17 -> 27, tests 14 -> 22
  most branches: report.render (6) -> data.load_request (8)
  data.py        65 ->   85
  model.py       36 ->   38
  rules.py        0 ->   42
  value.py        0 ->    9
```

Five rules added 42 lines in `rules.py` and 2 in `model.py`. The function with the most branches is
now the loader, which reads and checks more columns; no rule function has more than two loops. The
nine lines of `value.py` are the stub for the lesson *Value: NPV by start year and risk reduction*.

**Practice.** This lesson's project practice starts from `steps/02`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds.

<!-- practice 1 -->

## Summary

- **The step-02 plan breaks four rules the export already holds**: three must-dos missing, one
  pair of alternatives both funded.
- **Each rule is a function that adds rows with the names it owns.** `build` runs `RULES` and no
  longer changes when a rule is added.
- **The rules cost $2,919k of value and break nothing** on GridCap small.
- **A rule's test uses data where the old plan breaks that rule**, so it fails without the rule.

## Reference

| Row | Rule | Lesson |
| --- | --- | --- |
| `once_P001` | a project starts at most once | 6.4.1 |
| `must_P017` | a must-do starts exactly once | 6.5.1 |
| `alt_G030` | at most one project of an alternative group | 6.5.3 |
| `bundle_P011_P012` | members funded together or not at all | 6.5.2 |
| `after_P023_2029` | a child started by 2029 needs its parent started by 2029 minus the lag | 6.5.2, 6.5.4 |
| `budget_2027` | the year's spend within its budget | 6.4.2 |

**Further reading:** [MathOpt `model.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (`add_linear_constraint` takes a bounded expression and a name); [MathOpt `expressions.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/expressions.py) (`fast_sum` on an empty list, which is what an `after` row's parent side is when the parent cannot start early enough).

## Challenges

1. A bundle whose members must also start in the same year: which rows does lesson 6.5.2 add, and
   which function of `rules.py` would you change?
2. The planners add a child with two parents, both needed. What changes in the export, the loader
   and `parents`?
3. Change the order of `RULES`. Which tests still pass, and does the plan change?

## Design Note: Rules as a List of Functions

`RULES` is a plain tuple. A registry with decorators, or plugins found by name, would let a rule be
added without editing `rules.py`. That flexibility has no user here: every rule is reviewed with the
planners and lives in this one file, where a reader can see all of them. The tuple is enough until
someone needs to switch rules on and off per scenario, and the lesson *Scenarios, overrides and snapshots* shows that even then a
scenario changes data, not the list of rules.

## The Full Programs

**business_rules.py.** Checks the step-02 plan of GridCap small against the export's rule columns,
then counts the step-03 rows and checks its plan the same way (*The Step-02 Plan Breaks Four
Rules*, *The Rules Cost $2,919k*). *Try:* set P010's `must_do` to false in the export and predict
whether the value goes up, and by how much at most.

- Program: [business_rules.py](src/business_rules.py)

**cli_demo.py, ledger.py, code_size.py.** The demo run, the test ledger and the size table for
step 03.

- Program: [cli_demo.py](src/cli_demo.py)
- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
