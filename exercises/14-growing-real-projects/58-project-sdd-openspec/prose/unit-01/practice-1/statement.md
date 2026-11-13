The team lead wrote the first request:

> **Request 1.** Before we touch any rule, write down what the planner does today, in words the
> planners can read and sign and in a form the tests can check. And something has to check that the
> written rules are well formed.

The specs are written: `openspec/specs/capital-plan/spec.md` states the planner's rules, and
`openspec/specs/spec-checks/spec.md` states the format rules the project's checker applies, each with
its scenarios. They, the tests and the expected report are given and read-only. Your work is the
checker: `specs_check.py` can already read a spec into requirements and scenarios, but its
`check_requirement` is a stub that fails every requirement. Make it apply the rules the spec-checks
spec states, so that a requirement's text must carry SHALL or MUST, every requirement needs a
scenario with steps, and every scenario needs a trigger and an outcome. Each test is named after the
scenario it checks.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, prints the plan,
and then one line about the living specs and whether they pass strict validation;
`expected/report.txt` is the report it should print. Submit runs every test in `tests/` and compares
Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `check_requirement` in `specs_check.py`

```python
def check_requirement(req: Requirement, where: str) -> list[Issue]
```

- **Contract.** The issues of one requirement, each an Issue(level, where, message) with the `where` it is given, in this order: an ERROR 'requirement "<name>" has no text under its header' when req.text is empty, or else a WARNING 'requirement "<name>" should contain SHALL or MUST in its text' when the text has neither as a whole upper-case word (KEYWORD); an ERROR 'requirement "<name>" must include at least one scenario' when no scenario in req.scenarios has a non-empty body; then, for each scenario with a body, a WARNING 'scenario "<name>" is missing <what>' when has_steps finds no WHEN or GIVEN step ('a WHEN or GIVEN step') or no THEN step ('a THEN step'), both joined by ' and ' when both are missing. An empty list when the requirement keeps every rule.
- **Modeling idea.** A requirement states one behaviour with SHALL or MUST in its text, not only its header; a scenario counts only with steps under it, and needs a trigger and an outcome. Strict validation fails on warnings too.
- **Taught in** [14.4.1 Baseline Specs: Write Down What the Planner Already Does](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-01/14.4.1-baseline-specs-write-down-what-the-planner-already-does.unit.html).

#### `main` in `main.py`

```python
def main() -> None
```

- **Contract.** As before, then one more line about the project's living specs: 'openspec: <n> specs, <r> requirements, <s> scenarios; strict validation passed' (or FAILED), counting openspec/specs/*/spec.md next to main.py, their requirements and scenarios, and passing when specs_check.validate's issues pass in strict mode for every item.
- **Modeling idea.** The project checks its own specs on every run, as `openspec validate --strict` would.
- **Taught in** [14.4.1 Baseline Specs: Write Down What the Planner Already Does](../../../../14-growing-real-projects/58-project-sdd-openspec/units/unit-01/14.4.1-baseline-specs-write-down-what-the-planner-already-does.unit.html).
