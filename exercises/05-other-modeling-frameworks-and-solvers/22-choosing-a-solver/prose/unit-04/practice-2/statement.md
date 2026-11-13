A team at a rail operator is writing the recommendation for its crew-rostering service. It has
already filtered the candidates by the service's hard requirements, and it has run its benchmark
harness. Now it needs the rule that turns these into a decision, written down as code so the memo
can be regenerated.

Write `pick(passing, evidence)` in `pick.py`. `passing` lists the solvers that met every requirement.
`evidence[solver]` is a dict with `"solved"` and `"runs"` (counts), `"repeat"` (whether every cell
repeated) and `"spread"` (the worst seed spread, a ratio of at least 1). A **finalist** passed the
requirements, solved every run and repeated. A solver in `passing` may be missing from `evidence`:
it was never measured, so it is not a finalist. Rank the finalists by spread, lowest first, breaking
ties by name in alphabetical order. Return `(default, fallback)`: the first and second finalists, with
`None` for any that does not exist.

About six lines.
