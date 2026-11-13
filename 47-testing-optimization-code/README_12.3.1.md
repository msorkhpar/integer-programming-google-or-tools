# 12.3.1 Unit-Testing One Constraint at a Time

GridCap's planning model has been rewritten for the service this section builds, and the pull
request is green: the test suite solves the tiny portfolio, checks that the plan breaks no rule, and
checks that its NPV is the one on record. Then a reviewer notices that the rewritten precedence row
compares the parent's start with the child's start and forgets the lag. The tests never saw it. This
lesson shows why a test of the whole model can pass with a rule broken, and how to test each rule
on its own, with a hand-made instance, a plan it must accept and a plan it must refuse. GridCap is a
fictional utility's portfolio; the instances in the tests are made up by hand.

## The Model Under Test, One Rule per Function

The model is the multi-period selection of lessons 6.4.1 and 6.5.1 to 6.5.4. Its rows are written
by five functions in `plan_model.py`, one per rule, and the rule's label below is the prefix of the
row names its function writes (`budget_2029`, `after_P023_2029`).

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use (its window); $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative
groups, each a set of projects; $`C \subseteq P`$ the child projects, each with parent $`p(c)`$ and
lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$. There is no variable for a year outside the window.

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

| Label | Function in `plan_model.py` | Key in `RULES` |
| --- | --- | --- |
| once | `add_once` | `"once"` |
| must | `add_must` | `"must"` |
| alt | `add_alt` | `"alt"` |
| after | `add_after` | `"after"` |
| budget | `add_budget` | `"budget"` |

`build(portfolio, rules)` takes the rules as a dictionary from name to function, and the default is
all five. That one design choice is what makes the rest of the lesson possible: a test can build a
model with one rule and nothing else, and the lesson can swap a rule for a broken copy and ask which
tests notice. Here is the cumulative precedence row, the rule the reviewer found broken:

```python
def add_after(built: Built) -> None:
    by_id = {p.project_id: p for p in built.portfolio.projects}
    for c in built.portfolio.projects:
        if not c.parent:
            continue
        parent = by_id[c.parent]
        for t in c.starts():
            child_by_t = mathopt.LinearExpression()
            for u in c.starts():
                if u <= t:
                    child_by_t += built.x[c.project_id, u]
            parent_by = mathopt.LinearExpression()
            for s in parent.starts():
                if s <= t - c.parent_lag:
                    parent_by += built.x[parent.project_id, s]
            built.model.add_linear_constraint(child_by_t <= parent_by, name=f"after_{c.project_id}_{t}")
```

Both sums start from `mathopt.LinearExpression()`, so a year in which the parent cannot yet have
started gives an empty right-hand side that is still an expression, and the row says "the child
has not started by $`t`$" instead of raising a `TypeError`.

## A Whole-Model Test Can Pass With a Broken Rule

`bugs.py` holds five broken copies of the rules. Each differs from the correct function in one line,
the kind of change a refactor or a hurried fix leaves behind:

| Bug | Rule | The changed line does |
| --- | --- | --- |
| budget skips the last year | budget | loops over `years[:-1]` |
| must-do written as <= | must | writes `started <= 1` for a must-do |
| precedence ignores the lag | after | sums the parent up to $`t`$, not $`t - L_c`$ |
| alternatives count one year | alt | counts each member's earliest-start variable only |
| precedence adds 1 to the lag | after | sums the parent up to $`t - L_c - 1`$ |

The last one is the only bug that makes the model *stricter*: it refuses plans the rules allow. The
other four make it looser.

The usual end-to-end test solves a portfolio and checks the answer: the plan breaks no rule, which
`audit.violations` re-checks in plain Python from the data, and the NPV equals the correct model's.
`blind_spot.py` runs that test on GridCap tiny and small with each bug swapped in:

```python
def whole_model_test(portfolio, rules) -> tuple[float, str, str]:
    """Solve with these rules; PASS when the plan breaks no rule and its NPV is the correct one."""
    _, best, plan = optimize(portfolio)
    _, npv, got = optimize(portfolio, rules)
    same = "same plan" if got == plan else "plan changed"
    ok = not violations(portfolio, got) and abs(npv - best) < 1e-3
    return npv, same, "PASS" if ok else "FAIL"
```

