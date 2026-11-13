# 14.4. Project: Spec-Driven Development with OpenSpec

One project, grown one OpenSpec change at a time. GridCap's capital planner already works: it picks
which projects to start, and in which year, within a yearly budget. The planners now want to change
its rules, one request after another, and the team decides that no rule changes until it is written
down first. Each lesson takes one request through the whole loop: a proposal, a spec delta with
requirements and scenarios, a list of tasks, tests written from the scenarios that fail on the old
code, the change to the model and the code, the tests passing, and the change archived into the
project's living specs.

**Spec-Driven Development** (SDD) is that way of working: the spec says what the system must do
before anyone writes how. **OpenSpec** is an open-source spec workflow (MIT-licensed, from
Fission-AI) built around it: an `openspec/` folder of living specs and proposed changes, a format
for requirements and scenarios, and a command-line tool that validates and archives changes. These
lessons follow OpenSpec `2.0.0` (the tag `v2.0.0`, commit `d12c2817776779e06891d68230773b3bb673b106`),
read in its documentation and its source.

The project ships `specs_check.py`, a small Python checker that mirrors the format rules of
`openspec validate --strict` that these specs need, and the archive step, so each snapshot checks its
own specs with Python alone. **It is not the OpenSpec CLI.** The OpenSpec CLI is a Node.js program,
and the course's runner image now carries Node.js 24.21.0 and OpenSpec 2.0.0, so the module runs the
real CLI too: `src/openspec_cli.py` runs `openspec validate --all --strict`, `list`, `list --specs`
and `archive <id> --yes` on a temporary copy of every snapshot and every change. The pages show its
output next to `specs_check.py`'s. The two agree on every verdict and on every file archive writes;
they differ in how `list` reports a change and in the archive folder's date. `openspec init`, `new
change` and `show` stay read-along. Every output on the pages comes from these programs, run in the
runner.

The portfolios are invented. They belong to GridCap, the course's fictional utility, and come from a
seeded generator in the project (`capplan/portfolio.py`); no number in them is a real utility's.

## How the Project Is Kept

The project lives in complete snapshots under [`steps/`](steps): `steps/00` is the planner before
the first lesson, and `steps/NN` is the project after lesson NN of this module. Each snapshot holds
the package (`capplan/`), the checker (`specs_check.py`), the specs (`openspec/`), the tests
(`tests/`) and runs on its own:

```text
cd steps/04 && python3 -m pytest && python3 specs_check.py validate --strict && python3 main.py
```

Each snapshot's `main.py` plans a tiny portfolio, 12 projects drawn from seed 58, and prints the
report kept in its `expected/report.txt`. Each lesson's project practice starts from the code of the
snapshot before the lesson, with the specs, tests and expected report of the snapshot after it: the
change is proposed and its scenarios are tests, and the code is still the old code. It is graded by
those tests and by that report.

Each snapshot keeps its changes archived under `openspec/changes/archive/`, as OpenSpec leaves them,
and carries the next lesson's new names as stubs (marked `Stub:`), so every new test fails on an
assertion rather than an import error.

## Contents

1. [Baseline specs: write down what the planner already does](README_14.4.1.md)
2. [A regional spend share: the first change from proposal to archive](README_14.4.2.md)
3. [A must-do override that needs a recorded reason](README_14.4.3.md)
4. [Carry-over: a MODIFIED budget rule and a RENAMED requirement](README_14.4.4.md)
5. [Retiring the yearly start cap: a REMOVED requirement](README_14.4.5.md)
6. [Living specs: every scenario traced to a test, every test to a scenario](README_14.4.6.md)
