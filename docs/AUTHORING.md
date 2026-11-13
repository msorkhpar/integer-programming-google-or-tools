# Authoring conventions

How every module of this course is written, checked and shipped. The pilot (modules 01 and 26)
follows it; every later module, by any author, follows it too. The StudyForge skills (`lessons`,
`exercises`) are the base; this page adds what this course needs on top.

## 1. Formulation first

The core skill of the course is writing models. So a model is always **stated** before it is coded.

- **Every lesson that builds or changes a model has a "The model" block**: the complete formulation,
  in one place, in this order:
  1. **Sets and indices** (projects $`P`$, years $`Y`$, start years $`T_i`$, …)
  2. **Parameters**, with units (capex in $k, budgets $`B_y`$, …)
  3. **Decision variables with their domains and bounds** ($`x_{i,t} \in \{0,1\}`$,
     $`r_y \ge 0`$, $`0 \le s_y \le \bar s`$). Never a variable without its domain.
  4. **The objective function**, with its sense (max or min).
  5. **Every constraint, labeled**, with its quantifier ($`\forall i \in P`$). The label is the
     name the code gives the row (`budget_2029`, `once_P017`, `after_P023_2029`), and a table maps
     labels to code names when they are not obvious.
- A lesson that only changes part of a model restates the whole model, with the change marked, once.
  A reader must never have to assemble a model from three sections.
- **Display math** is a ```` ```math ```` fence; **inline math** is $`x_{i,t}`$ (dollar, backtick).
  The site draws both with KaTeX; GitHub draws them too. Use `\begin{aligned} … \end{aligned}` for a
  constraint system, `\text{…}` for words, and `&& \text{(label)}` for a row's label.
- **Practices follow the same progression:**
  - Sections 1–5: the statement gives the formulation of the part to implement; the reader turns
    it into code. Tests check behaviour, not code shape.
  - Section 6 on: modeling practices give the business rule in words; the reader writes the
    formulation and the code. Tests check feasible and infeasible hand-built plans, so any correct
    formulation passes. The statement says so.
  - Capstone and Projects: the reader writes the whole formulation; the blueprint names each
    method's modeling idea and the lesson that taught it.
- **Quizzes** ask formulation questions: which constraint states a rule, which objective answers a
  planner's question, what a variable's domain must be.

## 2. Lessons

- Follow the StudyForge `lessons` skill: a GridCap scenario first, rules as headings, end matter
  (Summary, Reference, Challenges, Design note), practices placed with `<!-- practice N -->`.
- **Every code block and every output is real.** Programs live in `<module>/src/`, tests of them in
  `<module>/tests/`. `python3 scripts/runner.py python3 scripts/verify_lessons.py <module>` fails a
  ```` ```python ```` block that is in no program and a ```` ```text ```` block no program printed.
- **Inline examples show their output; the full programs run.** A ```` ```python ```` fence is lifted
  from exactly one program in `src/`, with the ```` ```text ```` it printed directly under it; the
  page shows both and offers no Run (`example_run: false`), because the output is already there.
  The adapter (`ingest/read.py`, `runnable`) still records which program each fence comes from, so
  the lesson's last section, **The Full Programs**, can run them: one short paragraph per program
  (what it is, which section it backs, and a *Try:* that asks the reader to change one thing and
  predict before running, never a claimed result), then a one-link list (`- Program: [x.py](src/x.py)`).
  A module a program imports but that prints nothing is listed as `- Library:`. Tests check the
  lesson's numbers and are never linked (`example_tests: false`).
- **No claim about solver behaviour, timing or output without a program that produced it.** If a
  sentence explains *why* an output happened, it must follow from the code or the math, or go.
- Run everything in the runner image (`scripts/runner.py`), never on the host: a host run can print
  the machine's user and host names.
- **Sources come first, and the OR-Tools documentation leads them.** Before writing, open the
  OR-Tools pages (developers.google.com/optimization) and samples (github.com/google/or-tools) for
  every OR-Tools topic the lesson touches, the blueprint's resource library for the section and the
  matching entries of `docs/plan/resource-links.md`. Teach the API the way the OR-Tools pages do and
  check every API claim against them.
- **OR-Tools examples may be adapted** (they are Apache-2.0 code): move them onto GridCap or keep
  their own setting, run them like any program, and say where each came from in the prose and in a
  comment at the top of the program (`# Adapted from the OR-Tools example <name>, <URL>`). Never copy
  the documentation's prose.
- **Every lesson cites what it was written from.** The Reference section ends with a line
  `**Further reading:**` (or `**Further reading.**`) paragraph that links the sources actually opened for the lesson, OR-Tools pages first.
  `scripts/check_exercises.py` check 7 refuses a lesson without it.
- Length is not a target. A lesson is as long as it takes to present its concept fully, so that a
  learner with no background can follow every step and use it in an interview. The blueprint's
  minutes are estimates, not limits; never cut a step, a definition or the "why" to save time.
  Material beyond the lesson's concept still goes to the section's Going deeper part.

## 3. Practices and quizzes

