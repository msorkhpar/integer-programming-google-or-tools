# 9.1.2 Validating Inputs Before the Solve

The Budget Lock run of lesson 9.1.1 came back `INFEASIBLE`. Before the team asks a solver *which*
rules clash, a GridCap analyst asks something cheaper: is there a mistake in the input that would
make any model fail? Most infeasible runs in planning work come from the data, not from the model:
a window typed backwards, an extra zero on a cost, a crew count from the wrong spreadsheet, two
alternatives both marked must-do. Each of these can be found by reading the input, with no solve at
all, and named in the planners' own terms. This lesson writes five such checks, plants five errors
to show what each one catches, and runs the checks on the Budget Lock scenario to show what they
cannot catch. GridCap is a fictional utility; none of its numbers are real.

## The Model

The checks look at the model of lesson 9.1.1 (its full formulation is there) and reason about five
of its row families without building them. Here are those rows again, with the data each check reads:

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{i \in P} \sum_{t \in T_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i:\, q(i) = q} \ \sum_{t \in T_i,\ t \le y < t + d_i} m_i\, x_{i,t} &\le K_{q,y} && \forall q \in Q,\ y \in Y && \text{(crews}_{q,y}) \\
\sum_{i:\, r(i) = r} \ \sum_{t \in T_i} \text{capex}_i\, x_{i,t} &\ge \text{floor}_r && \forall r \in R && \text{(floor}_r)
\end{aligned}
```

Two more rows come from the scenario: $`\text{force}_i`$ and $`\text{force}_{i,f_i}`$ ask for a
project in any year or in year $`f_i`$, and $`\text{drop}_i`$ keeps it out. A project is
**required** when it is must-do or forced in. Its possible start years are its window
$`T_i`$, or only $`f_i`$ when the scenario names a year.

## A Solver Says "Infeasible" Even When the Cause Is One Typo

`presolve_checks.py` plants five errors in copies of GridCap small, the way they arrive in real
input, and asks the solver about each:

| Planted error | Rows it breaks |
| --- | --- |
| P017's window typed as 2030 to 2029 | $`\text{must}_{\text{P017}}`$ has no variable left |
| P039's first-year cost typed 11,700 instead of 1,170 | $`\text{must}_{\text{P039}}`$ against every $`\text{budget}_y`$ |
| P003's crew need typed 3 instead of 1 | $`\text{must}_{\text{P003}}`$ against $`\text{crews}_{\text{vegetation},2031}`$ |
| P001 and P002, alternatives, both marked must-do | $`\text{must}_{\text{P001}}`$, $`\text{must}_{\text{P002}}`$, $`\text{alt}_{\text{G001}}`$ |
| Plains floor typed 24,100 instead of 2,410 | $`\text{floor}_{\text{Plains}}`$ |

```python
planted = [
    ("P017 window typed 2030-2029", edit(small, "P017", latest_start=2029), Scenario()),
    ("P039 first-year cost 11,700", edit(small, "P039", cost_profile=(11700, 880)), Scenario()),
    ("P003 crew-months typed 3", edit(small, "P003", crew_months=3), Scenario()),
    ("P001 and P002 both must-do", edit(edit(small, "P002", must_do=True), "P001", must_do=True), Scenario()),
    ("Plains floor typed 24,100", replace(small, region_floor={**small.region_floor, "Plains": 24100}), Scenario()),
]
```

The solver's answer is the same five times: `INFEASIBLE`, and nothing else. It cannot tell a typo
from a real conflict, and the next three lessons (IIS, elastic rows, assumptions) cost one or many
more solves to find the cause. A check that reads the input finds each of these before the solve,
and names it.

The first error deserves a closer look, because the model accepts it without complaint. With an
empty window, P017 has no start variables, so its must-do row sums nothing and asks for that
nothing to equal 1. MathOpt's `fast_sum` of nothing is still a linear expression, so the row is
added and the model is simply infeasible. Python's built-in `sum` of nothing is the number 0, and
`0 == 1` is the Python value `False`, which `add_linear_constraint` refuses with a `TypeError`. So a
row whose sum can be empty is built from `fast_sum`, or from `mathopt.LinearExpression()` as the start
of the sum, or skipped:

```text
fast_sum([]) == 1 : INFEASIBLE
sum([]) == 1      : TypeError, Unsupported type for bounded_expr argument: bool
```

Either way, the real cause is the window, and only a check that reads the window says so.

## Each Check Reads One Project, Group or Region Against One Limit

`checks.py` has five functions, one per cause. Each returns a list of `Problem(check, subject,
detail)` records, so a report can say which check fired, what it is about, and the numbers. The
first helper lists the required projects with the start years each may use, overrides included:

```python
def required(portfolio: Portfolio, scenario: Scenario) -> dict[str, list[int]]:
    """Each required project's possible start years: its window, or the forced year."""
    need = {}
    for p in portfolio.projects:
        if p.must_do or p.project_id in scenario.force_in:
            year = scenario.force_in.get(p.project_id)
            need[p.project_id] = [t for t in p.starts() if year is None or t == year]
    return need
