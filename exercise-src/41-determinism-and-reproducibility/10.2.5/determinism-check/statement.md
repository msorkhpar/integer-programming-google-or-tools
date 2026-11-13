A pipeline-inspection company schedules its inspection robots with a small MILP and wants a test
that fails the build when a run stops repeating. A run is a function of no arguments that solves the
model and returns its manifest, a dict such as `{"status": "OPTIMAL", "objective": 17.0, "plan":
[["R1", "seg-4"], ...]}`.

Write `assert_deterministic(run, runs)`. It calls `run` exactly `runs` times and compares every
manifest with the first, in the canonical form `canonical(manifest)` that the starter gives you.
If they all match, it returns the sha256 hex digest of that canonical form. If any differs, it
raises `AssertionError` with a message that names the first run that differs (for example "run 3")
and the top-level fields that differ, using `changed_fields(a, b)` from the starter.

The tests run it on a HiGHS model and on a CP-SAT model, and on runs made to change. About ten lines.
