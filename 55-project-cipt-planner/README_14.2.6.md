# 14.2.6 Why It Failed, Why It Was Deferred: A Diagnostics Layer

Two messages arrived the same week. From finance, after trying a budget cut:

> We cut 2030 and 2031 to $4M each and the planner just said "infeasible". Infeasible why? Which of
> our numbers is the problem?

And from a regional manager:

> P030 is our biggest Valley project and it's not funded. Why not? What would it take?

## "Infeasible" Names No Rule, and "Not Funded" Has No Reason

`steps/05` returns a `Plan` with `status="infeasible"` and nothing else. The solver knows only that
no assignment satisfies every row; it does not say which rows clash (lesson 9.1.1). For a deferred
project the plan says nothing either: the project's variables are 0, and the reason lies in the
rows, the objective and every other project at once.

What the code does have, since the lesson *Business rules: must-dos, bundles, parents and alternatives*, is a name for every row, and names the planners can
read: `must_P017`, `budget_2030`. A diagnostics layer can work in those names.

## Relax One Named Row at a Time to Find the Rows That Clash

For "why infeasible", three tools from section 9 were candidates:

| Tool | For | Against |
| --- | --- | --- |
| MathOpt's `compute_infeasible_subsystem` | one call | in MathOpt only Gurobi offers it; HiGHS, the planner's solver, refuses it (lessons 4.3.5 and 9.1.3) |
| elastic rows with penalized slack (lesson 9.1.4) | one solve; says how much to change | needs a slack variable per row and a choice of penalties; answers "how much", not "which" |
| a deletion filter over named rows (lesson 9.1.3) (chosen) | works with any solver; returns an irreducible set: every row in it is needed for the clash | one solve per row |

A **deletion filter** goes through the rows in name order. It relaxes a row (sets its bounds to
$`-\infty`$ and $`+\infty`$) and solves. If the model is still infeasible, that row was not needed for
the clash, and it stays relaxed. If the model becomes feasible, the row is part of the clash, and
its bounds are restored. At the end the unrelaxed rows form an **irreducible infeasible set**:
together they have no plan, and without any one of them a plan exists. On GridCap small that is up
to 50 solves of a small model.

For "why deferred", the answer is lesson 9.3.2: force the project in and solve again. If a plan
exists, its NPV loss is the project's price, and the projects it pushes out are the trade. If no
plan exists, the deletion filter runs on the forced model, with the forcing row kept, and names the
rules that block the project.

## The Model

The planning model is the model of the lesson *Two goals: risk against NPV*, unchanged. Diagnostics solve variants of it.

**Sets, parameters, variables, rows.** As in the lesson *Two goals: risk against NPV*: rows `once`, `must`, `alt`, `bundle`,
`after`, `budget` and, when set, `risk_floor`. Write $`R`$ for the set of row names.

**The relaxed model of the deletion filter.** For a set $`D \subseteq R`$ of relaxed rows, the
model keeps every row in $`R \setminus D`$ and drops the rows in $`D`$. The filter keeps a row
$`\rho`$ in $`D`$ exactly when the model without $`D \cup \{\rho\}`$ is still infeasible:

```math
\begin{aligned}
&D \leftarrow \emptyset \\
&\text{for each } \rho \in R \text{ in name order:} \quad \text{if } \text{infeasible}(R \setminus (D \cup \{\rho\})) \text{ then } D \leftarrow D \cup \{\rho\} \\
&\text{conflict} = R \setminus D
\end{aligned}
```

**The forced model of "why deferred".** The planning model with one row more, for the project
$`j`$ asked about, and the objective $`\max \text{NPV}(x)`$:

```math
\begin{aligned}
\text{started}(j) &= 1 && && \text{(force}_j) \quad \leftarrow \text{new}
\end{aligned}
```

The price of $`j`$ is the base plan's NPV minus the forced plan's NPV.

## The Change, File by File

**`cipt/diagnose.py`.** Before: the stub of the lesson *Two goals: risk against NPV*, `why_infeasible` returning `None`. After,
the filter, `deletion_filter(built, keep=())`, whose code the page leaves to the practice. It is
the loop of the model block above, run on the rows of `built.rows`:

- It goes through the row names in sorted order. A row named in `keep` is never relaxed; the
  forcing row of "why deferred" below is passed that way.