```text
GridCap tiny: correct model OPTIMAL, NPV 2,473.0, 5 projects
  budget skips the last year    NPV   3,796.0  plan changed  whole-model test FAIL
  must-do written as <=         NPV   2,893.0  plan changed  whole-model test FAIL
  precedence ignores the lag    NPV   2,473.0  same plan     whole-model test PASS
  alternatives count one year   NPV   2,473.0  same plan     whole-model test PASS
  precedence adds 1 to the lag  NPV   2,473.0  same plan     whole-model test PASS
GridCap small: correct model OPTIMAL, NPV 24,260.0, 27 projects
  budget skips the last year    NPV  29,858.0  plan changed  whole-model test FAIL
  must-do written as <=         NPV  26,646.0  plan changed  whole-model test FAIL
  precedence ignores the lag    NPV  24,313.0  plan changed  whole-model test FAIL
  alternatives count one year   NPV  24,397.0  plan changed  whole-model test FAIL
  precedence adds 1 to the lag  NPV  24,260.0  same plan     whole-model test PASS
```

On tiny, three of the five bugs pass. The reason is in the data: a broken row only shows when the
optimum would use the freedom it wrongly gives, or wants a plan it wrongly takes away. Tiny's best
plan never wants a child one year early, or two alternatives at once, so the solver never tries to,
and a model that allows it returns the same plan. On small, where the optimum does push against
those rules, four bugs fail, but the too-strict lag still passes: small's best plan has no child
starting exactly at its lag, so the plans that bug wrongly forbids were not wanted anyway.

A whole-model test checks *one point*, the optimum of one instance. A rule is a statement about
*every* plan. Testing a rule through the optimum means hoping the instance happens to lean on it.

## One Rule, One Hand-Made Instance Where It Alone Can Bind

A **unit test of a constraint** isolates it twice. It builds the model with that rule and no other,
so nothing else can refuse a plan, and it uses an instance made by hand so that the rule binds. A
rule **binds** a plan when the plan sits exactly at its limit or would break it. `tiny.py` makes such
instances short: `project(...)` fills every field a rule does not read, and `portfolio(...)` gives
every year a budget of 10,000, far above anything two or three small projects can spend, unless the
test says otherwise:

```python
def project(pid: str, cost: tuple[int, ...] = (100,), window: tuple[int, int] = (2027, 2027), *,
            must: bool = False, parent: str | None = None, lag: int = 0, alt: str | None = None,
            npv: int = 10) -> Project:
```

The budget test needs a year where the budget is tight and two plans on either side of it. Project
A spends 60 in its first year and 40 in its second; project B spends 1. Only 2029's budget is set,
to 40:

```python
def only(rules: dict, name: str) -> dict:
    """The rule set with every rule but `name` taken out."""
    return {name: rules[name]}


def test_budget_caps_every_year(rules: dict = RULES):
    # A spends 60 in 2028 and 40 in 2029; B spends 1 in 2029. Only 2029's budget is tight.
    data = portfolio(project("A", cost=(60, 40), window=(2028, 2028)),
                     project("B", cost=(1,), window=(2029, 2029)),
                     budget={2029: 40})
    model = build(data, only(rules, "budget"))
    assert allowed(model, {"A": 2028})                   # 40 in 2029: exactly the budget
    assert not allowed(model, {"A": 2028, "B": 2029})    # 41 in 2029: one over
```

Every number in the test can be checked by eye, and every choice is deliberate. The tight year is
the last one, because "the last year" is where off-by-one loops fail. A's spend reaches 2029 only
through its second year of work, so a model that charged the whole cost to the start year would
treat 2029 differently. And the two plans differ by $1k, the smallest step money can take in
GridCap's integer $k, so the test pins the limit exactly.

Each test takes the rule set as a parameter with the real rules as its default. Pytest calls it with
the default; `one_rule.py`, below, calls it with each broken copy.

## Fix the Plan, Then Ask the Solver: Allowed or Refused

A unit test of a rule asks one question: does the model accept *this* plan? A solver answers it if
the plan leaves it no choice. `accepts` fixes every start variable, to 1 for the plan's starts and 0
for all others, by setting both bounds, then solves and reads the termination reason:

```python
def accepts(built: Built, starts: set[tuple[str, int]]) -> bool:
    """Does the model accept these starts? Fix every variable, solve, and read the status.

    Each (project, year) in `starts` is fixed to 1 and every other variable to 0, so the solver has
    no choice left: OPTIMAL means the starts meet every row, INFEASIBLE means some row refuses
    them. A start the model has no variable for (outside the window) is refused outright.
    """
    if any(key not in built.x for key in starts):
        return False
    for key, var in built.x.items():
        value = 1.0 if key in starts else 0.0
        var.lower_bound = value
        var.upper_bound = value
    try:
        result = solve_highs(built.model)
    finally:
        for var in built.x.values():
            var.lower_bound, var.upper_bound = 0.0, 1.0
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(built: Built, plan: dict[str, int]) -> bool:
    """Does the model accept this plan (project -> start year)? See `accepts`."""
    return accepts(built, set(plan.items()))
```

