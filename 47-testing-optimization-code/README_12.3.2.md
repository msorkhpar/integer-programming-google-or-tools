# 12.3.2 Property-Based Tests With Hypothesis

The unit tests of lesson 12.3.1 check each of GridCap's planning rules on instances someone thought
of. The next bug will sit in an instance nobody thought of: a child whose parent has a two-year
window, a must-do in an alternative group, a budget that binds only in the middle year. Rather than
write more instances by hand, this lesson states what must be true of *every* plan the model returns
(spend within budget, must-dos always funded, children never without their parents) and lets a
library generate hundreds of small portfolios to try to break it. The library is Hypothesis; the
portfolios are made-up, GridCap-shaped instances, and GridCap itself is fictional.

## The Model Under Test

The model is lesson 12.3.1's, unchanged: one binary per project and allowed start year, and five
rules, each written by its own function in `plan_model.py`.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, each with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the budget of
year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## A Property Is a Rule Every Plan Must Obey, Checked Outside the Model

A **property** is a statement that must hold for every valid input, not for one example. A
**property-based test** draws many inputs, runs the code on each, and checks the statement. If one
input breaks it, the test fails and reports that input. The Hypothesis documentation describes it as
an addition to example-based unit tests, not a replacement, and that is how this module uses it:
unit tests pin the boundary of each rule, properties look for the instance nobody wrote.

The properties of a planning model come from its business rules. Whatever the data, the plan the
model returns must spend within each year's budget, fund every must-do, never fund a child without
its parent (or before the lag), start each project inside its window, and fund at most one project
of each alternative group. The model's rows say the same, so asking the model whether its own plan
is valid proves nothing: a wrong row would approve its own wrong plan. The property is checked by
`audit.violations`, a separate re-check in plain Python that reads only the data and the plan. A
bug would have to be in both, written the same wrong way, to slip through.

Each property is a plain function of one drawn case. Three of them are the rules the planners care
most about, one each:

```python
def spend_within_budget(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    spend = spend_by_year(case.portfolio, plan)
    assert all(spend[y] <= case.portfolio.budget[y] for y in case.portfolio.years)


def must_dos_always_funded(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    assert all(p.project_id in plan for p in case.portfolio.projects if p.must_do)


def children_never_without_parents(case: Case, rules: dict = RULES) -> None:
    _, _, plan = optimize(case.portfolio, rules)
    for p in case.portfolio.projects:
        if p.parent and p.project_id in plan:
            assert p.parent in plan
            assert plan[p.project_id] >= plan[p.parent] + p.parent_lag
```

`plan_obeys_every_rule` checks them all at once through `audit.violations`, and adds `note`, a
Hypothesis function that attaches a line to the report of a failing case, here the plan the model
returned:

```python
def plan_obeys_every_rule(case: Case, rules: dict = RULES) -> None:
    status, npv, plan = optimize(case.portfolio, rules)
    note(f"plan {plan}")
    assert status == "OPTIMAL"                                   # the witness proves it is feasible
    assert violations(case.portfolio, plan) == []
```

Two more properties are not rules but facts about any correct optimizer: the objective it reports
equals the plan's NPV recomputed from the data (`reported_value_is_the_plans_value`), and adding
money to every year's budget never lowers the optimum (`more_budget_never_lowers_the_value`). The
second is a **metamorphic** property: it relates the answers to two inputs instead of checking one
answer. Both compare floats from the solver within `TOL = 1e-3`, because HiGHS's objective values
carry noise around 1e-5 (in lesson 8.3.3 one plan came back as 17,064 and as 17,064.00001) and
GridCap's money is whole $k.

## Generate Instances That Are Feasible by Construction

Hypothesis builds inputs from **strategies**: `st.integers(min_value, max_value)` draws an integer
in a range (both ends included), `st.lists(elements, min_size=..., max_size=...)` a list,
`st.booleans()` true or false, `st.sampled_from(seq)` one item of a sequence. `@st.composite` turns
a function into a strategy of its own: its first argument, `draw`, takes a strategy and returns a
value from it, so the function can make later choices depend on earlier ones.

