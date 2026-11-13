A parcel company's routing service must give the same routes every time it reruns a day, and its
determinism test compares run records from fresh processes. Compared as they are, two records never
match: each holds the time the run started and how long it took, its cost carries floating-point
noise, and its set of unserved stops prints in whatever order the process's hash seed gives.

The docstring of `run_bytes.py` gives a record's shape. Write:

- `canonical(record)`, the record as bytes that are equal exactly when two runs did the same work:
  without the two clock fields (`started_at`, and `wall_seconds` inside `stats`), with every float
  rounded to 6 decimals and `-0.0` written as `0.0`, with dictionary keys sorted, each set as a
  sorted list, and each list kept in its order, since a route visits its stops in order;
- `repeats(records)`, `True` when every record in the list has the same canonical bytes.

`json.dumps(..., sort_keys=True, separators=(",", ":"))` writes compact JSON with sorted keys; JSON
has no sets, so turn them into lists first. About fifteen lines.
