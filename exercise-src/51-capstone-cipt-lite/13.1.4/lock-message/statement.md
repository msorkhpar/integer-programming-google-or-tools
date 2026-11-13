Finance has locked the practice utility's numbers for the year (the utility is fictional), and the
locked scenario has no plan. Planners will not read row names or a solver status; they need **one
message**: which rules clash, the arithmetic that shows it, and the smallest change to a number the
scenario set that gives the scenario a plan, checked by a solve.

`lock.py` gives you milestone 2's model: `build(snapshot, scenario)` returns a `Built` with the
MathOpt `model`, the start variables `x` and `rows`, every row by name (`must_J1`, `force_J4`,
`alt_G1`, `after_J5_2028`, `budget_2029`, `region_North_2028`, `crews_lines_2028`, `floor_South`). A
scenario's `fix_start` and `force_out` are bounds on the variables, not rows. Also given:
`feasible(b)` (does the model have a plan?) and `describe(row, snapshot, scenario)`, one row in
the planners' words.

Write:

- `conflict(b)`: a **deletion filter** (lesson 9.1.3) over the *limit* rows only, the families in
  `LIMITS`; the decision rows (`once`, `alt`, `after`) stay on. Switch a row off by setting its
  bounds to $`-\infty, +\infty`$; if the model is still infeasible, leave it off for good,
  otherwise switch it back on. First do this for each whole family, in the order of `LIMITS`
  (skipping a family with no row), then for each row of the families that stayed, in the order the
  model holds them (lesson 9.1.5). Return the rows left, sorted, and the number of `feasible` calls.
  Count only the family and row calls: `conflict` does not first solve to confirm the scenario is
  infeasible (`message` is only called on one that is). Whatever happens, give every row its own
  bounds back before you return.
- `required(snapshot, scenario, rows)`: each project a `must_` or `force_` row of the conflict names,
  with its window's start years, in the conflict's order; then each project the scenario fixes, by
  id, with its fixed year only.
- `arithmetic(snapshot, scenario, rows)`: for every combination of the required projects' starts
  (`itertools.product`, in `required`'s order), the **first** `budget_` or `crews_` row of the
  conflict, in its sorted order, that the combination overruns, counting only the required
  projects. Lines read `- J1 2027, J2 2028: the 2027 budget needs $200k, has $150k.` or
  `- J1 2027, J2 2028: lines crews in 2028 need 4, have 3.`; a combination that overruns none gets
  no line.
- `repair(snapshot, scenario, rows)`: for each conflict row, in order, that is a number the
  *scenario* set: a crews row, raise it by 1 at a time; a budget row, by $10k at a time. The steps
  stop at the snapshot's own figure and never pass it: a budget locked at $155k with a snapshot
  figure of $200k tries $165k, $175k, $185k and $195k, and not $200k, because $205k would be past
  it. Return the first value that `feasible(build(...))` accepts, as
  `lines crews in 2028 at 4 instead of 3` or `the 2027 budget at $200k instead of $150k`, or `None`.
  Every dollar amount in the message, here and in the arithmetic lines, is written with a thousands
  separator: `$1,250k`.
- `message(snapshot, scenario)`, exactly these lines:

  ```text
  Budget Lock '<name>' has no plan. These <N> rules cannot all hold:
  - <describe(row)>
  - <id> is fixed by this scenario to start in <year>.
  Every way to start <required ids, joined with ", "> runs out:
  <the arithmetic lines>
  Smallest change, checked by a solve: <repair>.
  ```

  The `- <describe(row)>` line comes once for each conflict row, in the conflict's order, and the
  `- <id> is fixed ...` line once for each project the scenario fixes, by id. `<N>` counts the
  conflict rows and the fixed projects, and the last line is
  `No single number of the scenario ends it.` when `repair` finds nothing.

The header names the planning step, `Budget Lock '<name>'`, where the lesson's library writes
`Scenario '<name>'`: every scenario this practice sees is a Budget Lock one. The lesson's message
also numbers its rules and reports the pre-solve checks and the solve count; this one leaves those
out, so that its lines are the conflict, the arithmetic and the change. Lesson 9.1.6 explains why
the message names rules, shows the arithmetic and checks its repair by a solve.