The hard part is not drawing a portfolio but drawing one that has a valid plan. A random portfolio
is often infeasible (a must-do that costs more than its year's budget), and an infeasible case tests
nothing about the plan. Filtering those out wastes most draws. Instead `cases` draws a plan first,
the **witness**, and builds the data around it:

```python
@st.composite
def cases(draw, max_projects: int = 5) -> Case:
    n = draw(st.integers(min_value=1, max_value=max_projects))
    projects, witness, groups_used = [], {}, set()
    for k in range(n):
        pid = f"P{k + 1}"
        cost = tuple(draw(st.lists(st.integers(1, 50), min_size=1, max_size=2)))
        last_start = YEARS[-1] - len(cost) + 1                 # the work ends inside the horizon
        first = draw(st.integers(YEARS[0], last_start))
        last = draw(st.integers(first, last_start))
        parent, lag = None, 0
        if k > 0 and draw(st.booleans()):
            parent = draw(st.sampled_from([p.project_id for p in projects]))
            lag = draw(st.integers(0, 1))
        alt = draw(st.sampled_from([None, None, "G1", "G2"]))
        start = draw(st.integers(first, last))
        # In the witness only if the rules allow it: parent in it and early enough, group still free.
        fits = (parent is None or (parent in witness and witness[parent] + lag <= start)) \
            and alt not in groups_used
        chosen = fits and draw(st.booleans())
        must = chosen and draw(st.booleans())
        if chosen:
            witness[pid] = start
            if alt:
                groups_used.add(alt)
        projects.append(project(pid, cost, (first, last), must=must, parent=parent, lag=lag, alt=alt,
                                npv=draw(st.integers(0, 100))))
    spend = {y: 0 for y in YEARS}
    for p in projects:
        if p.project_id in witness:
            for year, amount in p.spend(witness[p.project_id]).items():
                spend[year] += amount
    budget = {y: spend[y] + draw(st.integers(0, 60)) for y in YEARS}
    return Case(portfolio(*projects, budget=budget, name="drawn"), witness)
```

Every rule holds for the witness by construction. A parent is drawn only from earlier projects, so
no project can be its own ancestor. A project joins the witness only if its parent is already in it
and starts at least the lag earlier, and only if its alternative group has no member there yet. Only
witness projects can be must-dos. And each year's budget is the witness's spend in that year plus a
drawn slack of 0 to 60, so a slack of 0 makes the budget bind exactly. The model therefore always
has a feasible plan, and `plan_obeys_every_rule` may assert `OPTIMAL`.

The witness gives one more property for free: the optimum is never worse than a plan known to be
valid. That property, `never_worse_than_the_witness`, turns out to matter below.

The ranges are small on purpose: at most five projects, three years, costs of 1 to 50. Bugs in
model code are logic bugs (a wrong loop bound, a wrong sign), and they show on small instances as
well as large ones, while small instances solve in milliseconds and shrink to cases a person can
read.

## Hypothesis Shrinks a Failure to a Small Case That Still Fails

`property_test` turns a property into a Hypothesis test: `@given(cases())` runs the function on drawn
cases, and the settings (next section) say how many and how:

```python
def property_test(check, rules: dict = RULES, config: settings = CI, pinned: bool = True):
    """`check` as a Hypothesis test over drawn cases, on the given rules, pinned cases first."""
    @config
    @given(cases())
    def run(case: Case) -> None:
        check(case, rules)
    for case in PINNED if pinned else []:
        run = example(case)(run)
    run.__name__ = run.__qualname__ = check.__name__
    return run
```

When a drawn case fails, Hypothesis does not stop there. It **shrinks** the case: it retries simpler
variants (fewer projects, smaller numbers, `False` for booleans) and keeps any that still fail, then
reports the simplest one it reached. `hypothesis_finds.py` runs the properties, in order, against
each broken rule of lesson 12.3.1, and prints Hypothesis's report of the first one that fails (the
`Failing test case` line and the note; the inner test function is called `run`):