- To relax a row, it saves the row's two bounds, then sets them to $`-\infty`$ and $`+\infty`$
  (`-math.inf` and `math.inf`). If the model is now feasible, the row is needed for the clash, and
  its saved bounds go back. If the model is still infeasible, the row stays relaxed: it joins
  $`D`$.
- It returns, sorted, the names of the rows that are not relaxed at the end: the conflict
  $`R \setminus D`$, with any rows of `keep` among them.

Relaxing changes the row's bounds in place; MathOpt's `LinearConstraint` has setters for
`lower_bound` and `upper_bound`, so the model is never rebuilt. `feasible` is one solve and one
comparison, from `steps/06/cipt/diagnose.py`:

<!-- snapshot: steps/06/cipt/diagnose.py -->
```python
def feasible(built: Built) -> bool:
    return run_highs(built.model).termination.reason.name != "INFEASIBLE"
```

Only the termination `INFEASIBLE` counts as "no plan". MathOpt also has
`INFEASIBLE_OR_UNBOUNDED`, for a solver that proved one of the two without saying which, and
`feasible` counts it as feasible. Every variable of the planner is binary, so its models can never
be unbounded, and every infeasible request on this page and in the tests ended `INFEASIBLE`. The rows dictionary that the lesson
*The first request: fund projects within one budget* started keeping "for later" is what lets the filter fit in eight lines.

`describe` turns a row name back into the planners' words, one branch per name prefix. From
`steps/06/cipt/diagnose.py`:

<!-- snapshot: steps/06/cipt/diagnose.py -->
```python
def describe(request: Request, name: str) -> str:
    """One row, in the planners' words."""
    kind, _, rest = name.partition("_")
    if kind == "budget":
        return f"spend in {rest} within ${request.budget[int(rest)]:,}k"
    if kind == "must":
        return f"{rest} is a must-do"
    if kind == "force":
        return f"{rest} is forced in"
    if kind == "alt":
        return f"at most one of {', '.join(request.groups('alt_group')[rest])}"
    if kind == "bundle":
        return f"{' and '.join(rest.split('_'))} are funded together or not at all"
    if kind == "after":
        child, year = rest.split("_")
        c = request.project(child)
        return f"{child} started by {year} needs {c.parent} started by {int(year) - c.parent_lag}"
    if kind == "risk":
        return f"remove at least ${request.risk_floor:,.1f}k of risk"
    return name
```

`name.partition("_")` splits at the first underscore, so `risk_floor` is the kind `risk`. An
alternative group is listed by its members, in id order, joined by a comma and a space
(`at most one of P030, P031`); the risk floor is stated in $k with one decimal and thousands commas
(`remove at least $<floor>k of risk`); a name with a prefix it does not know comes back as it is.

`why_deferred` adds the forcing row and either prices the project or explains it:

<!-- snapshot: steps/06/cipt/diagnose.py -->
```python
    built = build(request)
    built.add(f"force_{project_id}", built.started(project_id) == 1)
    forced = solve_built(built)
    if forced.status == "infeasible":
        rows = deletion_filter(built, keep=(f"force_{project_id}",))
        return Deferral(project_id, math.inf, (), explain(request, rows))
    displaced = tuple(p for p in plan.funded if p not in forced.starts)
    return Deferral(project_id, plan.npv - forced.npv, displaced, None)
```

The forcing row is kept, because the question is "which rules stop *this* project", not "is the
model feasible without forcing it", which it is.

**`cipt/__main__.py`.** The command line prints the conflict when the plan is infeasible and gains
`--why PROJECT`, which prints the price or the blocking rules of a project the plan left out. From
`steps/06/cipt/__main__.py`:

<!-- snapshot: steps/06/cipt/__main__.py -->
```python
    plan = solve(request)
    print(render(request, plan))
    if plan.status == "infeasible":
        print(why_infeasible(request).message)
        return 1
    if args.why and args.why not in plan.starts:
        d = why_deferred(request, plan, args.why)
        if d.conflict:
            print(f"{args.why} cannot be funded. {d.conflict.message}")
        else:
            print(f"Funding {args.why} costs ${d.npv_cost:,.0f}k of NPV and drops {', '.join(d.displaced) or 'nothing'}.")
    return 0
```

