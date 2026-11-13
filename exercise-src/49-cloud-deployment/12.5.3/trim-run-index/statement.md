The trim planner of the vegetation team (lesson 12.5.2's practice) writes each run's result to S3 at
`trim-results/<survey digest>/<run id>.json`, a JSON object with `run_id`, `status` and, when the
run has a plan, `cost` (whole $k). The planners' tool needs two answers fast: a run's status, and the
best run of each survey. Keep a local SQLite index, as the lesson does.

`trim_index.py` gives you the schema, `connect`, `record` (which inserts a `submitted` row) and
`result_key`. Write:

- `poll(conn, s3, bucket, run_id)`: the run's status. A run id the index never saw is `"unknown"`. A
  run already finished in the index answers from its row, without reading S3 again. A `submitted` run
  looks for its result object: if there is none (`NoSuchKey`), it stays `"submitted"`; if there is
  one, record its `status`, its key and its `cost` (missing for runs with no plan) in the row, and
  return the status. Any other S3 error propagates.
- `best_runs(conn)`: a dict from survey digest to the best run's id. Only runs with a plan count
  (`optimal` or `time_limit`); the best has the lowest cost, and equal costs go to the lower run id
  (compared as text). Surveys with no run that counts are left out.

The schema's `CHECK` refuses a finished row without a result key, as the lesson's does. About 25
lines remain.