Three details matter, and each is a way to get the helper wrong:

- **Fix every decision, not only the plan's.** If only the plan's starts were fixed to 1, the solver
  could switch on other projects too. A plan that leaves out a must-do would then look allowed,
  because the solver adds the must-do for you. The decisions left free must be none.
- **Fix the decisions, and only the decisions.** This model has no other variables, but many models
  do: a continuous overtime or slack variable, a carry-over amount (lesson 6.4.4). Those are the
  model's to choose once the plan is fixed. Fixing them to 0 would refuse plans the rules allow.
- **A start outside the window is refused, not skipped.** The model has no variable for it, so a
  helper that ignored unknown starts would test some other plan than the one asked about.

The bounds are put back afterwards, so one built model can answer many questions. MathOpt reports
`OPTIMAL` when the fixed values meet every row; the objective value is irrelevant here.
The once rule is the one rule a plan written as `{project: year}` cannot break, since a dictionary
holds one year per project, so its test calls `accepts` with two starts for the same project:

```python
def test_a_project_starts_at_most_once(rules: dict = RULES):
    data = portfolio(project("A", window=(2027, 2028)))
    model = build(data, only(rules, "once"))
    assert accepts(model, {("A", 2027)})
    assert not accepts(model, {("A", 2027), ("A", 2028)})
```

<!-- practice 1 -->

## Pair Every Refused Plan With an Allowed One, at the Boundary

A test that only checks refusals passes on a model that refuses everything. A test that only checks
acceptances passes on a model with no rule at all. So every test here pairs the two, and puts them on
either side of the rule's limit: the budget at 40 and at 41, the must-do in its last allowed year and
left out, the child at exactly its lag and one year early:

```python
def test_child_waits_for_its_parent_and_lag(rules: dict = RULES):
    data = portfolio(project("P", window=(2027, 2028)),
                     project("C", window=(2028, 2029), parent="P", lag=1))
    model = build(data, only(rules, "after"))
    assert allowed(model, {"P": 2027, "C": 2028})        # exactly the lag
    assert not allowed(model, {"P": 2028, "C": 2028})    # one year early
    assert not allowed(model, {"C": 2029})               # no parent at all
```

`one_rule.py` runs the five unit tests against the correct rules and against each broken copy, and
then prints, for each bug, the assertion that caught it:

```python
def outcome(test, rules: dict) -> str | None:
    """None if the test passed, else the source line of the assertion that failed."""
    try:
        test(rules)
    except AssertionError as error:
        return traceback.extract_tb(error.__traceback__)[-1].line
    return None
```

```text
bug 1: budget skips the last year
bug 2: must-do written as <=
bug 3: precedence ignores the lag
bug 4: alternatives count one year
bug 5: precedence adds 1 to the lag
                                        correct  bug 1    bug 2    bug 3    bug 4    bug 5
test_budget_caps_every_year             pass     FAIL     pass     pass     pass     pass
test_must_do_is_always_funded           pass     pass     FAIL     pass     pass     pass
test_a_project_starts_at_most_once      pass     pass     pass     pass     pass     pass
test_at_most_one_alternative            pass     pass     pass     pass     FAIL     pass
test_child_waits_for_its_parent_and_lag pass     pass     pass     FAIL     pass     FAIL
the assertion that caught each bug:
  bug 1  test_budget_caps_every_year: assert not allowed(model, {"A": 2028, "B": 2029})    # 41 in 2029: one over
  bug 2  test_must_do_is_always_funded: assert not allowed(model, {})                        # left out
  bug 3  test_child_waits_for_its_parent_and_lag: assert not allowed(model, {"P": 2028, "C": 2028})    # one year early
  bug 4  test_at_most_one_alternative: assert not allowed(model, {"R": 2027, "S": 2028})    # both, in different years
  bug 5  test_child_waits_for_its_parent_and_lag: assert allowed(model, {"P": 2027, "C": 2028})        # exactly the lag
```

Every bug fails exactly one test, and the failing test's name says which rule is broken. The last
line is the one the end-to-end test could never produce: bug 5, the too-strict lag, was caught by
the *allowed* half of the pair, the plan with the child at exactly its lag. A test with only the
refused plans would have passed it, as both whole-model tests did.

