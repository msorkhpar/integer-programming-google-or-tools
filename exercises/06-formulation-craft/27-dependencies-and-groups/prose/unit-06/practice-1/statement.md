A ferry operator schedules each vessel's dry-dock overhaul in one of the years 2027 to 2031. The
model in `docks.py` has a binary `x[vid, t]` for each vessel and each year `t` in its `years`, and
each vessel docks at most once (given). The fleet managers send three kinds of override, each a
tuple:

- `("lock", vid, year)`: the vessel docks in `year`, and in no other year. If `year` is not one of
  the vessel's `years`, the lock cannot be kept, and the vessel does not dock in this plan at all:
  the reference closes every year the vessel has, as for a ban, and the model stays solvable.
- `("ban", vid)`: the vessel does not dock in this plan.
- `("by", vid, year)`: if the vessel docks, it docks in `year` or earlier.

Write two functions in `docks.py`:

- `apply_overrides(x, vessels, overrides)` changes the model so that it allows exactly the plans
  that keep every override, **using only the variables' bounds** (no rows), and returns a record of
  what it changed.
- `undo_overrides(changes)` takes that record and puts every bound back exactly as it was before
  `apply_overrides`, even a bound that was not 0 or 1 at the time.

Write down, for each kind of override, which variables' bounds it sets and to what, before you code
it. Then decide what `undo_overrides` needs to know about each change, and make your record hold it.

The tests fix plans through the remaining bounds and ask the solver whether the model accepts them,
and they read the bounds back after an undo. About fifteen lines.
