The planner is now used for the real portfolio, GridCap medium in this course: 400 projects over
ten years (fictional, like all GridCap data). Audit and the planning lead sent the last requests:

> Audit: if we run the same export twice we must get the same plan, and every run must say what it
> was planned from and with what. Prove it.
>
> Planning lead: the rule tests are good, but last month a change to the window code moved projects
> and no test noticed. And each run takes half a minute now; next cycle starts from this cycle's
> plan, so can the solver start from it too?

You start from the planner with scenarios and snapshots. Identify a plan by a digest of its content,
rerun an export from scratch and show whether the runs agree, and record for each run what it was
planned from and with which solver and settings. Check today's plan of a fixed export against a
reviewed golden plan and list every project whose start moved, including one the golden plan never
funded. Let a solve start from last cycle's plan, keeping only the starts the new model still has,
and give the same plan as a solve from nothing.

A plan's canonical JSON is that of the store: sorted keys, no spaces after `,` and `:`. A golden
file is one JSON object with the keys `input` (the export's content hash), `npv`, `starts` and
`status`, written with sorted keys, an indent of one space and a final newline. When the export's
hash differs from the golden file's `input`, the check returns the single line
`input changed: golden <first 12 hex digits>, now <first 12 hex digits>`. A hint reaches HiGHS as
`mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values=...)])`, passed
to `mathopt.solve` as `model_params`, with the variables of this model as keys.

Run's report gains a line: `main.py` now plans the demo export three times and says whether the
plans agree. After the scenario section it prints an empty line, then
`3 runs, same plan: <True or False>, plan digest <12 hex digits>`, the digits being the start of
the first run's plan digest. Submit runs every test in `tests/`, the earlier steps'
included, and compares Run's report with the expected one.