For a project the plan already funds, `--why` prints nothing after the report: there is no
deferral to explain. For an infeasible request, the conflict is printed, `--why` is not answered,
and the command returns 1.

**`cipt/scenario.py` and `cipt/store.py`** are new and are stubs for the lesson *Scenarios, overrides and snapshots*.
No code of this step imports them, and in this lesson's practice they are already these stubs.

## The Messages Name the Rules and the Numbers

`diagnose_small.py` asks both questions on GridCap small (a fictional utility). Finance's cut:

```text
budgets cut: infeasible, 50 rows
No plan meets these 3 rules together; drop or change any one of them:
  budget_2030: spend in 2030 within $4,000k
  budget_2031: spend in 2031 within $4,000k
  must_P017: P017 is a must-do
```

Of 50 rows, three clash. P017, a $5,310k must-do whose window is 2030 to 2031, cannot fit in either
year at $4,000k. The message also says what finance can change: either budget, or the must-do
status.

The regional manager's question, and a second project for comparison:

```text
P030: funding it costs $870k of NPV and drops P001, P005, P016, P028, P031
P040: funding it costs $467k of NPV and drops P005, P016
```

These two lines are `diagnose_small.py`'s own summary of each `Deferral`, one line per project so
the two can be compared. The command line words the same `Deferral` as a sentence instead, in the
format of `__main__.py` above: `Funding <id> costs $<cost>k of NPV and drops <ids>.`, with
`nothing` when it drops no project.

P030 is worth funding only at the cost of five other projects and $870k of NPV, P031 among them:
P030 and P031 are alternatives, so funding one drops the other. Then the engineers lengthen
P023's lag after its parent P022 to three years, and the manager asks about P023:

```text
P023 with a three-year lag: cannot be funded. No plan meets these 2 rules together; drop or change any one of them:
  after_P023_2029: P023 started by 2029 needs P022 started by 2026
  force_P023: P023 is forced in
```

The plan starts in 2027, so no plan can have P022 started by 2026. On the demo export, the command
line gives the same kind of answer for P003:

```text
$ python -m cipt data/demo.json --why P003    # steps/06
```

```text
P003 cannot be funded. No plan meets these 4 rules together; drop or change any one of them:
  budget_2028: spend in 2028 within $3,280k
  budget_2029: spend in 2029 within $2,310k
  force_P003: P003 is forced in
  must_P002: P002 is a must-do
```

P003 spends $980k and $1,490k in 2027 and 2028. The must-do P002 needs $2,730k in 2028 or 2029;
2029's $2,310k is too small for it, so it lands in 2028 beside P003, and 2028 cannot hold both. The conflict is irreducible: drop either budget row or the must-do
and P003 fits.

## Each Diagnostic Test Checks the Exact Set of Rows

From `steps/06/tests/test_diagnose.py`:

<!-- snapshot: steps/06/tests/test_diagnose.py -->
```python
def test_conflict_leaves_out_rules_that_do_not_clash():
    raw = export([row("A", (100,), 5, must_do=True), row("B", (10,), 5, latest=2028, alt_group="G"),
                  row("C", (10,), 5, latest=2028, alt_group="G")], years=TWO, budget={2027: 50, 2028: 1000})
    conflict = why_infeasible(load_request(raw))
    assert (conflict.rows if conflict else None) == ["budget_2027", "must_A"]
```

A test that only asked "does the conflict mention the budget" would pass on a filter that relaxed
nothing and returned all rows. Checking the exact set checks that the set is irreducible.

```text
14.2.6: 8 tests added; on step 05, 8 fail on an assertion; on step 06, 41 of 41 pass
  test_conflict_names_the_clashing_rules
    before: assert None == ['budget_2027', 'must_A', 'must_B']
    after:  passed
  test_conflict_leaves_out_rules_that_do_not_clash
    before: assert None == ['budget_2027', 'must_A']
    after:  passed
  test_message_states_each_rule_in_planners_words
    before: assert '  must_A: A is a must-do' in ''
    after:  passed
  test_deferral_prices_forcing_a_project_in
    before: assert (0.0, (), None) == (100, ('A',), None)
    after:  passed
  test_deferral_names_the_rows_that_block_it
    before: assert None == ['after_B_2027', 'force_B']
    after:  passed
  test_command_line_explains_an_infeasible_request
    before: assert 'No plan meets these 3 rules together' in 'test: infeasible\nfunded 0 of 5 projec
    after:  passed
  test_message_words_alternatives_and_the_risk_floor
    before: assert '  alt_G: at most one of A, B' in ''
    after:  passed
  test_why_adds_nothing_for_a_funded_project
    before: assert (2, '') == (0, 'test: op... project A\n')
    after:  passed
```

