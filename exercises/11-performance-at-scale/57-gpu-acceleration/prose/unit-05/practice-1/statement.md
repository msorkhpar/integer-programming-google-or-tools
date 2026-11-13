A maintenance crew chooses which jobs to do this year. Job $`j`$ is worth $`v_j`$ ($k of avoided
risk) and takes $`h_{j,q}`$ crew-weeks in quarter $`q`$; quarter $`q`$ has $`C_q`$ crew-weeks. Some
jobs depend on others: for each pair $`(a, b)`$ in `requires`, job $`b`$ may be done only if job
$`a`$ is. The selection is the plan of record, so it must come from a solve that repeats bit for
bit when the auditors rerun it.

Before you code, write the formulation: the binary variables, the objective, one labelled row per
quarter and one per dependency, with their quantifiers. Then write `build(values, hours, capacity,
requires)` in `crew.py`, returning a `highspy.HighsLp` that maximises the value. `solve(lp,
fixed=None)` is given: it solves on one thread and can pin some jobs to 0 or 1 first, which is how
the tests check plans you did not choose. Any correct formulation passes. About twenty-five lines.
