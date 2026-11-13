Riverbend Water's (invented for this practice) audit trail is append-only. Each entry is a dict
with a sequence number `seq`, an `action`, a `project`, a `kind`, a `year` and who made it, when and
why. The actions are:

- `set`: the override becomes the one in force for its project, replacing any earlier one;
- `inherit`: the same as `set`, written when a plan is copied with its overrides;
- `revoke`: the project's override ends;
- `refused`: a request that was turned down; it changes nothing;
- `clear`: a manager resets the plan; every override in force ends (its `project` is empty).

Entries may reach you in any order, for example merged from two pages of a query.

Write `in_force(entries)` in `replay.py`. It returns `{project: (kind, year)}` for the overrides in
force after every entry has been applied in the order the entries were made. About ten lines.
