# 1.3.3 Testing Numerical Code with pytest: Tolerances, Fixtures, Parametrize

GridCap's analysts compute each project's **present value**: what a cost paid in a later year is
worth today, once money's yearly return is taken into account. One analyst writes it as a division,
another rewrites it as a multiplication, and the test that compared the two results with `==` starts
failing. Both formulas are right. Meanwhile the loader of lesson 1.3.2 has six rules and no test that
proves each one still fires. This lesson writes tests for numerical code with pytest, in four rules:
what a test is, how to compare floats, how to share an input between tests, and how to turn a table
of cases into tests. GridCap is a fictional utility, and its numbers are generated, not real data.

## A Test Is a Function That Asserts, and pytest Runs Every One It Finds

[pytest](https://docs.pytest.org/) is a widely used Python test runner. A **test** is a function whose
name starts with `test_` and that checks something with `assert`. `assert condition` does nothing when
the condition is true and stops the function with an `AssertionError` when it is false. pytest
collects the test functions of a file, runs each one, and reports it as **passed** (it returned) or
**failed** (it raised). You run it from a shell with `python -m pytest path/to/file.py`; the programs
of this lesson call `pytest.main([...])`, which does the same from inside Python.

On its own, pytest only collects files whose names start with `test_` or end with `_test.py`, plus
any file you name on its command line. The programs of this lesson have ordinary names, so the course's own test runs leave
them alone, and each one names itself when you run it.

The present value of a cost $`c`$ paid $`n`$ years from now, at a yearly discount rate $`r`$, is

```math
\text{pv} = \frac{c}{(1 + r)^{n}} = c\,(1 + r)^{-n}
```

GridCap's rate is $`r = 0.07`$. Here are two tests of a `present_value` function, one per way of
writing the formula:

```python
def present_value(cost: int, years_ahead: int) -> float:
    """What `cost` paid `years_ahead` years from now is worth today, at RATE a year."""
    return cost / (1 + RATE) ** years_ahead


def test_present_value_exact():
    assert present_value(2150, 1) == 2150 * (1 + RATE) ** -1


def test_present_value_within_tolerance():
    assert present_value(2150, 1) == approx(2150 * (1 + RATE) ** -1)
```

```text
F.                                                                       [100%]
=================================== FAILURES ===================================
___________________________ test_present_value_exact ___________________________
first_tests.py:18: in test_present_value_exact
    assert present_value(2150, 1) == 2150 * (1 + RATE) ** -1
E   assert 2009.3457943925232 == (2150 * ((1 + 0.07) ** -1))
E    +  where 2009.3457943925232 = present_value(2150, 1)
=========================== short test summary info ============================
FAILED first_tests.py::test_present_value_exact - assert 2009.3457943925232 =...
```

The first line has one character per test, in order: `F` for a failure, `.` for a pass. Below it,
pytest explains each failure. It shows the file and line of the `assert`, and because it rewrites
every `assert` it runs, it also prints the values on each side: the left side was
`2009.3457943925232`, computed by `present_value(2150, 1)`. A last line, not shown here, counts the
passes and failures and says how long the run took. When any test fails, pytest's exit code is 1
(0 when all pass), which is how a build server knows to stop. The program prints it:

```text
pytest exit code: 1
```

Why did the first test fail when the two formulas are the same? That is the next rule.

## Compare Computed Floats With a Tolerance You Chose, Never With ==

A **float** stores a number in binary with about 16 significant decimal digits, so most results are
rounded in their last digit. Dividing by $`1.07`$ and multiplying by $`1.07^{-1}`$ round at different
steps, and the two answers can land on neighbouring floats:

```python
def pv_divide(profile: tuple[int, ...], start: int) -> float:
    return sum(c / (1 + rate) ** (start + k - base) for k, c in enumerate(profile))


def pv_multiply(profile: tuple[int, ...], start: int) -> float:
    return sum(c * (1 + rate) ** -(start + k - base) for k, c in enumerate(profile))
```

```text
divide:   2009.3457943925232
multiply: 2009.3457943925234
a == b: False
math.isclose(a, b): True
a == approx(b): True
```

These compute P001's present value (one year of work, $2,150k, starting in 2028, one year after
the plan's first year, 2027). The two results differ by about $`2 \times 10^{-13}`$ $k, a tiny
fraction of a cent, and `==` says they are different. A **tolerance** says how far apart two numbers
may be and still count as equal. `math.isclose` and pytest's `approx` both compare with one.

What tolerance does `approx` use? Printing it shows:

```text
approx(b) means 2009.3457943925234 ± 0.00200935
approx(0.0) means 0.0 ± 1.0e-12
1e-9 == approx(0.0): False
1e-9 == approx(0.0, abs=1e-6): True
```

By default `approx(expected)` allows a **relative** tolerance of one millionth of `expected`
(`rel=1e-6`), or an **absolute** tolerance of $`10^{-12}`$ (`abs=1e-12`), whichever is larger. For
$2,009k that is $0.002k, two dollars, which is a sensible "equal" for money in $k. Near zero the
relative part vanishes: one millionth of 0 is 0, so `approx(0.0)` allows only $`10^{-12}`$. A number
that should be zero, such as the unspent part of a budget a solver used up, needs an absolute
tolerance you choose, as in `approx(0.0, abs=1e-6)`.

Why not round both sides instead? Because rounding moves a tiny difference to a big one when the
value sits near a rounding boundary:

```text
rounded to cents: 0.13 0.12
```

`0.125 + 1e-12` and `0.125 - 1e-12` differ by two trillionths, and rounded to two decimals they differ
by a whole cent. A tolerance never does that.

Not every number needs one. GridCap keeps money as whole $k in `int`s, and Python adds integers
exactly, so a total cost is tested with `==`. A tolerance is for floats: present values, rates, and the
variable values a solver returns, which lesson 1.1.3 printed as floats such as `1.0` and `0.099`.

<!-- practice 1 -->

## A Fixture Builds an Input Once and Hands It to Every Test That Names It

Several tests often need the same input, such as the tiny portfolio. A **fixture** is a function
marked `@pytest.fixture` that builds that input. A test asks for it by naming it as a parameter, and
pytest calls the fixture and passes its result in:

```python
@pytest.fixture(scope="module")
def tiny() -> Portfolio:
    return generate("tiny")


def test_capex_is_the_sum_of_the_cost_profile(tiny):
    assert tiny.project("P003").capex == 980 + 1490
```

```python
def test_csv_round_trip_keeps_the_portfolio(tiny, tmp_path):
    assert load_csv(save_csv(tiny, tmp_path)).content_hash() == tiny.content_hash()
```

A fixture's **scope** says how long one result is kept. The default, `scope="function"`, builds a
fresh one for every test that asks, so no test can see what another test did to it. `scope="module"`
builds it once for all the tests in the file, which is right for an input that is slow to build and
that no test changes (a GridCap `Portfolio` is frozen). `tmp_path` is a fixture pytest provides: a new
empty folder per test (pytest keeps those of the last three runs and deletes older ones), so the round-trip test writes its CSV files where nothing else
can collide with them. The test checks that writing the portfolio and reading it back gives the same
content hash, the fingerprint `gridcap` computes from every number in a portfolio.

`--setup-show` makes pytest print when it builds (`SETUP`) and discards (`TEARDOWN`) each fixture,
with its scope as a letter: `S` for the whole session, `M` for the module, `F` for one function:

```text
    SETUP    M tiny
        fixture_checks.py::test_capex_is_the_sum_of_the_cost_profile (fixtures used: tiny) .
        fixture_checks.py::test_present_value_of_a_one_year_project (fixtures used: tiny) .
SETUP    S tmp_path_factory
        SETUP    F tmp_path (fixtures used: tmp_path_factory)
        fixture_checks.py::test_csv_round_trip_keeps_the_portfolio (fixtures used: request, tiny, tmp_path, tmp_path_factory) .
        TEARDOWN F tmp_path
    TEARDOWN M tiny
TEARDOWN S tmp_path_factory
```

`tiny` is set up once and used by all three tests. `tmp_path` is set up for the one test that asked
for it and torn down right after. (`tmp_path_factory` and `request` are pytest's own helpers behind
`tmp_path`.)

## Parametrize Turns a Table of Cases Into One Test per Row, and Each Case Breaks One Rule

Lesson 1.3.2's loader has six rejection rules, and each deserves a test. Writing six near-identical
functions invites copy mistakes. `@pytest.mark.parametrize` takes a list of cases and runs one test
function once per case, passing each case's values in as parameters:

```python
CASES = [
    ("P009", "unable to parse string as an integer"),
    ("P010", "greater than or equal to 0"),
    ("P011", "earliest start after latest"),
    ("P012", "Input should be 'Ridge'"),
    ("P008", "duplicate id"),
    ("P013", "unknown parent"),
]
```

```python
@pytest.mark.parametrize(("project_id", "reason"), CASES, ids=[pid for pid, _ in CASES])
def test_bad_row_is_rejected_for_its_rule(rejected, project_id, reason):
    assert any(pid == project_id and reason in why for _, pid, why in rejected)
```

The first argument names the parameters, the second is the table, and `ids=` gives each case a
readable name in the report. `rejected` is a module-scoped fixture that loads the dirty export of
lesson 1.3.1 once and returns `load`'s list of rejections, `(line, project id, reason)` triples. Run
with `-v` (verbose), pytest lists every case on its own line:

```text
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P009] PASSED     [ 14%]
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P010] PASSED     [ 28%]
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P011] PASSED     [ 42%]
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P012] PASSED     [ 57%]
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P008] PASSED     [ 71%]
bad_row_cases.py::test_bad_row_is_rejected_for_its_rule[P013] PASSED     [ 85%]
bad_row_cases.py::test_good_rows_are_not_rejected PASSED                 [100%]
```

Each case is a separate test: if one fails, the report names it, and the others still run. Adding a
seventh rule is one more line in the table.

The table is only as good as its cases, and two habits make it trustworthy. First, **each case breaks
exactly one rule.** A row with a negative cost *and* an unknown region is rejected even if the
negative-cost check is deleted, because the region check still rejects it, so the test would keep
passing over a broken loader. Every row the planner appended in lesson 1.3.1 breaks one rule, and
that is why they make good cases. Second, **each case checks its reason, not only that the row was
rejected.** The test above asserts the reason text for that project, so it fails if P010 is ever
rejected for something other than its negative cost. The last test of the file checks the other
direction: no good row is rejected at all.

<!-- practice 2 -->

## The Model

The selection model of lesson 1.1.1, whole, with the budget row written as a test checks it on a
plan that came from a solver. A test cannot ask a float sum to be at most $`B`$ exactly, so it allows
a tolerance, and the mark shows the change.

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$
the child projects, each with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups.

**Parameters.** $`\text{capex}_i`$ and $`\text{npv}_i`$ for each project ($k); $`B`$, the capital
budget ($k); in a test, a relative tolerance $`\rho`$ and an absolute tolerance $`\alpha`$ (for
example $`\rho = 10^{-6}`$, $`\alpha = 10^{-6}`$).

**Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$: 1 if project $`i`$ is funded.

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B + \max(\rho\,|B|,\ \alpha) && && \text{(budget, as a test checks it)} \quad \leftarrow \text{this lesson} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

The model itself keeps $`\le B`$. The tolerance belongs to the test, because the test reads values a
solver computed in floating point, and $`\max(\rho|B|, \alpha)`$ is the same "relative or absolute,
whichever is larger" rule that `approx` uses.

## Summary

- **A test is a function that asserts, and pytest runs every one it finds.** A failure shows the
  values on both sides of the `assert`, and any failure makes the run's exit code 1.
- **Compare computed floats with a tolerance you chose, never with `==`.** `approx` is relative
  by default; near zero, pass `abs=`. Never round both sides. Integer money is compared exactly.
- **A fixture builds an input once and hands it to every test that names it.** The default scope is
  one build per test; `scope="module"` shares one build across a file. `tmp_path` gives each test
  its own folder.
- **Parametrize turns a table of cases into one test per row, and each case breaks one rule.** Check
  the reason, not only the rejection.

## Reference

| Need | pytest |
| --- | --- |
| Run a file's tests | `python -m pytest file.py` (`-v` one line per test, `-q` quiet) |
| Float equality with tolerance | `actual == approx(expected, rel=1e-6, abs=1e-12)` |
| Plain-Python tolerance | `math.isclose(a, b, rel_tol=1e-9, abs_tol=0.0)` |
| Shared input | `@pytest.fixture(scope="module")`, then name it as a test parameter |
| A fresh folder per test | the `tmp_path` fixture |
| See fixture builds | `--setup-show` |
| One test per case | `@pytest.mark.parametrize(("a", "b"), cases, ids=[...])` |

| Tolerance | What it bounds | When |
| --- | --- | --- |
| relative, $`\rho`$ | $`\lvert a - b\rvert \le \rho\,\lvert b\rvert`$ | values far from zero, of any size |
| absolute, $`\alpha`$ | $`\lvert a - b\rvert \le \alpha`$ | values that should be zero or near it |

**Further reading:** [pytest: good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) (which files, functions and classes pytest collects); [pytest API reference, `approx`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx) (the default `rel=1e-6` and `abs=1e-12`, and why comparing with zero needs the absolute part); [pytest: how to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) (requesting a fixture by name, and the five scopes); [pytest: how to parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) (one test per set of values, each reported on its own); [pytest: temporary directories](https://docs.pytest.org/en/stable/how-to/tmp_path.html) (`tmp_path`, one folder per test, and how long pytest keeps them); [pytest exit codes](https://docs.pytest.org/en/stable/reference/exit-codes.html) (0 for all passed, 1 for failures, and the rest); [Python tutorial: floating-point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html) (why float results round, and `math.isclose`).

## Challenges

1. A test compares a solver's objective with `approx(3627)`. How large a difference does it allow,
   in $k? Would you tighten or loosen it for a $500M portfolio?
2. Make the `tiny` fixture function-scoped. How many `SETUP` lines for it does `--setup-show` print
   now? Predict, then run `fixture_checks.py`.
3. Add a seventh case to `CASES` for a row with a blank `program`. Which reason fragment would you
   assert?

## Design Note: Tests Use Their Own Small Inputs

These tests read GridCap tiny, because this lesson is about GridCap. A real loader's tests are better
off with hand-made rows like the ones in this module's practices: each built to break one rule, small
enough to check by eye, and not changed when the generator changes. GridCap's own `tests/` pins the
generator's output with a content hash, so a change to the data is always deliberate.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**first_tests.py.** Two tests of one present value, run by pytest: one with `==`, which fails, and one
with `approx` (*A Test Is a Function That Asserts*). *Try:* Change the exact test to compare
`present_value(2000, 0)` with `2000.0`. Predict whether it passes.

- Program: [first_tests.py](src/first_tests.py)

**float_compare.py.** Computes P001's present value two ways and compares them with `==`,
`math.isclose` and `approx`, then shows the tolerances `approx` uses (*Compare Computed Floats With a
Tolerance*). *Try:* Replace P001 with P003, a two-year project. Predict whether `a == b` changes.

- Program: [float_compare.py](src/float_compare.py)

**fixture_checks.py.** Three tests that share a module-scoped `tiny` fixture, run with `--setup-show`
(*A Fixture Builds an Input Once*). *Try:* Remove `scope="module"`. Predict how many times `tiny` is
set up.

- Program: [fixture_checks.py](src/fixture_checks.py)

**bad_row_cases.py.** One parametrized test over the six bad rows of the dirty export (*Parametrize
Turns a Table of Cases Into One Test per Row*). *Try:* Change P010's reason to `"cost_profile"`.
Predict whether the test still catches a loader that rejects P010 for the wrong reason.

- Program: [bad_row_cases.py](src/bad_row_cases.py)