The last "before" is the step-05 command line refusing an option it does not have yet: it exits
with status 2 and prints nothing, while `--why A` on a funded project must print exactly the report
the command prints without it.

## Diagnostics Were the Largest Step So Far, and Changed No Model Code

```text
14.2.6: steps/05 -> steps/06
  package lines 390 -> 516, functions 37 -> 49, tests 33 -> 41
  most branches: goals.frontier (10) -> goals.frontier (10)
  __main__.py    15 ->   27
  diagnose.py    20 ->   76
  scenario.py     0 ->   24
  store.py        0 ->   34
```

Of the 126 new lines, 58 are the stubs of the next lesson; the diagnostics themselves are 56 lines
in `diagnose.py` and 12 in the command line. `model.py`, `rules.py` and `solve.py` did not change:
the layer is built entirely on the row names and the `Built` handles earlier steps put in place.
`describe` is a chain of `if` branches, one per row prefix; each new rule must add one, and the
next lesson does.

**Practice.** This lesson's project practice starts from `steps/05`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds. This step's `main.py` also asks
why P003 is not in the demo plan, as `--why P003` does: after the report it prints
`P003 cannot be funded. ` followed by the conflict message, whose first line is
`No plan meets these <n> rules together; drop or change any one of them:` and whose next lines are
`  <row>: <description>`, one per row in name order; the frontier section of the lesson before
follows.

<!-- practice 1 -->

## Summary

- **"Infeasible" names no rule, and "not funded" has no reason**, until the code works in row
  names.
- **Relax one named row at a time to find the rows that clash.** The deletion filter returns an
  irreducible set, and `describe` puts each row in the planners' words.
- **Force a deferred project in to price it**, or, when that is infeasible, to find the rows that
  block it.
- **Each diagnostic test checks the exact set of rows**, which is what irreducible means.

## Reference

| Name | Meaning |
| --- | --- |
| deletion filter | relax each row in turn; keep it relaxed while still infeasible; the rest clash |
| irreducible infeasible set | rows with no plan together; drop any one and a plan exists |
| `why_infeasible(request)` | `None`, or a `Conflict` with rows and a message |
| `why_deferred(request, plan, pid)` | a `Deferral`: NPV cost and displaced projects, or a conflict |
| `force_P030` | the row $`\text{started}(j) = 1`$ that diagnostics add |

**Further reading:** [MathOpt `linear_constraints.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/linear_constraints.py) (`LinearConstraint.lower_bound` and `upper_bound` are settable, which relaxes a row without rebuilding); [MathOpt `result.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py) (`TerminationReason.INFEASIBLE`, which `feasible` tests); [MathOpt `compute_infeasible_subsystem_result.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/compute_infeasible_subsystem_result.py) (the built-in alternative, for solvers that offer it).

## Challenges

1. The filter goes through rows in name order. Find an infeasible request with two different
   irreducible sets and show that a different order returns the other one.
2. `why_deferred` reports the projects that the forced plan drops but not those it starts in a
   different year. Add the shifted ones, using the plans' `starts`.
3. The filter solves once per row. Sort the rows so the `once` rows come last and count the solves
   that change nothing.

## Design Note: Diagnose in the Names People Can Change

The filter could run over variables and bounds too, and would then sometimes name a variable
bound in its conflict. No planner can act on "x_P017_2030 ≤ 1". Every row the filter can name is
something a person set: a budget, a must-do flag, a lag. That is also why the next lesson writes
scenario overrides as rows instead of bounds.

## The Full Programs

**diagnose_small.py.** A budget cut that makes GridCap small infeasible, then two deferred projects
and one blocked by a longer lag, with `steps/06`. *Try:* cut only 2031 to $4,000k and predict the
conflict before running.

- Program: [diagnose_small.py](src/diagnose_small.py)

**cli_demo.py, ledger.py, code_size.py.** The demo run with `--why`, the test ledger and the size
table for step 06.

- Program: [cli_demo.py](src/cli_demo.py)
- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
