Riverbend Water (invented for this practice) keeps one cost estimate per main-replacement project:
one `estimate` row and its `estimate_line` rows (`estimate.py` has the schema; a line's amount may
not be negative). Engineers revise estimates often, and a revision replaces the project's earlier
estimate. A report that finds a header without its lines prints a $0 job, and one that finds no
estimate at all drops the project, so a failed revision must leave the old estimate exactly as it
was. Street names such as O'Brien Street are common.

Write `save_estimate(conn, project, lines)` in `estimate.py`. `lines` is a list of `(item, amount)`.
It replaces the project's estimate, if it has one, with a new header and the given lines, and
returns the new `estimate_id`. If any line is refused by the database, the exception reaches the
caller and the database is as it was before the call. A saved estimate must be visible to other
connections to the same database file. `connect` already opens connections with foreign keys on
and `autocommit=False` (an argument of Python `3.12` and later; the runner has `3.14.7`). The
foreign key is checked on every statement, so to replace an estimate, delete the old estimate's
lines before its header: a header deleted while its lines still point at it is refused. About eight
lines.