```

The five checks, each in one sentence and with the rows it protects:

| Check | Fires when | Row it protects |
| --- | --- | --- |
| `window` | a required project has no start year whose work ends inside the plan | $`\text{must}_i`$, $`\text{force}_i`$ |
| `budget` | a required project alone overspends some year's budget, in every start year it may use | $`\text{budget}_y`$ |
| `crews` | a required project alone needs more crew-months than its program has, in every start year | $`\text{crews}_{q,y}`$ |
| `group` | an alternative group has two or more required members | $`\text{alt}_g`$ |
| `floor` | a region's floor is above what all its projects together cost | $`\text{floor}_r`$ |

The budget check is typical. For each start year it asks whether some year of the project's work
costs more than that year's budget. Only when every start year fails is there a problem:

```python
        if starts and all(any(amount > budget.get(y, 0) for y, amount in p.spend(t).items()) for t in starts):
            found.append(Problem("budget", pid, f"spends {list(p.cost_profile)} from its start in {starts}; "
                                                f"budgets {[budget.get(t) for t in starts]}"))
```

Here is each planted error with the solver's answer and the checks' answer:

```text
P017 window typed 2030-2029   solver: INFEASIBLE
   window P017   no start year: window 2030-2029, forced None, 1 year(s) of work
P039 first-year cost 11,700   solver: INFEASIBLE
   budget P039   spends [11700, 880] from its start in [2027, 2028, 2029]; budgets [8890, 8120, 8760]
P003 crew-months typed 3      solver: INFEASIBLE
   crews  P003   needs 3 vegetation crew-months a year; [2] in [2031]
P001 and P002 both must-do    solver: INFEASIBLE
   group  G001   at most one of the group may be funded, but ['P001', 'P002'] are all required
Plains floor typed 24,100     solver: INFEASIBLE
   floor  Plains floor $24,100k, but all its projects together cost $12,060k
```

Each check fired exactly once, on its own error, and named the project, group or region with the
numbers that clash. That message is what a planner needs: "P039's first-year cost is 11,700 and no
year's budget is more than 8,890" points straight at the typo. The checks read only the input, and
there are as many of them as there are projects, groups and regions, so they cost far less than a
solve.

## A Check Must Never Refuse a Scenario That Has a Plan

A check that fires on a scenario with a plan is worse than no check: the planners would chase a
problem that does not exist, and soon stop trusting the checks. So every check here is **sound**:
it fires only when the rows it protects cannot all hold, whatever the rest of the plan does. Each
gets this by comparing a *least* demand with a *most* supply:

- `budget` and `crews` look at one required project alone. If that project cannot fit in any
  start year with the whole budget or crew to itself, no plan can fit it.
- `floor` adds the cost of *every* project in the region except those forced out, and ignores the
  alternative groups that would stop some of them being funded together. That total is more than
  any plan can spend in the region, so a floor above it can never be met.
- `group` counts only required members, all of which every plan must fund.

The base data passes, as it must, because the base model has a plan worth $22,741k (lesson 9.1.1):

```text
base data: no problem found
```

The direction of each comparison is what makes a check sound. Turn one around and it becomes
unsound. Suppose the floor check added only the projects a good plan would fund. It would then fire
whenever that plan fell short, even though another plan meets the floor. A sum over every project
that is not forced out, as the lesson's check takes, is the most the region can get, so it cannot
miss a floor that no plan meets.

<!-- practice 1 -->

## Passing Every Check Does Not Mean a Plan Exists

Now the Budget Lock scenario, first as finance locked it, and then with the transmission crews of
2030 and 2031 put back to GridCap's figures:

```python
for scenario in (LOCK, replace(LOCK, name="lock, crews restored", crews={})):
    problems = run_checks(small, scenario)
    reason = solve(build(small, scenario).model).termination.reason.name
