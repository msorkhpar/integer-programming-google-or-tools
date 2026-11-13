Riverbend Water (invented for this practice) answers its engineers' what-if questions the way this
module does: never by editing the plan under review. `whatif.py` already has the model: `solve(plan,
projects)` picks at most one start year per water main within each year's budget, maximizing value,
and applies the plan's overrides as bounds (`("start_in", y)` fixes the year, `("out", None)` keeps
the main out).

Write the two missing functions; `what_if` uses them.

- `copy_with_overrides(base, plan_id, overrides)`: a new `Plan` with `base`'s budgets and
  overrides, the new `overrides` added on top (a new override on a project replaces the old one),
  and `parent_id` naming `base`. The base must come out of a what-if exactly as it went in.
- `diff(a, b)`: from plan `a` to plan `b` (each `{pid: start year}`), the projects `b` selects that
  `a` does not, the projects `a` funds that `b` defers, and the projects both fund in different
  years, as `(pid, a's year, b's year)`. Each list sorted by project id.

The main test overrides three mains on a copy, re-optimizes both plans and checks the diff. About
eight lines in all.
