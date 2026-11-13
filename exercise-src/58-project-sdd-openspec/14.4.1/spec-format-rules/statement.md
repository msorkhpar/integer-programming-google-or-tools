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