```

```text
budget-lock: solver INFEASIBLE; checks: [('crews', 'P017')]
lock, crews restored: solver INFEASIBLE; checks: no problem found
```

The checks found one cause: P017, a must-do, needs 13 transmission crew-months in its start year,
and the scenario leaves 12 in each of the two years it may start (lesson 9.1.6 prints the check's
message in full). Restoring those crews clears the
check, and the model is still infeasible. Something else clashes, and no single-project check can
see it, because it needs several rows at once. The board forces P032 into 2028 and P023 into the
plan, and P023 needs its parent P022 started at least a year earlier. P032 alone fits the locked
2028 budget, and so does P022. Together they do not (lesson 9.1.6 works out the sums). That is a conflict between projects, and
finding it takes the tools of the next lessons.

This is the shape of every pre-solve check: **sound, but not complete**. A check can prove "no
plan", but passing every check proves nothing. Checks catch the common, cheap causes early and in
plain words. The IIS (lesson 9.1.3) and its relatives catch the rest.

<!-- practice 2 -->

## Summary

- **A solver says "infeasible" even when the cause is one typo.** All five planted errors got the
  same `INFEASIBLE`, with no cause named.
- **Each check reads one project, group or region against one limit.** Window, budget, crews,
  alternative group and regional floor: each fired once, on its own error, with the numbers.
- **A check must never refuse a scenario that has a plan.** Compare a least demand with a most
  supply, and the check is sound. The base data passes.
- **Passing every check does not mean a plan exists.** The Budget Lock scenario with its crews
  restored passes all five and is still infeasible: its conflict joins several projects.

## Reference

| Cause | Sound test |
| --- | --- |
| empty window | no start year $`t \in T_i`$ (or $`t = f_i`$) with $`t + d_i - 1 \le \max Y`$ |
| required project over budget | for every allowed $`t`$, some $`k`$ with $`c_{i,k} > B_{t+k}`$ |
| required project over crews | for every allowed $`t`$, some year of work with $`m_i > K_{q(i),y}`$ |
| two required alternatives | $`\lvert g \cap (M \cup F) \rvert \ge 2`$ for some $`g \in \mathcal{G}`$ |
| floor above supply | $`\sum_{i:\, r(i) = r,\ i \notin D} \text{capex}_i < \text{floor}_r`$ |

| Term | Meaning |
| --- | --- |
| pre-solve check | a test on the input that can show no plan exists, with no solve |
| required project | a must-do project, or one the scenario forces in |
| sound check | fires only when no plan can exist |
| complete check | fires whenever no plan exists (no practical set of checks is complete) |

**Further reading:** the
[CP-SAT troubleshooting page](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md)
in the OR-Tools repository, whose advice on infeasible models includes checking the input data
for errors, such as negative capacities, before anything else; OR-Tools'
[MathOpt](https://developers.google.com/optimization/math_opt) for the model API the checks
stand in front of; and Gurobi's
[infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html),
which starts where checks stop, with the IIS of lesson 9.1.3.

## Challenges

1. Add a sixth check: a required child whose parent can never start early enough (the parent's
   last start plus the lag is after the child's last start). Which row does it protect?
2. The floor check ignores alternative groups. Write a stronger sound version that, in each group,
   counts only the group's most expensive member. Does it fire on the base data?
3. Put P032's forced year at 2031. Which check fires, and what does its message say?

## Design Note: A Check Returns Records, Not Strings

`run_checks` returns `Problem(check, subject, detail)` rather than finished sentences. A service
can then count problems by check, refuse the run, show the detail to a planner, or log the subject
for an audit. Each of those wants a different view of the same finding. The sentence for a planner
is built last, in one place, which is the job of lesson 9.1.6.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**presolve_checks.py.** The five planted errors with the solver's and the checks' answers, the
empty-sum rows, the base data, and the Budget Lock scenario with and without its crew cut (*every
section*). *Try:* Plant P040's first-year cost as 8,500. Predict whether the budget check fires.

- Program: [presolve_checks.py](src/presolve_checks.py)

The checks themselves are in `checks.py`.

- Library: [checks.py](src/checks.py)
