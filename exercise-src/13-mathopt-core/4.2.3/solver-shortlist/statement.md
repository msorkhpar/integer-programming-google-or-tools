A freight company's planning service receives models from several teams and must send each to a
solver that will answer the model as written. You decide from the model alone, before any solve.

Write `shortlist(model, need_duals=False)` in `shortlist.py`. It returns the solvers of `CANDIDATES`
(GLOP, PDLP, HiGHS, SCIP, CP-SAT, in that order) that may take the model, keeping that order:

- **GLOP and PDLP** solve LPs only: drop them if any variable is integer.
- **CP-SAT** works over integers: drop it if any variable is continuous, since it would round that
  variable and still report `OPTIMAL`.
- **Dual values** (`need_duals=True`) come only from GLOP, PDLP and HiGHS, and only for an LP: drop
  SCIP and CP-SAT, and if any variable is integer, no solver can give them, so return an empty list.

Read each variable's `integer` flag through `model.variables()`.