The alternatives test uses two different years on purpose: R in 2027 and S in 2028. A broken row
that counts only each project's earliest-start variable still refuses R and S in the same year, so
a test that put both in 2027 would pass that bug.

`test_a_project_starts_at_most_once` passes everywhere because no bug touches the once rule. It is
still worth its few lines: the next refactor may.

<!-- practice 2 -->

## Summary

- **A whole-model test can pass with a broken rule.** It checks one optimum; on GridCap tiny three of
  five broken rules left the optimal plan unchanged, and on small one still did.
- **One rule, one hand-made instance where it alone can bind.** Build the model with that rule only,
  on an instance small enough to check by eye.
- **Fix the plan, then ask the solver: allowed or refused.** Fix every decision variable by its
  bounds, leave helper variables free, and refuse a start the model has no variable for.
- **Pair every refused plan with an allowed one, at the boundary.** The allowed half catches a rule
  that is too strict, which no check of the solver's own plans can see.

## Reference

| Unit test | Instance | Allowed | Refused |
| --- | --- | --- | --- |
| budget | A (60, 40) from 2028, B (1) in 2029, $`B_{2029} = 40`$ | A | A and B (41 in 2029) |
| must | M must-do, window 2027–2028 | M in 2028 | nothing |
| once | A, window 2027–2028 | A in 2027 | A in 2027 and in 2028 |
| alt | R (2027) and S (2027–2028) in group G | S in 2028 | R in 2027 and S in 2028 |
| after | P (2027–2028), C (2028–2029) with lag 1 | P 2027, C 2028 | P 2028, C 2028; C alone |

| Term | Meaning |
| --- | --- |
| unit test of a constraint | a test of one rule alone, on a hand-made instance, with an allowed and a refused plan |
| binds | a plan sits exactly at the rule's limit, or would break it |
| boundary pair | an allowed plan at the limit and a refused plan one step past it |
| whole-model test | solve a full instance and check the optimal plan; it sees one point of the model |

**Further reading:** [The basic example of MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt/basic_example) (building a model, solving it, and checking `result.termination.reason` before reading values, as `accepts` does); [How to parametrize fixtures and test functions (pytest)](https://docs.pytest.org/en/stable/how-to/parametrize.html) (`@pytest.mark.parametrize`, which the module's tests use to run every one-rule test on the real rules).

## Challenges

1. Write the unit test for a rule this model does not have yet: a minimum spend per year. Which
   plans form its boundary pair?
2. The budget test sets only 2029's budget. Add a broken copy of the budget rule that the test
   misses, then add the plan that catches it.
3. `accepts` fixes variables by their bounds. Write a version that adds equality rows instead, and
   say what each version leaves in the model after it returns.

## Design Note: Why the Model Is Built From a Dictionary of Rules

The usual model builder is one long function. Its rows can only be tested together, so every test
is a whole-model test. Writing one function per rule, and letting `build` take any subset, costs a
few lines and makes each rule testable alone. The same seam lets a test swap in a broken copy, which
is how this lesson checks its own tests: a test suite that no broken rule can fail is not testing
anything (lesson 12.3.2 calls this the test of the tests).

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**blind_spot.py.** Solves GridCap tiny and small with each broken rule and runs the whole-model test
on the result (*A Whole-Model Test Can Pass With a Broken Rule*). *Try:* Add GridCap tiny with its
2028 budget halved as a third portfolio. Predict which of the three passing bugs it exposes.

- Program: [blind_spot.py](src/blind_spot.py)

**one_rule.py.** Runs each one-rule test against the correct rules and every broken copy, and names
the assertion that caught each bug (*Pair Every Refused Plan With an Allowed One, at the Boundary*).
*Try:* Delete the line `assert allowed(model, {"P": 2027, "C": 2028})` from `rule_tests.py`.
Predict which column of the table changes.

- Program: [one_rule.py](src/one_rule.py)

**rule_tests.py.** The five unit tests, one per rule, and `only`.

- Library: [rule_tests.py](src/rule_tests.py)

**plan_model.py.** The model, one function per rule, with `build`, `accepts` and `allowed`.

- Library: [plan_model.py](src/plan_model.py)

**bugs.py.** The five broken copies of the rules.

- Library: [bugs.py](src/bugs.py)

**tiny.py.** Helpers for hand-made instances.

- Library: [tiny.py](src/tiny.py)

**audit.py.** Re-checks a plan against the data in plain Python.

- Library: [audit.py](src/audit.py)
