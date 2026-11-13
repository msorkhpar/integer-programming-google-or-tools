A bus operator keeps every timetable version its scheduling service has used, in a bucket of files
(`Store.files`, a dict from name to bytes, stands in for it). Each scenario, such as `"winter"`, has
a chain of versions; an auditor must be able to fetch the exact timetable behind any run and know it
was not changed since.

In `timetables.py`, write `Store.put(doc, scenario)` and `Store.get(key)`. `canonical(doc)` is
written.

- `put` stores the timetable's canonical bytes under their SHA-256 hex digest and returns the digest.
  A name that is already in `files` is never written again.
- `put` appends `{"scenario", "version", "digest", "parent"}` to `log` when the content differs from
  that scenario's latest version: versions count from 1 within each scenario, and `parent` is the
  digest of the scenario's previous version (`None` for the first). Sending the scenario's latest
  content again adds nothing; going back to older content is a new version.
- `get(key)` returns the stored timetable as a dict, or `None` when there is no such file or its
  bytes no longer hash to `key`.

About fifteen lines.
