The trim planner's results live in S3 at `trim-results/<survey id>/<run id>.json`. The planners'
tool shows every run of a survey, and a busy survey can have thousands. Its first version made one
`list_objects_v2` call, and nobody noticed for a year.

In `run_listing.py`, write `runs_of(s3, bucket, survey_id)`: the run ids that have a result for that
survey, sorted as text. The rules:

- List every key, on every page: one list call returns at most 1,000 keys. Use the client's
  paginator, as lesson 12.5.3's `rebuild` does.
- Only keys directly under `trim-results/<survey id>/` count. Survey ids have different lengths:
  the runs of `S-70` are not runs of `S-7`.
- A run's result is a file named `<run id>.json` right in that folder. Other files (`t-1.log`) and
  files in deeper folders (`old/t-0.json`) are not runs.
- A survey with no results gives `[]`. A bucket that does not exist is not "no results": let S3's
  `NoSuchBucket` error propagate.

The tests run against moto, which pages like S3. About 10 lines.
