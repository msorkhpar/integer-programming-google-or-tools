A vegetation-management contractor rosters its tree-trimming crews with CP-SAT. The roster must be
reproducible: the same data and the same three numbers from the run's manifest (seed, worker count,
amount of work) must give the same roster on any rerun on the same OR-Tools version.

Write `configure(solver, seed, workers, work)`. It sets the parameters of the given `CpSolver` so
that a run with those three numbers repeats, whether `workers` is 1 or more, and returns the solver.
`work` is the deterministic amount of work at which the search stops. Leave every other parameter
at its default.

About six lines.
