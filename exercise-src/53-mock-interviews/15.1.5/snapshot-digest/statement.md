A transit agency's planning service names every scenario's inputs by a digest, so that an auditor can
check years later which inputs produced a locked plan. A snapshot is a dict with a `"scenario"`
name, `"budgets"` (year strings to $k), `"projects"` (a list of dicts, each with a unique `"pid"`)
and `"must_do"` (a list of project ids whose order means nothing). The order of the projects means
nothing either.

Write two functions in `snapshots.py`:

- `canonical(snapshot)` returns the snapshot's bytes in one canonical form: the projects sorted by
  `"pid"`, the must-do ids sorted, then `json.dumps` with sorted keys, separators `(",", ":")` and
  ASCII only, encoded as UTF-8.
- `snapshot_digest(snapshot)` returns the SHA-256 hex digest of those bytes.

Equal content must give equal digests in every process, whatever its string-hash seed, and any change
of content a different one. About eight lines.