- Sources live in `exercise-src/<module>/<lesson>/` (see `scripts/exercises.py`'s docstring).
- Tests use their own small instances, never GridCap or the lesson's numbers. A workspace is
  self-contained: no `gridcap` import.
- Starters fail every test on an assertion (return a wrong value; never raise). Each edge case's
  plant is one realistic misconception, written as edits of the reference, and passes every main case.
- Modeling tests pair an allowed plan and a refused plan in one test, so a starter with no rules fails.
- **Two or three code practices per Core or Deep lesson, one per rule worth doing by hand.** A quiz
  is not a practice; a lesson whose only hands-on part is one function is too thin.
- **A practice sits after every section it draws on.** Its aspects' `basis` sections are all above
  its `<!-- practice N -->` marker.
- **From section 6 on, a practice transfers, never retypes.** It uses a different business rule or
  setting than the lesson's own code, so the learner writes a formulation the page did not show.
  Given scaffolding (variables, rows the lesson already taught) goes in the starter.
- `python3 scripts/exercises.py prove <module>` gates every draft in the offline runner.
- Quizzes: three questions, each a scenario with inputs the page does not show; options parallel in
  form and length; every wrong option a misconception the page refutes. Readings come from
  independent agents: a page-free reader (StudyForge's `Q2_PROMPT`, sees only the question) and a
  page reader (sees the pages, picks the key, says whether a passage refutes each wrong option).
  Reword until the page-free reader picks nothing and the page reader refutes every wrong option;
  record with `scripts/exercises.py record`.
- **Spread the keys.** The site shows options in the order written, so the key's position varies
  across a quiz and across a module (no position holds more than 40% of a module's keys).
- **A quiz aspect names a topic, never the answer.** Its sentence is shown on the quiz card before
  the reader answers: "why the cash row is an inequality", not "the cash row is an inequality
  because money lapses".

- **An empty sum is the number 0, and MathOpt refuses a row built from it** (`0 <= 5` is a Python
  `bool`, and `add_linear_constraint` raises `TypeError`). Skip the row, or build it with
  `mathopt.LinearExpression()` as the start of the sum, when its set can be empty.

## 4. Data and licences

- GridCap is fictional; say so where a lesson could be mistaken for real data.
- No Gurobi license in any image, commit or page. Gurobi examples read `GRB_LICENSE_FILE`, mounted
  read-only at run time.
- Cite only sources actually opened. Paraphrase; never copy a resource's text.

## 5. What the learner run taught us

An agent playing a learner with no LP or ILP background read the pilot on the site, solved its
practices and answered its quizzes (2026-11-11). It passed, but for the wrong reasons, and each
reason is now a rule above or a check in `scripts/check_exercises.py`:

| Found | Rule | Check |
| --- | --- | --- |
| every quiz key was option a | spread the keys | 1 |
| the quiz card's aspects stated the answers | a quiz aspect names a topic | 2 |
| a practice came before the section that teaches it | a practice sits after its sections | 3 |
| module 26 practices were the lesson's snippet with names changed | from section 6 on, transfer | 4 |
| one code practice per lesson, against 2-3 in the other courses | two or three per Core lesson | 5 |
| a wrapped line starting "0." or "2028." became a list, cutting the sentence (section 1 run) | rewrap so no prose line starts with a number and a period; indent fences inside list items | 6 |
| quiz keys found from wording alone: the key echoed the stem, was the longest, or only wrong options had "always"/"never" (section 1 and 2 readers) | the key matches the others in length and form; stem words and absolutes are spread across options | readers |
| MathOpt, "LP relaxation", "bound", "concave" used before they were defined | define a term where it is first used, or link the lesson that does | read |
| prose that disagreed with its own output ("two children", "section 3") | every number and reference in prose is checked against the output or the page it names | read |

The last two are for the author and the outsider review to read for; no script sees them.

**Before a module ships**, in this order: `scripts/check_math.py`, `scripts/verify_lessons.py` (in
the runner), `scripts/check_exercises.py`, `scripts/exercises.py prove`, then the outsider review.
**At the end of each section**, run a learner judge: a fresh agent with no exposure to earlier runs
reads the section on the site, solves its practices in copies of the workspaces, answers the quizzes
from a file with the keys removed, and logs every fact it needed that the pages did not give.
When it extracts a page's text it drops every `<details>` (worked solutions) and every quiz element:
`[data-practice-kind="quiz"]` (the card), `section[data-practice-quiz]` and `[data-form-kind="quiz"]`
(the questions), and the quiz's "Check yourself" section. It writes its formulation before coding
each modeling practice, and it reads a test file only after a failed attempt, saying so.

## 6. Run only what a change touches

A check that passed stays passed until one of its inputs changes. Re-running it on unchanged inputs
spends time, machine and tokens for nothing, so it is not done.

| What changed | What runs, and nothing more |
| --- | --- |
| a lesson's prose or math | `scripts/check_math.py <that lesson's file>` |
| a program in `<module>/src/`, or a lesson's code or output fences | `scripts/verify_lessons.py <that module>` (in the runner) and that module's example tests |
| one practice or quiz | `scripts/exercises.py prove <module> <lesson>`, for that lesson only |
| a quiz's wording | the reader rounds for the questions whose digest changed, never the rest |
| a StudyForge source file | the test modules that mirror it (the tree mirrors the source), plus `python3 -m tests.floor` |
| what is shipped | `studyforge exercises stale` names exactly the authored units to re-ship; re-ship those |

**The full runs happen once, at the end:** when a section is done, run `check_math`,
`verify_lessons`, `check_exercises`, `prove` and the corpus checks over the whole section, then the
learner judge; when a StudyForge change set is done, run its full suite once before its commit,
compared with main's. A full suite that is already running for a change set is not started again.