```text
bug 1: budget skips the last year
  caught by plan_obeys_every_rule
  Failing test case: run(
    case=Case(P1(cost=[1], window=2027-2029, npv=1); budget {2027: 0, 2028: 0, 2029: 0}; witness {}),
)
  plan {'P1': 2029}
bug 2: must-do written as <=
  caught by plan_obeys_every_rule
  Failing test case: run(
    case=Case(P1(cost=[1], window=2027-2027, npv=0, must); budget {2027: 1, 2028: 0, 2029: 0}; witness {'P1': 2027}),
)
  plan {}
bug 3: precedence ignores the lag
  caught by plan_obeys_every_rule
  Failing test case: run(
    case=Case(P1(cost=[1], window=2027-2028, npv=0); P2(cost=[1], window=2027-2028, npv=1, parent=P1 lag=1); P3(cost=[1], window=2027-2027, npv=0); P4(cost=[1], window=2027-2027, npv=0); budget {2027: 0, 2028: 2, 2029: 0}; witness {}),
)
  plan {'P1': 2028, 'P2': 2028}
bug 4: alternatives count one year
  caught by plan_obeys_every_rule
  Failing test case: run(
    case=Case(P1(cost=[1], window=2027-2028, npv=1, alt=G1); P2(cost=[1], window=2027-2028, npv=1, alt=G1); budget {2027: 0, 2028: 2, 2029: 0}; witness {}),
)
  plan {'P1': 2028, 'P2': 2028}
```

Read bug 1's case as a unit test someone could have written: one project costing 1, allowed in any
year, and a budget of 0 in every year. The correct model funds nothing; the broken one, which caps
only 2027 and 2028, starts it in 2029, the year it forgot. Bug 4's case is lesson 12.3.1's
alternatives test, found without being told: two members of one group, both started in 2028, which
a row that counts only 2027 starts allows. Hypothesis wrote each counterexample, and each one points
at its rule.

Shrinking aims for simple, not provably smallest. Bug 3's case kept two projects, P3 and P4, that
are worth 0 and take no part in the failure; the two that matter are P1 and its child P2, started in
the same year although the lag is 1.

## Validity Properties Miss a Rule That Is Too Strict; a Witness Catches It

The fifth bug, the precedence row that adds 1 to the lag, passed both whole-model tests of lesson
12.3.1. It passes every validity property too, because a model that is too strict still returns
valid plans; they are only worse than they should be. `hypothesis_finds.py` goes on:

```text
bug 5: precedence adds 1 to the lag
  caught by never_worse_than_the_witness
  Failing test case: run(
    case=Case(P1(cost=[1], window=2027-2027, npv=0); P2(cost=[1], window=2027-2027, npv=0); P3(cost=[1], window=2027-2027, npv=0); P4(cost=[1], window=2027-2027, npv=1, parent=P1 lag=0); budget {2027: 2, 2028: 0, 2029: 0}; witness {'P1': 2027, 'P4': 2027}),
)
```

The five properties before it in the list all held; `never_worse_than_the_witness` failed.
The witness funds P1 and its child P4 in 2027, which a lag of 0 allows, for an NPV of 1. The broken
row demands the parent start a year before the child, which no year in the window allows, so the
model leaves P4 out and reports 0, less than a plan the strategy proved valid.

So a property suite needs both kinds. **Soundness** properties (every returned plan obeys the rules)
catch a model that allows too much. **Optimality** properties (the optimum is at least as good as a
known valid plan; more budget never lowers it) catch a model that allows too little. The witness is
what makes the second kind possible without solving the problem a second way.

Running the properties against deliberately broken code, as this section did, is the **test of the
tests**: a suite that no broken rule can fail checks nothing. Changing code on purpose to see
whether the tests notice is called mutation testing.

<!-- practice 1 -->

## Fix the Seed, Bound the Examples, Pin What You Found

By default Hypothesis draws different cases on every run and saves failing ones to a local example
database (a `.hypothesis` directory) to replay first next time. That suits a developer's machine. In
CI it does not: a test that fails on one run and passes on the next cannot block a merge, and a
database on a throwaway CI machine is lost. This module's tests use one settings object:

