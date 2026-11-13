A grid operator's maintenance-scheduling MILP has an objective in $k (thousands of dollars). Its
planners send each run's stopping request as a small dict, in their own units:

- `"matters_dollars"`: the smallest amount of objective, in **dollars**, they care about, or `None`;
- `"share_percent"`: a share of the objective, in **percent**, that is also good enough, or `None`;
- `"minutes"`: how long they can wait, as a number of minutes (it may be fractional), or `None`;
- `"nodes"`: a node budget, or `None`. A request with a node budget must give the same answer on
  every run.

Write `limits_for(request)` in `limits.py`, returning a `mathopt.SolveParameters` with:

- `absolute_gap_tolerance`: `matters_dollars` converted to $k, or left unset (`None`) when it is
  `None`;
- `relative_gap_tolerance`: `share_percent` as a fraction (0.5 percent is `0.005`), or `0.0` when it
  is `None`, so that no solver's default tolerance ever decides;
- `node_limit`: `nodes` when it is given;
- `time_limit`: a `datetime.timedelta` of `minutes` when it is given, **except** when `nodes` is
  given: a repeatable run must not stop on the clock, so it gets no time limit.

Leave every other field of `SolveParameters` at its default.
