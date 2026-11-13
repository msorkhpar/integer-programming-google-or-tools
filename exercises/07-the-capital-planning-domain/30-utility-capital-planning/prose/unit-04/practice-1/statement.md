A state commission's auditor (in a fictional water utility's rate case) has the utility's stored
record of the run behind its plan of record, and replays it. Each run record is a dictionary with
a `snapshot` (the id of its inputs), its solver `settings`, the termination `status`, the
`objective` value, and the `plan` (project id to start year). The auditor wants a list of what the
replay did not reproduce.

Write `audit(original, replay, tol=1e-6)` in `audit.py`. It returns a list of findings, empty when
the replay reproduced the run, in this order:

- `"inputs differ"` when the snapshots differ. A replay of other inputs proves nothing about the
  run, so this is then the only finding.
- `"settings differ: <names>"` with the setting names whose values differ, sorted and joined by
  `", "` (a setting only one run has differs too).
- `"status differs"`.
- `"objective differs"` when the objectives are further apart than `tol` times the larger of 1
  and the original's absolute value. Solvers compute in floating point, so two equal answers can
  differ in the last digits.
- `"plan differs: <ids>"` with the project ids whose start years differ, sorted and joined by
  `", "`; a project in one plan only is one of them.

Before you code, decide which findings a replay with 8 threads instead of 1, the same objective
and one project moved by a year should produce. The tests use hand-made run records. About
fifteen lines.