```python
CI = settings(max_examples=60, derandomize=True, database=None, deadline=None)
```

- `derandomize=True` draws the cases from a seed derived from the test itself, so every run tests the
  same cases until the test, Python or Hypothesis changes.
- `max_examples=60` bounds the work: 60 drawn cases per property (the default is 100). Each case is a
  solve, so this sets the test's run time. Raise it in a nightly job; explicit examples come on top.
- `database=None` turns the example database off; nothing is written to disk.
- `deadline=None` removes the per-case time limit (200 ms by default). A solve's time varies with
  machine load, and a deadline would make the test fail for reasons that have nothing to do with
  the model.

`reproducible.py` checks what each choice buys. It runs one recording test twice in a process and
compares the cases drawn:

```python
def drawn(config: settings, fixed_seed: int | None = None) -> list[str]:
    seen = []

    @config
    @given(cases())
    def record(case) -> None:
        seen.append(repr(case))

    if fixed_seed is not None:
        record = seed(fixed_seed)(record)
    record()
    return seen
```

```text
derandomize=True     60 cases, then 60; same cases both times: True
random, no seed      60 cases, then 60; same cases both times: False
random, @seed(2027)  60 cases, then 60; same cases both times: True
first case under derandomize=True: Case(P1(cost=[1], window=2027-2027, npv=0); budget {2027: 0, 2028: 0, 2029: 0}; witness {})
```

`@seed(n)` is the other way to fix the draws: it pins one test to a seed and overrides
`derandomize`. The same program prints the profile Hypothesis registers as `"ci"`, which makes most
of the same choices (it also prints a reproduction blob on failure and keeps 100 examples); this
module states its own settings so that the choice is visible in the code:

```text
the built-in 'ci' profile: settings(backend='hypothesis', database=None, deadline=None, derandomize=True, max_examples=100, phases=(Phase.explicit, Phase.reuse, Phase.generate, Phase.target, Phase.shrink, Phase.explain), print_blob=True, report_multiple_bugs=True, stateful_step_count=50, suppress_health_check=(HealthCheck.too_slow,), verbosity=Verbosity.normal)
```

A profile is registered with `settings.register_profile(name, ...)` and switched on with
`settings.load_profile(name)` (usually in `conftest.py`) or pytest's `--hypothesis-profile` option.

