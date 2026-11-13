GridCap's auditors sent the sixth request:

> **Request 6.** For every rule in these specs, show us the test that proves the planner keeps it. For
> every test, show us the rule it checks.

The change is proposed and archived in `openspec/`: it adds a traceability requirement to the
checker's spec, with the naming convention every test already follows. It also finishes the open
tasks of the must-do change, whose scenario "A must-do that cannot start in the plan is refused" has
been in the living spec with no test and no code. The specs, the tests and the expected report are
given and read-only.

You start from the planner without the start cap, where `specs_check.trace` is a stub. Write the
trace: every scenario of the living specs to the test named after it in its capability's test file,
and every test of those files to its scenario, reporting both kinds of gap. Then make the planner
refuse, before solving, a must-do project that cannot start in any plan year, naming it, where it
now returns an infeasible plan with no word about why.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, prints the plan, the refusal of the retired start cap,
the line about the specs, and a last line with the trace; `expected/report.txt` is the report it
should print. Submit runs every test in `tests/`, the earlier steps' included, and compares Run's
report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `test_name` in `specs_check.py`

```python
def test_name(scenario: str) -> str
```

- **Contract.** A new function. `test_` followed by the scenario's name in lower case, with each run of characters other than `a`-`z` and `0`-`9` replaced by one `_`, and no `_` at either end of the name part: the scenario `A must-do is refused!` gives `test_a_must_do_is_refused`.
- **Modeling idea.** The link between a scenario and its test is a naming convention the checker can check.
- **Taught in** [14.4.6 Living Specs: Every Scenario Traced to a Test, Every Test to a Scenario](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-06/14.4.6-living-specs-every-scenario-traced-to-a-test-every-test-to-a-scenario.unit.html).

#### `trace` in `specs_check.py`

```python
def trace(root: Path) -> Trace
```

- **Contract.** Reads every scenario of `root/openspec/specs/<capability>/spec.md` and expects its test, named by `test_name`, in `root/tests/test_<capability>.py` with each `-` of the capability written as `_` (`capital-plan` gives `tests/test_capital_plan.py`). Reads the module-level test functions (named `test_...`) of those files with `ast`, without importing them; other test files are ignored. Returns `Trace(pairs, untested, untraced)`: the number of scenarios whose test was found, the sorted `<capability>: <scenario>` labels with no test, and the sorted `tests/<file>::<test>` names that match no scenario of their own file's capability.
- **Modeling idea.** A scenario is matched to a test in its own capability's file only; a test of the same name elsewhere does not count.
- **Taught in** [14.4.6 Living Specs: Every Scenario Traced to a Test, Every Test to a Scenario](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-06/14.4.6-living-specs-every-scenario-traced-to-a-test-every-test-to-a-scenario.unit.html).

#### `check` in `capplan/request.py`

```python
def check(projects: list[Project], request: Request) -> None
```

- **Contract.** As before, and raises ValueError, naming the project, for a must-do whose window has no plan year.
- **Modeling idea.** An empty window gives an empty sum, 0 == 1, which CP-SAT takes as a constraint that never holds; refuse it with a message first.
- **Taught in** [14.4.6 Living Specs: Every Scenario Traced to a Test, Every Test to a Scenario](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-06/14.4.6-living-specs-every-scenario-traced-to-a-test-every-test-to-a-scenario.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, and a last line from `specs_check.trace`: 'trace: <pairs> scenarios with their tests, <n> with none, <m> tests with no scenario'.
- **Modeling idea.** The project traces its specs to its tests on every run.
- **Taught in** [14.4.6 Living Specs: Every Scenario Traced to a Test, Every Test to a Scenario](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-06/14.4.6-living-specs-every-scenario-traced-to-a-test-every-test-to-a-scenario.unit.html).
