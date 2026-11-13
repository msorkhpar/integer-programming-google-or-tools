A rail depot plans its maintenance jobs for the coming years, and the depot managers send manual
overrides before every solve. Each override is a tuple: `("lock", job, year)` (the job starts in
`year`) or `("ban", job)` (the job is not done). Each `Job` has the years it may start in, the crew
that does it, and optionally a job it must follow, with a lag: it may start no earlier than `lag`
years after that job starts.

The planning model has rules the overrides can contradict:

- A job starts only in one of its own `years`.
- A crew can start at most one job per year.
- A job that follows another starts at least `lag` years after it.

Write `conflicts(jobs, overrides)` in `review.py`. It returns the set of job ids that take part in a
conflict between the overrides and these rules, read from the overrides alone:

- a job locked into a year that is not one of its `years`;
- a job that is both locked and banned;
- two or more jobs of one crew locked into the same year (all of them are reported);
- a job locked into a year less than `lag` years after the year its predecessor is locked into (the
  follower is reported).

`jobs` maps each id to a `Job`. A job appears in at most one lock. List the cases on a sheet first,
with the test instance's jobs, and decide which comparisons each needs. About fifteen lines.