A fixed seed has a price: the suite tries the same 60 cases forever and will not find a bug outside
them. So when a run does find one (a nightly job with more examples, or a developer's random run),
keep the shrunk case. `@example(...)` adds an explicit case that runs before any drawn ones, every
time. `PINNED` holds bug 3's case, with the two idle projects removed, and `property_test` applies
`example(case)` for each. Run against bug 3 again, the test fails on the pinned case before drawing
anything:

```python
PINNED = [
    Case(portfolio(project("P1", (1,), (2027, 2028), npv=0),
                   project("P2", (1,), (2027, 2028), npv=1, parent="P1", lag=1),
                   budget={2027: 0, 2028: 2, 2029: 0}), witness={}),
]
```

```text
bug 3 again, with the shrunk case pinned as an @example:
  Failing explicit example: run(
    case=Case(P1(cost=[1], window=2027-2028, npv=0); P2(cost=[1], window=2027-2028, npv=1, parent=P1 lag=1); budget {2027: 0, 2028: 2, 2029: 0}; witness {}),
)
  plan {'P1': 2028, 'P2': 2028}
```

An explicit example does not count toward `max_examples` and is not shrunk; it is a hand-written
unit test that Hypothesis wrote for you.

<!-- practice 2 -->

## Summary

- **A property is a rule every plan must obey, checked outside the model.** The checker reads only
  the data and the plan, so a wrong row cannot approve its own plan.
- **Generate instances that are feasible by construction.** Draw a valid plan, the witness, and build
  the data around it, so every case tests the plan and none is wasted on infeasibility.
- **Hypothesis shrinks a failure to a small case that still fails.** Four broken rules came back as
  readable counterexamples of one to four projects.
- **Validity properties miss a rule that is too strict; a witness catches it.** Pair soundness
  properties with optimality ones, and run the suite against broken code to test the tests.
- **Fix the seed, bound the examples, pin what you found.** `derandomize=True`, a bounded
  `max_examples`, no database and no deadline make CI repeatable; `@example` keeps found cases.

## Reference

| Setting or tool | What it does | This module |
| --- | --- | --- |
| `@given(strategy)` | runs the test on drawn values | `@given(cases())` |
| `@st.composite` | a strategy built from `draw` calls | `cases` |
| `max_examples` | how many drawn cases pass before the test stops (default 100) | 60 |
| `derandomize` | the same cases on every run | `True` |
| `@seed(n)` | the same cases for this test, from seed `n` | not used |
| `database` | where failing cases are saved and replayed | `None` |
| `deadline` | a time limit per case (default 200 ms) | `None` |
| `@example(...)` | an explicit case, run first, not shrunk | `PINNED` |
| `note(text)` | a line in the failing case's report | the plan |

| Property | Kind | Catches a model that |
| --- | --- | --- |
| `plan_obeys_every_rule` (and the three single-rule ones) | soundness | allows too much |
| `reported_value_is_the_plans_value` | consistency | reports a value its plan does not have |
| `never_worse_than_the_witness` | optimality | allows too little |
| `more_budget_never_lowers_the_value` | metamorphic | gets worse when it has more room |

**Further reading:** [The basic example of MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (the solve and status check each property runs); [Hypothesis: introduction](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html) (`@given`, and property-based tests as an addition to unit tests); [Hypothesis: strategies reference](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html) (`composite`, `integers`, `lists`, `booleans`, `sampled_from`); [Hypothesis: API reference](https://hypothesis.readthedocs.io/en/latest/reference/api.html) (`settings` and its defaults, `derandomize`, `database`, `deadline`, `@seed`, `@example`, `note`, shrinking); [Hypothesis: settings](https://hypothesis.readthedocs.io/en/latest/tutorial/settings.html) (profiles: `register_profile`, `load_profile`); [Hypothesis: replaying failures](https://hypothesis.readthedocs.io/en/latest/tutorial/replaying-failures.html) (the example database, and `@example` for cases that must always run).

## Challenges

1. Write a property for the alternatives rule alone, then find which bug it catches first.
2. `cases` lets a child have only one parent. Draw a second kind of child that needs two parents.
   What must the witness check before adding it?
3. Set `max_examples=5` and run `hypothesis_finds.py`. Predict which bugs still get caught.

## Design Note: Why the Strategy Draws a Plan First

A strategy can draw data and then discard the infeasible cases with `assume` or `.filter`. The
Hypothesis documentation warns that a condition that is hard to satisfy can make such a test fail as
unsatisfiable. Feasibility is a hard condition: with must-dos, budgets and parents drawn
independently, every case where a must-do outgrows its budget or a must-do child's parent cannot
fit would be thrown away, and the cases that survive are the easy ones, with roomy budgets. Drawing the witness
first makes every case feasible, keeps the slack under control (a slack of 0 makes a budget bind
exactly), and gives a lower bound on the optimum to test against. The cost is a strategy that is
longer to write; practice 2 asks for one.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**hypothesis_finds.py.** Runs the properties against each broken rule and prints what Hypothesis
reports (*Hypothesis Shrinks a Failure*, *Validity Properties Miss a Rule That Is Too Strict*, and
the pinned case in *Fix the Seed*). *Try:* Move `never_worse_than_the_witness` to the front of
`PROPERTIES`. Predict which property catches each bug now.

- Program: [hypothesis_finds.py](src/hypothesis_finds.py)

**reproducible.py.** Compares the cases drawn by two runs under three settings (*Fix the Seed, Bound
the Examples, Pin What You Found*). *Try:* Change `max_examples` in `CI` to 20. Predict whether the
first case printed changes.

- Program: [reproducible.py](src/reproducible.py)

**properties.py.** The properties, the `CI` settings, `PINNED` and `property_test`.

- Library: [properties.py](src/properties.py)

**strategies.py.** The `cases` strategy and the `Case` it returns.

- Library: [strategies.py](src/strategies.py)
